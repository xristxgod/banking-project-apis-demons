import psycopg2
import asyncpg
from dotenv import load_dotenv
from config import DB_URL


load_dotenv()


class DB:
    """Class for receiving data for processing"""
    @staticmethod
    async def get_addresses():
        connection: asyncpg.Connection = await asyncpg.connect(DB_URL)
        data = [int(x[0], 0) for x in await connection.fetch("""SELECT wallet FROM bnb_wallet""")]
        await connection.close()
        return data
        # return [int(x, 0) for x in [
        #     '0xeC25655F2E03E3d88E376b1f10292752C4cb551A',
        #     '0xdbFFDd67016E85dDf5acA9f6649a61c8C4C0F177'
        # ]]

    @staticmethod
    def get_tokens():
        connection = psycopg2.connect(DB_URL)
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM contract WHERE type='bsc'""")
        data = cursor.fetchall()
        connection.close()
        return data
        # return [(1, 'Tether USD', 'USDT', '0xBBc709564f70Fba250860f06E8b059eA54EEBa7A', 18, 'bsc', 'bsc_erc20_usdt')]

    @staticmethod
    async def get_transaction_by_hash(transaction_hash: str):
        connection: asyncpg.Connection = await asyncpg.connect(DB_URL)
        data = await connection.fetchrow(
            f"""SELECT * 
                FROM bnb_transaction 
                WHERE status=0 and transaction_id='{transaction_hash}';"""
        )
        await connection.close()
        return data

    @staticmethod
    async def get_all_transactions_hash():
        connection: asyncpg.Connection = await asyncpg.connect(DB_URL)
        data = [row[0] for row in await connection.fetch(
            """SELECT transaction_id 
               FROM bnb_transaction 
               WHERE status=0;"""
        )]
        await connection.close()
        return data
