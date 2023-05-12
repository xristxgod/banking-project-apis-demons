from __future__ import annotations

import enum
import asyncio
from typing import NoReturn, Optional

from tronpy.async_tron import AsyncTransaction, PrivateKey

from apps.transaction_v2 import schemas

lock = asyncio.Lock()


class BaseTransaction:

    class TransactionNotSign(Exception):
        pass

    def __init__(self, obj: AsyncTransaction, **kwargs):
        self.obj = obj

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._is_signed = False
        self._fee: Optional[schemas.ResponseCommission] = None

        self._raw_transaction: Optional[dict] = None
        self._transaction_info: Optional[dict] = None

    @property
    def id(self) -> str:
        return self.obj.txid

    @property
    def fee(self) -> schemas.ResponseCommission:
        return self._fee

    @fee.setter
    def fee(self, new_fee: schemas.ResponseCommission):
        self._fee = new_fee

    @property
    def is_expired(self) -> bool:
        return self.obj.is_expired

    async def sign(self, private_key: PrivateKey) -> NoReturn:
        self.obj.sign(private_key)
        self._is_signed = True

    async def send(self) -> schemas.BaseResponseSendTransactionSchema:
        async with lock:
            if not self._is_signed:
                raise self.TransactionNotSign()
            if not self.obj.is_expired:
                await self.obj.update()

            self._raw_transaction = await self.obj.broadcast()
            self._transaction_info = await self._raw_transaction.wait()
        return await self._make_response()

    async def _make_response(self) -> schemas.BaseResponseSendTransactionSchema:
        raise NotImplementedError()

    async def to_schemas(self) -> schemas.ResponseCreateTransaction:
        return schemas.ResponseCreateTransaction(
            id=self.id,
            fee=self.fee,
        )

    @classmethod
    async def create(cls, body: schemas.BaseCreateTransactionSchema) -> BaseTransaction:
        raise NotImplementedError()
