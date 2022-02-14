import psycopg2
from config import DB_URL, decimal, Decimal


class DB:
    """ Class for receiving data for processing """

    @staticmethod
    def get_balance(address: str) -> Decimal:
        try:
            connection = psycopg2.connect(DB_URL)
            cursor = connection.cursor()
            cursor.execute(f"""SELECT id FROM btc_wallet WHERE wallet='{address}'""")
            wallet_id = cursor.fetchone()[0]
            cursor.execute(f"""SELECT balance FROM btc_balance WHERE wallet_id = %s""", (wallet_id, ))
            record = cursor.fetchone()
            if record is None:
                data = decimal.create_decimal('0.0')
            else:
                data = decimal.create_decimal(record[0])
            connection.close()
            return data
        except:
            return None
