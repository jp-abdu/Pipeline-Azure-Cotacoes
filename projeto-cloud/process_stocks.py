from lxml import etree
from datetime import datetime
from db_handler import PostgresHandler
import io

class StockProcessor:
    def __init__(self):
        self.db = PostgresHandler()

    def process_xml_file(self, xml_content_string, fallback_date=None):
        print(f"[INFO] Iniciando processamento (namespace-agnóstico) a partir do conteúdo do blob...")

        try:
            xml_bytes = xml_content_string.encode('utf-8')

            tree = etree.parse(io.BytesIO(xml_bytes))
            root = tree.getroot()

            trade_date = None
            trade_date_node = root.xpath('.//*[local-name()="CreDt"]')
            if trade_date_node:
                trade_date = datetime.strptime(trade_date_node[0].text.split('T')[0], '%Y-%m-%d').date()
            elif fallback_date:
                trade_date = fallback_date
                print(f"[WARN] Tag <CreDt> não encontrada. Usando data de fallback: {trade_date}")
            else:
                print("[FATAL] Não foi possível determinar a data do pregão.")
                return

            papers = root.xpath('.//*[local-name()="PricRpt"]')
            print(f"[INFO] Encontrados {len(papers)} relatórios de preço (<PricRpt>) no arquivo.")

            processed_count = 0
            for paper in papers:
                symbol_node = paper.xpath('.//*[local-name()="TckrSymb"]')
                attrs_node = paper.xpath('.//*[local-name()="FinInstrmAttrbts"]')

                if not symbol_node or not attrs_node:
                    continue

                symbol = symbol_node[0].text.rstrip('TF')

                if not self._is_spot_market(symbol):
                    continue

                attrs = attrs_node[0]

                try:
                    stock_data = {
                        'symbol': symbol,
                        'date': trade_date,
                        'opening_price': self._get_price(attrs, 'FrstPric'),
                        'minimum_price': self._get_price(attrs, 'MinPric'),
                        'maximum_price': self._get_price(attrs, 'MaxPric'),
                        'average_price': self._get_price(attrs, 'TradAvrgPric'),
                        'last_price': self._get_price(attrs, 'LastPric'),
                        'volume': self._get_price(attrs, 'FinVol'),
                        'trades_quantity': int(self._get_price(attrs, 'RglrTxsQty') or 0)
                    }

                    if stock_data['trades_quantity'] > 0:
                        self.db.save_stock_data(stock_data)
                        processed_count += 1
                except Exception as e:
                    print(f"[ERROR] Erro ao processar dados para o papel {symbol}: {str(e)}")

            if processed_count > 0:
                print(f"[SUCCESS] Total de {processed_count} papéis do mercado à vista salvos no banco de dados.")
            else:
                print("[WARN] Nenhum papel com dados de negociação válidos foi encontrado após os filtros.")

        except etree.XMLSyntaxError as e:
            print(f"[FATAL] Erro de sintaxe no XML com lxml: {str(e)}")
        except Exception as e:
            print(f"[FATAL] Erro inesperado no processamento: {str(e)}")

    def _is_spot_market(self, symbol):
        return symbol.endswith(('3', '4', '11'))

    def _get_price(self, element, tag):
        node = element.xpath(f'*[local-name()="{tag}"]')
        if node and node[0].text:
            return float(node[0].text)
        return 0.0