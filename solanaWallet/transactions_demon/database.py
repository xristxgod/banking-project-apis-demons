import os
from asyncpg import Connection, connect, Record
from asyncio import create_task
from typing import List, Optional
from config import logger


class DB:
    """ Class for receiving data for processing """
    def __init__(self):
        self.__conn: Optional[Connection] = None

    def __del__(self):
        if self.__conn is not None:
            create_task(self.__conn.close())

    async def start(self):
        try:
            if self.__conn is None:
                self.__conn: Connection = await connect(os.getenv("DataBaseURL"))
            return self.__conn is not None
        except Exception as e:
            logger.error(f'DB ERROR: {e}')
            return None

    async def get_pub_keys(self) -> List[str]:
        try:
            result: List[Record] = await self.__conn.fetch(f"""
                SELECT public_key
                FROM solana_wallet;
            """)
            if len(result) > 0:
                return [x[0] for x in result]
            return None
        except Exception as e:
            logger.error(f'DB ERROR: {e}')
            return None
