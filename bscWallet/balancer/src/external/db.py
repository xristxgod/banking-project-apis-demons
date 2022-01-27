from asyncpg import connect, Connection

from config import DB_URL, logger


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
            logger.error(f'ERROR GET PK: {e}')
        # return '16e55515317cb556e19b674f3e053d5528960a7920155518623467a8188b0d65'
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
            logger.error(f'ERROR GET ADDRESSES: {e}')
        return None

