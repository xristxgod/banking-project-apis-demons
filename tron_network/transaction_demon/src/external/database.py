from typing import Optional, List, Dict

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
    async def get_addresses() -> Optional[List[TAddress]]:
        return await Database.get("SELECT wallet FROM tron_wallet")

    @staticmethod
    async def get_transactions_hash() -> Optional[List[str]]:
        return await Database.get("SELECT transaction_id FROM tron_transaction WHERE status=0")

    @staticmethod
    async def get_transaction_hash(transaction_hash: str) -> Dict:
        result = await Database.get(
            f"SELECT * FROM tron_transaction WHERE status=0 AND transaction_id='{transaction_hash}';"
        )
        return result[0]


__all__ = [
    "DatabaseController", "Database"
]
