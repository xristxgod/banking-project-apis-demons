import os
import psycopg2


class DB:
    """ Class for receiving data for processing """

    def __init__(self):
        pass

    def get_addresses(self):
        connection = psycopg2.connect(os.getenv("DataBaseURL"))
        cursor = connection.cursor()
        sql = """SELECT wallet FROM btc_wallet"""
        cursor.execute(sql)
        data = [x[0] for x in cursor.fetchall()]
        connection.close()
        return data
