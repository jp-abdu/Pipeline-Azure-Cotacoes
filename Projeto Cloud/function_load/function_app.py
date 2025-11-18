import azure.functions as func
import logging
import os
import re
from lxml import etree
from datetime import datetime
from decimal import Decimal
import mysql.connector

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="dados-pregao-bolsa/{name}",
                  connection="AzureWebJobsStorage")
def load_file_b3_trigger(myblob: func.InputStream):
    """
    Função que é acionada quando um novo arquivo XML é carregado no blob storage.
    Processa o XML da B3, extrai os dados de cotações e carrega no banco de dados MySQL.
    """
    logging.info(f"Processando blob: {myblob.name}")
    logging.info(f"Tamanho do blob: {myblob.length} bytes")

    try:
        # Ler o conteúdo do blob
        xml_content = myblob.read()
        logging.info(f"XML lido com sucesso. Tamanho: {len(xml_content)} bytes")

        # Fazer parse do XML e extrair os dados
        logging.info("Iniciando parse do XML...")
        assets = parse_b3_xml(xml_content)

        if not assets:
            logging.warning("Nenhum ativo encontrado no XML")
            return

        logging.info(f"Total de {len(assets)} ativos extraídos do XML")

        # Carregar dados no banco de dados
        logging.info("Iniciando carregamento no banco de dados...")
        records_loaded = load_to_database(assets)

        logging.info(f"Processamento concluído. {records_loaded} registros carregados no banco de dados")

    except Exception as e:
        logging.error(f"Erro ao processar arquivo: {str(e)}")
        raise


def parse_b3_xml(xml_content):
    """
    Faz o parse do arquivo XML da B3 e extrai os dados de cotações.
    Baseado no layout BVMF.217.01 dos arquivos de boletim diário da B3.
    Usa iterparse para processar XML grande de forma eficiente.
    """
    assets = []

    try:
        # Usar iterparse para processar XML de forma eficiente sem carregar tudo na memória
        from io import BytesIO

        context = etree.iterparse(
            BytesIO(xml_content),
            events=('end',),
            tag='{urn:bvmf.217.01.xsd}PricRpt'
        )

        count = 0
        for event, pric_rpt in context:
            try:
                # Extrair dados do ativo
                asset = extract_asset_data_b3(pric_rpt)
                if asset:
                    assets.append(asset)
                    count += 1

                    # Log a cada 1000 ativos para monitorar progresso
                    if count % 1000 == 0:
                        logging.info(f"Processados {count} ativos...")

                # Limpar o elemento da memória após processar
                pric_rpt.clear()
                while pric_rpt.getprevious() is not None:
                    del pric_rpt.getparent()[0]

            except Exception as e:
                logging.warning(f"Erro ao processar PricRpt: {str(e)}")
                continue

        # Limpar contexto
        del context

        logging.info(f"Total de ativos extraídos: {len(assets)}")

    except Exception as e:
        logging.error(f"Erro ao fazer parse do XML: {str(e)}")
        raise

    return assets


