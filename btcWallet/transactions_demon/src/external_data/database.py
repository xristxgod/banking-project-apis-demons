import psycopg2
from config import DB_URL


class DB:
    """ Class for receiving data for processing """

    def get_addresses(self):
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()
        sql = """SELECT wallet FROM btc_wallet"""
        cursor.execute(sql)
        data = [x[0] for x in cursor.fetchall()]
        connection.close()
        return data

    @staticmethod
    def get_transaction_by_hash(transaction_hash: str):
        connection = None
        try:
            connection = psycopg2.connect(DB_URL)
            cursor = connection.cursor()
            cursor.execute(
                f"""SELECT * 
                    FROM btc_transaction 
                    WHERE status=0 and transaction_id='{transaction_hash}';"""
            )
            return cursor.fetchone()
        except Exception as error:
            raise error
        finally:
            if connection is not None:
                connection.close()

    @staticmethod
    def get_all_transactions_hash():
        connection = None
        try:
            connection = psycopg2.connect(DB_URL)
            cursor = connection.cursor()
            cursor.execute(
                """SELECT transaction_id 
                   FROM btc_transaction 
                   WHERE status=0;"""
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as error:
            raise error
        finally:
            if connection is not None:
                connection.close()
