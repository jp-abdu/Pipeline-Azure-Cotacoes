import os
import urllib3
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from datetime import datetime
from dotenv import load_dotenv

# Suprimir warnings SSL para desenvolvimento local
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class CosmosHandler:
    def __init__(self):
        # Configurações do CosmosDB Emulator
        self.endpoint = os.getenv("COSMOS_ENDPOINT")
        self.key = os.getenv("COSMOS_KEY")
        self.database_name = os.getenv("COSMOS_DATABASE_NAME")
        self.container_name = os.getenv("COSMOS_CONTAINER_NAME")
        
        # Cliente CosmosDB
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = None
        self.container = None
        
        self.setup_database()

    def setup_database(self):
        """Configura o banco de dados e container"""
        try:
            # Criar ou obter database
            try:
                self.database = self.client.create_database(
                    id=self.database_name,
                    offer_throughput=400
                )
                print(f"[INFO] Database '{self.database_name}' criado.")
            except exceptions.CosmosResourceExistsError:
                self.database = self.client.get_database_client(self.database_name)
                print(f"[INFO] Database '{self.database_name}' já existe.")

            # Criar ou obter container
            try:
                self.container = self.database.create_container(
                    id=self.container_name,
                    partition_key=PartitionKey(path="/symbol"),
                    offer_throughput=400
                )
                print(f"[INFO] Container '{self.container_name}' criado.")
            except exceptions.CosmosResourceExistsError:
                self.container = self.database.get_container_client(self.container_name)
                print(f"[INFO] Container '{self.container_name}' já existe.")

        except Exception as e:
            print(f"[FATAL] Erro ao configurar CosmosDB: {e}")
            raise

    def save_stock_data(self, stock_data):
        """Salva dados de ação no CosmosDB"""
        try:
            # Converter date para string ISO format
            if isinstance(stock_data['date'], datetime):
                date_str = stock_data['date'].isoformat()
            else:
                date_str = stock_data['date'].isoformat() if hasattr(stock_data['date'], 'isoformat') else str(stock_data['date'])
            
            # Criar documento para CosmosDB
            document = {
                'id': f"{stock_data['symbol']}_{date_str}",  # ID único
                'symbol': stock_data['symbol'],
                'date': date_str,
                'opening_price': stock_data['opening_price'],
                'minimum_price': stock_data['minimum_price'],
                'maximum_price': stock_data['maximum_price'],
                'average_price': stock_data['average_price'],
                'last_price': stock_data['last_price'],
                'volume': stock_data['volume'],
                'trades_quantity': stock_data['trades_quantity'],
                'created_at': datetime.utcnow().isoformat()
            }

            # Upsert (inserir ou atualizar) o documento
            self.container.upsert_item(body=document)
            
        except Exception as e:
            print(f"[ERROR] Erro ao salvar dados no CosmosDB para o papel {stock_data.get('symbol')}: {e}")
            raise

    def get_stock_data(self, symbol=None, date=None):
        """Recupera dados de ações do CosmosDB"""
        try:
            query = "SELECT * FROM c"
            parameters = []
            
            if symbol and date:
                query += " WHERE c.symbol = @symbol AND c.date = @date"
                parameters = [
                    {"name": "@symbol", "value": symbol},
                    {"name": "@date", "value": date.isoformat() if hasattr(date, 'isoformat') else str(date)}
                ]
            elif symbol:
                query += " WHERE c.symbol = @symbol"
                parameters = [{"name": "@symbol", "value": symbol}]
            elif date:
                query += " WHERE c.date = @date"
                parameters = [{"name": "@date", "value": date.isoformat() if hasattr(date, 'isoformat') else str(date)}]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return items
            
        except Exception as e:
            print(f"[ERROR] Erro ao buscar dados no CosmosDB: {e}")
            return []