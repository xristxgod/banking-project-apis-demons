from typing import Union, List

from asyncpg import connect
from src.utils.types import TronAccountPrivateKey, TronAccountAddress
from config import DB_URL, logger

async def get_private_key(address: TronAccountAddress) -> Union[TronAccountPrivateKey, None]:
    try:
        connection = await connect(DB_URL)
        row = await connection.fetchrow(
            "SELECT private_key FROM tron_wallet WHERE wallet = $1",
            address
        )
        await connection.close()
        return row[0]
    except Exception as error:
        logger.error(f"Error get private key: {error}")
    return None

async def get_wallets() -> Union[List[TronAccountAddress], None]:
    try:
        connection = await connect(DB_URL)
        row = await connection.fetch(
            'SELECT wallet FROM tron_wallet',
        )
        await connection.close()
        return [x[0] for x in row]
    except Exception as e:
        logger.error(f'ERROR GET ADDRESSES: {e}')
        return None