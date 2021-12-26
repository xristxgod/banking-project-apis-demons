from typing import List

import psycopg2
import psycopg2.errorcodes

from transactions_demon.config import DataBaseUrl
from transactions_demon.src.tron_typing import TronAccountAddress

def get_addresses() -> List[TronAccountAddress]:
    """Get all addresses into table"""
    __connection = None
    try:
        __connection = psycopg2.connect(DataBaseUrl)
        __cursor = __connection.cursor()
        __cursor.execute("""SELECT wallet FROM tron_wallet""")
        return [address[0] for address in __cursor.fetchall()]
    except Exception as error:
        raise error
    finally:
        if __connection is not None:
            __connection.close()
