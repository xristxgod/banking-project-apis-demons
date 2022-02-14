from typing import List, Dict

import psycopg2
import psycopg2.extras
import psycopg2.errorcodes

from src.utils import TronAccountAddress
from config import DataBaseUrl

def get_addresses() -> List[TronAccountAddress]:
    """Get all addresses into table"""
    __connection = None
    try:
        __connection = psycopg2.connect(DataBaseUrl)
        __cursor = __connection.cursor()
        __cursor.execute("""SELECT wallet FROM tron_wallet;""")
        return [address[0] for address in __cursor.fetchall()]
    except Exception as error:
        raise error
    finally:
        if __connection is not None:
            __connection.close()

def get_contracts() -> Dict:
    """Get information from a file"""
    __connection = None
    try:
        __connection = psycopg2.connect(DataBaseUrl)
        __cursor = __connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        __cursor.execute("""SELECT * FROM contract WHERE type='tron';""")
        return __cursor.fetchall()
    except Exception as error:
        raise error
    finally:
        if __connection is not None:
            __connection.close()

def get_transaction_hash(transaction_hash: str) -> Dict:
    __connection = None
    try:
        __connection = psycopg2.connect(DataBaseUrl)
        __cursor = __connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        __cursor.execute(f"""SELECT * from tron_transaction WHERE status=0 and transaction_id='{transaction_hash}';""")
        return __cursor.fetchone()
    except Exception as error:
        raise error
    finally:
        if __connection is not None:
            __connection.close()

def get_all_transactions_hash() -> List:
    __connection = None
    try:
        __connection = psycopg2.connect(DataBaseUrl)
        __cursor = __connection.cursor()
        __cursor.execute("""SELECT transaction_id from tron_transaction WHERE status=0""")
        return [address[0] for address in __cursor.fetchall()]
    except Exception as error:
        raise error
    finally:
        if __connection is not None:
            __connection.close()