from __future__ import annotations

import copy
import asyncio

from core import meta
from apps.transaction import schemas
from apps.transaction.schemas import TransactionType
from apps.transaction import services

__all__ = (
    'TransactionStorage',
)

lock = asyncio.Lock()


class TransactionStorage(metaclass=meta.Singleton):

    objs: dict[schemas.TransactionType, services.BaseTransaction] = {
        TransactionType.TRANSFER_NATIVE: services.NativeTransfer,
        TransactionType.TRANSFER: services.Transfer,
        TransactionType.APPROVE: services.Approve,
        TransactionType.TRANSFER_FROM: services.TransferFrom,
        TransactionType.FREEZE: services.Freeze,
        TransactionType.UNFREEZE: services.Unfreeze,
        TransactionType.DELEGATE: services.Delegate,
        TransactionType.UN_DELEGATE: services.UnDelegate,
    }

    class TransactionNotFound(Exception):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            setattr(cls, 'instance', super().__new__(cls, *args, **kwargs))
        return getattr(cls, 'instance')

    def __init__(self):
        self.transactions: dict[str, services.BaseTransaction] = {}

    async def clear_buffer(self):
        """
        Clears the buffer of unused transactions every `settings.TRANSACTION_BUFFER_CLEAR_TIME` minutes.
        """
        async with lock:
            for key, transaction in copy.copy(self.transactions).items():
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

    def get(self, transaction_id: str, delete: bool = True) -> services.BaseTransaction:
        if delete:
            obj = self.transactions.pop(transaction_id, None)
        else:
            obj = self.transactions.get(transaction_id)

        if not obj:
            raise self.TransactionNotFound(f'{transaction_id} not found!')

        return obj