def extract_asset_data_b3(pric_rpt_element):
    """
    Extrai os dados de um ativo individual do elemento PricRpt.
    Layout BVMF.217.01 da B3.
    Filtra apenas ativos que atendem aos seguintes padrões:
    - 4 letras + 1 número (terminando em 3, 4, 5 ou 6)
    - 4 letras + 2 números (terminando em 11 ou 34)
    """
    try:
        # Namespace do XML da B3
        ns = '{urn:bvmf.217.01.xsd}'

        # Código do ativo (TckrSymb)
        ticker_elem = pric_rpt_element.find(f'.//{ns}TckrSymb')
        if ticker_elem is None or not ticker_elem.text:
            return None
        ticker = ticker_elem.text.strip()

        # Filtrar usando regex:
        # - ^[A-Z]{4}[3-6]$ : 4 letras maiúsculas seguidas de um número (3, 4, 5 ou 6)
        # - ^[A-Z]{4}(11|34)$ : 4 letras maiúsculas seguidas de 11 ou 34
        pattern = r'^[A-Z]{4}([3-6]|11|34)$'
        if not re.match(pattern, ticker):
            return None

        # Data do pregão
        trade_date_elem = pric_rpt_element.find(f'.//{ns}Dt')
        if trade_date_elem is not None and trade_date_elem.text:
            try:
                trade_date = datetime.strptime(trade_date_elem.text, '%Y-%m-%d').date()
            except:
                trade_date = datetime.now().date()
        else:
            trade_date = datetime.now().date()

        # Buscar atributos financeiros
        fin_attrs = pric_rpt_element.find(f'.//{ns}FinInstrmAttrbts')

        if fin_attrs is None:
            logging.warning(f"FinInstrmAttrbts não encontrado para {ticker}")
            return None

        # Preço de abertura (FrstPric)
        opening_price_elem = fin_attrs.find(f'.//{ns}FrstPric')
        opening_price = Decimal(opening_price_elem.text) if opening_price_elem is not None and opening_price_elem.text else None

        # Preço de fechamento (LastPric)
        closing_price_elem = fin_attrs.find(f'.//{ns}LastPric')
        closing_price = Decimal(closing_price_elem.text) if closing_price_elem is not None and closing_price_elem.text else None

        # Preço médio (TradAvrgPric)
        avg_price_elem = fin_attrs.find(f'.//{ns}TradAvrgPric')
        avg_price = Decimal(avg_price_elem.text) if avg_price_elem is not None and avg_price_elem.text else None

        # Quantidade de negócios (RglrTxsQty) - usar como proxy para volume
        qty_elem = fin_attrs.find(f'.//{ns}RglrTxsQty')
        volume = Decimal(qty_elem.text) if qty_elem is not None and qty_elem.text else None

        # Se não temos preço de fechamento, não adicionar o ativo
        if closing_price is None:
            return None

        asset = {
            'nome': ticker,
            'dataPregao': trade_date,
            'precoAbertura': opening_price,
            'precoFechamento': closing_price,
            'precoMedio': avg_price,
            'volumeDiario': volume
        }

        return asset

    except Exception as e:
        logging.warning(f"Erro ao extrair dados do PricRpt: {str(e)}")
        return None


def load_to_database(assets):
    """
    Carrega os dados dos ativos no banco de dados MySQL.
    Usa INSERT ... ON DUPLICATE KEY UPDATE para evitar duplicatas.
    Processa em lotes para otimizar memória e performance.
    """
    if not assets:
        logging.warning("Nenhum ativo para carregar")
        return 0

    try:
        # Conectar ao banco de dados
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", "3306"))
        )

        cursor = conn.cursor()
        logging.info("Conexão com banco de dados estabelecida")

        # Query de inserção com update em caso de duplicata
        query = """
        INSERT INTO asset (nome, dataPregao, precoAbertura, precoFechamento,
                          volumeDiario, precoMedio)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            precoAbertura = VALUES(precoAbertura),
            precoFechamento = VALUES(precoFechamento),
            volumeDiario = VALUES(volumeDiario),
            precoMedio = VALUES(precoMedio)
        """

        # Processar em lotes de 500
        BATCH_SIZE = 500
        records_processed = 0

        for i in range(0, len(assets), BATCH_SIZE):
            batch = assets[i:i + BATCH_SIZE]

            for asset in batch:
                try:
                    cursor.execute(query, (
                        asset['nome'],
                        asset['dataPregao'],
                        asset['precoAbertura'],
                        asset['precoFechamento'],
                        asset['volumeDiario'],
                        asset['precoMedio']
                    ))
                    records_processed += 1
                except Exception as e:
                    logging.warning(f"Erro ao inserir ativo {asset['nome']}: {str(e)}")
                    continue

            # Commit do lote
            conn.commit()
            logging.info(f"Lote processado: {records_processed}/{len(assets)} ativos")

        logging.info(f"Total de {records_processed} registros carregados no banco")

        # Fechar conexão
        cursor.close()
        conn.close()

        return records_processed

    except mysql.connector.Error as e:
        logging.error(f"Erro de conexão com banco de dados: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Erro ao carregar dados no banco: {str(e)}")
        raise
