import os
import psycopg2
import psycopg2.errorcodes
from dotenv import load_dotenv

load_dotenv()


class DB:
    """Class for receiving data for processing"""
    def get_addresses(self):
        connection = psycopg2.connect(os.getenv('DataBaseURL'))
        cursor = connection.cursor()
        cursor.execute("""SELECT wallet FROM eth_wallet""")
        data = [int(x, 0) for x in cursor.fetchall()]
        connection.close()
        return data
        # return [int(x, 0) for x in [
        #     '0x6fAE511E40F582C50cD487a4999dc857a7bc3527',
        #     '0xeC25655F2E03E3d88E376b1f10292752C4cb551A'
        # ]]
