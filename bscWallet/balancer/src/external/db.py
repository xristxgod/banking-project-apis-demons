from asyncpg import connect, Connection

from config import DB_URL
from src.external.es_send import send_exception_to_kibana


class DB:
    @staticmethod
    async def get_private_key(address: str):
        try:
            conn = await connect(DB_URL)
            row = await conn.fetchrow(
                'SELECT private_key FROM bnb_wallet WHERE wallet = $1',
                address,
            )
            await conn.close()
            return row[0]
        except Exception as e:
            await send_exception_to_kibana(e, 'ERROR GET PRIVATE KEY')
        return None

    @staticmethod
    async def get_wallets():
        try:
            conn: Connection = await connect(DB_URL)
            row = await conn.fetch(
                'SELECT wallet FROM bnb_wallet',
            )
            await conn.close()
            return [x[0] for x in row]
        except Exception as e:
            await send_exception_to_kibana(e, 'ERROR GET ADDRESS')
        return None

