from typing import List, Dict

import asyncpg
import psycopg2
import psycopg2.extras
import psycopg2.errorcodes

from config import DataBaseUrl


async def get_addresses() -> List:
    """Get all addresses into table"""
    connection: asyncpg.Connection = await asyncpg.connect(DataBaseUrl)
    data = [address[0] for address in await connection.fetch("""SELECT wallet FROM tron_wallet""")]
    await connection.close()
    return data


async def get_all_transactions_hash() -> List:
    """Get all transactions not processed."""
    connection: asyncpg.Connection = await asyncpg.connect(DataBaseUrl)
    data = [address[0] for address in await connection.fetch("""SELECT transaction_id from tron_transaction WHERE status=0""")]
    await connection.close()
    return data


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
    """Get a hash transaction."""
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
