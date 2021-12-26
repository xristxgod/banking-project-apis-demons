import os
import psycopg2


class DB:
    """ Class for receiving data for processing """

    def __init__(self):
        """ Connect to database """
        try:
            self._connection = psycopg2.connect(os.getenv("DataBaseURL"))
        except Exception as e:
            raise RuntimeError("Error: Step 26 {}".format(e))
        self._cursor = self._connection.cursor()

    def get_addresses(self):
        sql = """SELECT wallet FROM btc_wallet"""
        self._cursor.execute(sql)
        return [x[0] for x in self._cursor.fetchall()]

    def close_connection(self):
        self._connection.close()
