import azure.functions as func
import logging
import mysql.connector
import os
from lxml import etree
from datetime import datetime
from decimal import Decimal

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="dados-pregao-bolsa",
                  connection="AZURESTORAGE_CONNECTION_STRING")
def load_file_b3_trigger(myblob: func.InputStream):
    logging.info(f"Iniciando processamento do arquivo: {myblob.name}")
    logging.info(f"Tamanho do arquivo: {myblob.length} bytes")

    try:
        # 1. Ler conteúdo do arquivo XML
        xml_content = myblob.read()
        logging.info("Arquivo lido com sucesso")

        # 2. Parsear dados do XML
        assets = parse_b3_xml(xml_content)
        logging.info(f"Total de ativos extraídos: {len(assets)}")

        # 3. Carregar no banco de dados
        if assets:
            records_inserted = load_to_database(assets)
            logging.info(f"Carga concluída: {records_inserted} registros processados")
        else:
            logging.warning("Nenhum ativo encontrado no arquivo")

    except Exception as e:
        logging.error(f"Erro ao processar arquivo {myblob.name}: {str(e)}")
        raise


def parse_b3_xml(xml_content):
    """
    Faz o parse do arquivo XML da B3 e extrai os dados de cotações.
    Baseado no layout dos arquivos de boletim diário da B3.
    """
    assets = []

    try:
        # Parse do XML
        root = etree.fromstring(xml_content)

        # Namespace do XML da B3 (se houver)
        namespaces = root.nsmap

        # Buscar elementos de cotações
        # O XML da B3 geralmente tem estrutura: BizGrpList -> Msg -> TradgSsnData -> SctyList -> Scty
        for scty in root.findall('.//Scty', namespaces):
            try:
                # Extrair dados do ativo
                asset = extract_asset_data(scty, namespaces)
                if asset:
                    assets.append(asset)
            except Exception as e:
                logging.warning(f"Erro ao processar ativo: {str(e)}")
                continue

    except Exception as e:
        logging.error(f"Erro ao fazer parse do XML: {str(e)}")
        # Fallback: tentar parse sem namespace
        try:
            assets = parse_b3_xml_fallback(xml_content)
        except:
            raise

    return assets


def extract_asset_data(scty_element, namespaces):
    """
    Extrai os dados de um ativo individual do elemento XML.
    """
    try:
        # Código do ativo
        ticker = scty_element.findtext('.//TckrSymb', namespaces=namespaces)
        if not ticker:
            return None

        # Data do pregão
        trade_date_str = scty_element.findtext('.//TradDt', namespaces=namespaces)
        if trade_date_str:
            trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d').date()
        else:
            trade_date = datetime.now().date()

        # Preços
        opening_price = scty_element.findtext('.//OpngPric', namespaces=namespaces)
        closing_price = scty_element.findtext('.//ClsgPric', namespaces=namespaces)
        avg_price = scty_element.findtext('.//AvrgPric', namespaces=namespaces)

        # Volume
        volume = scty_element.findtext('.//TtlTradgVol', namespaces=namespaces)

        asset = {
            'nome': ticker,
            'dataPregao': trade_date,
            'precoAbertura': Decimal(opening_price) if opening_price else None,
            'precoFechamento': Decimal(closing_price) if closing_price else None,
            'precoMedio': Decimal(avg_price) if avg_price else None,
            'volumeDiario': Decimal(volume) if volume else None
        }

        return asset

    except Exception as e:
        logging.warning(f"Erro ao extrair dados do ativo: {str(e)}")
        return None


def parse_b3_xml_fallback(xml_content):
    """
    Parse alternativo caso o XML tenha estrutura diferente.
    """
    assets = []
    logging.info("Usando parser alternativo para XML")

    # Adicione aqui lógica alternativa se necessário
    # Por exemplo, se o XML tiver estrutura simplificada

    return assets


def load_to_database(assets):
    """
    Carrega os dados dos ativos no banco de dados MySQL.
    Usa INSERT ... ON DUPLICATE KEY UPDATE para evitar duplicatas.
    """
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

        records_processed = 0
        for asset in assets:
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

        # Commit das transações
        conn.commit()
        logging.info(f"Commit realizado: {records_processed} registros")

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
