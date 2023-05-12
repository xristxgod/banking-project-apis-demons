from __future__ import annotations

import enum
import asyncio

from apps.transaction_v2 import schemas
from apps.transaction_v2 import services

lock = asyncio.Lock()


class TransactionStorage:

    objs: dict[schemas.TransactionType, services.BaseTransaction] = {

    }

    class Method(enum.Enum):
        TRANSFER = 'transfer'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            setattr(cls, 'instance', super().__new__(cls, *args, **kwargs))
        return getattr(cls, 'instance')

    def __init__(self):
        self.transactions: dict[str, services.BaseTransaction] = {}

    async def clear_buffer(self):
        async with lock:
            for key, transaction in self.transactions.items():
                if not transaction.is_expired:
                    del self.transactions[key]

    async def create(self, body: schemas.BaseCreateTransactionSchema,
                     save: bool = True) -> services.BaseTransaction:
        obj = self.objs[body.transaction_type]
        transaction = await obj.create(body)
        if save:
            async with lock:
                self.transactions.update({
                    transaction.id: transaction
                })
        return transaction

    async def get(self, transaction_id: str):
        pass
