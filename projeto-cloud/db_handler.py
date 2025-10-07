import psycopg2
import os

class PostgresHandler:
    def __init__(self):
        self.conn_string = os.getenv("POSTGRES_CONN_STRING")
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.conn_string)
        except psycopg2.OperationalError as e:
            print(f"[FATAL] Erro ao conectar ao PostgreSQL: {e}")
            raise

    def save_stock_data(self, stock_data):
        sql = """
            INSERT INTO stock_prices (
                symbol, date, opening_price, minimum_price, maximum_price,
                average_price, last_price, volume, trades_quantity
            ) VALUES (
                %(symbol)s, %(date)s, %(opening_price)s, %(minimum_price)s, %(maximum_price)s,
                %(average_price)s, %(last_price)s, %(volume)s, %(trades_quantity)s
            )
            ON CONFLICT (symbol, date) DO UPDATE SET
                opening_price = EXCLUDED.opening_price,
                minimum_price = EXCLUDED.minimum_price,
                maximum_price = EXCLUDED.maximum_price,
                average_price = EXCLUDED.average_price,
                last_price = EXCLUDED.last_price,
                volume = EXCLUDED.volume,
                trades_quantity = EXCLUDED.trades_quantity;
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, stock_data)
            self.conn.commit()
        except (Exception, psycopg2.Error) as e:
            print(f"[ERROR] Erro na transação com o banco de dados para o papel {stock_data.get('symbol')}: {e}")
            self.conn.rollback()

    def __del__(self):
        if self.conn:
            self.conn.close()