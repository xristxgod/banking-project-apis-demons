import os
import asyncpg


class TokenDB:
    """An impromptu database for adding and receiving files"""
    @staticmethod
    async def get_token(symbol: str) -> str:
        connection: asyncpg.Connection = await asyncpg.connect(os.getenv('DataBaseURL'))
        row = await connection.fetchrow(
            """SELECT address FROM contract WHERE type='bsc' AND symbol=$1""", symbol.upper()
        )
        await connection.close()
        return row[0]
        # return '0xBBc709564f70Fba250860f06E8b059eA54EEBa7A'

    @staticmethod
    async def get_tokens():
        connection: asyncpg.Connection = await asyncpg.connect(os.getenv('DataBaseURL'))
        data = await connection.fetch("""SELECT * FROM contract WHERE type='bsc'""")
        await connection.close()
        return data
