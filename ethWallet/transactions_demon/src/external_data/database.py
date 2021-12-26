import os
import psycopg2
import psycopg2.errorcodes
from dotenv import load_dotenv

load_dotenv()


class DB:
    """Class for receiving data for processing"""
    def __init__(self):
        """Connect to database"""
        try:
            self.__connection = psycopg2.connect(os.getenv('DataBaseURL'))
        except Exception as error:
            raise RuntimeError("Error: Step 26 {}".format(error))
        self.__cursor = self.__connection.cursor()

    def get_addresses(self):
        self.__cursor.execute("""SELECT wallet FROM eth_wallet""")
        return [int(x, 0) for x in self.__cursor.fetchall()]

    def close_connection(self):
        self.__connection.close()
