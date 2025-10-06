import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

class PostgresHandler:
    def __init__(self):
        load_dotenv()  # Carrega as variáveis do arquivo .env
        
        self.conn = psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            database=os.getenv("PG_DATABASE", "stocks_db"),
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASSWORD"),  # Agora vai pegar a senha do .env
        )
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(12),
                    date DATE,
                    opening_price DECIMAL(10,2),
                    minimum_price DECIMAL(10,2),
                    maximum_price DECIMAL(10,2),
                    average_price DECIMAL(10,2),
                    last_price DECIMAL(10,2),
                    volume DECIMAL(15,2),
                    trades_quantity INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                );
            """)
            self.conn.commit()

    def save_stock_data(self, stock_data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO stocks (
                    symbol, date, opening_price, minimum_price, 
                    maximum_price, average_price, last_price, 
                    volume, trades_quantity
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, date) 
                DO UPDATE SET
                    opening_price = EXCLUDED.opening_price,
                    minimum_price = EXCLUDED.minimum_price,
                    maximum_price = EXCLUDED.maximum_price,
                    average_price = EXCLUDED.average_price,
                    last_price = EXCLUDED.last_price,
                    volume = EXCLUDED.volume,
                    trades_quantity = EXCLUDED.trades_quantity;
            """, (
                stock_data['symbol'],
                stock_data['date'],
                stock_data['opening_price'],
                stock_data['minimum_price'],
                stock_data['maximum_price'],
                stock_data['average_price'],
                stock_data['last_price'],
                stock_data['volume'],
                stock_data['trades_quantity']
            ))
            self.conn.commit()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()