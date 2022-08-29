from typing import Optional, List

import asyncpg
from tronpy.tron import TAddress

from .elastic import ElasticController
from config import Config


class Database:
    @staticmethod
    async def get(sql: str) -> List:
        connection: Optional[asyncpg.Connection] = None
        try:
            connection = await asyncpg.connect(Config.DATABASE_URL)
            result: List[asyncpg.Record] = await connection.fetch(sql)
            return [x for x in result]
        except Exception as ex:
            await ElasticController.send_exception(
                ex=ex,
                message=f"Bad connect to database: {Config.DATABASE_URL}"
            )
            return []
        finally:
            if connection is not None:
                await connection.close()


class DatabaseController:
    @staticmethod
    async def get_private_key(address: TAddress) -> str:
        pass


__all__ = [
    "Database", "DatabaseController"
]
