from typing import Union, List

from asyncpg import connect

from src.utils.types import TronAccountPrivateKey, TronAccountAddress
from src.utils.es_send import send_exception_to_kibana
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
        logger.error(f"Error: get private key: {error}")
        await send_exception_to_kibana(error=error, msg="ERROR: GET PRIVATE KEY FROM DB")
    return None

async def get_wallets() -> Union[List[TronAccountAddress], None]:
    try:
        connection = await connect(DB_URL)
        row = await connection.fetch(
            'SELECT wallet FROM tron_wallet',
        )
        await connection.close()
        return [x[0] for x in row]
    except Exception as error:
        logger.error(f'Error: get addresses: {error}')
        await send_exception_to_kibana(error=error, msg="ERROR: GET WALLETS FROM DB")
        return None