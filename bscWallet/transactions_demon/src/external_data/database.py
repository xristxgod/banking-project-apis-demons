import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DB:
    """Class for receiving data for processing"""
    @staticmethod
    def get_addresses():
        connection = psycopg2.connect(os.getenv('DataBaseURL'))
        cursor = connection.cursor()
        cursor.execute("""SELECT wallet FROM bnb_wallet""")
        data = [int(x[0], 0) for x in cursor.fetchall()]
        connection.close()
        return data
        # return [int(x, 0) for x in [
        #     '0xeC25655F2E03E3d88E376b1f10292752C4cb551A',
        #     '0xdbFFDd67016E85dDf5acA9f6649a61c8C4C0F177'
        # ]]

    @staticmethod
    def get_tokens():
        connection = psycopg2.connect(os.getenv('DataBaseURL'))
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM contract WHERE type='bsc'""")
        data = cursor.fetchall()
        connection.close()
        return data
        # return [(1, 'Tether USD', 'USDT', '0xBBc709564f70Fba250860f06E8b059eA54EEBa7A', 18, 'bsc', 'bsc_erc20_usdt')]
