from __future__ import annotations

import asyncio
import decimal
from typing import NoReturn, Optional

from tronpy.async_tron import AsyncTransaction, PrivateKey

from core.crypto import node
from apps.transaction_v2 import schemas

lock = asyncio.Lock()


class BaseTransaction:

    class TransactionNotSign(Exception):
        pass

    def __init__(self, obj: AsyncTransaction, expected_commission: dict, type: schemas.TransactionType, **kwargs):
        self.obj = obj
        self.type = type

        self._expected_commission = expected_commission
        self._commission: Optional[dict] = None

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._is_signed = False

        self._raw_transaction: Optional[dict] = None
        self._transaction_info: Optional[dict] = None

    @property
    def id(self) -> str:
        return self.obj.txid

    @property
    def expected_commission_schema(self) -> schemas.ResponseCommission:
        return schemas.ResponseCommission(**self._expected_commission)

    @property
    def commission_schema(self) -> schemas.ResponseCommission:
        return schemas.ResponseCommission(**self._commission)

    @property
    def to_schema(self) -> schemas.ResponseCreateTransaction:
        return schemas.ResponseCreateTransaction(
            id=self.id,
            fee=self.expected_commission_schema,
        )

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

    @classmethod
    async def create(cls, body: schemas.BaseCreateTransactionSchema) -> BaseTransaction:
        raise NotImplementedError()


class NativeTransfer(BaseTransaction):

    async def _make_response(self) -> schemas.ResponseSendTransfer:
        self._commission = dict(
            fee=decimal.Decimal(self._transaction_info.get('fee', 0)),
            bandwidth=self._transaction_info.get('receipt', {}).get('net_usage', 0),
            energy=0,
        )

        return schemas.ResponseSendTransfer(
            id=self.id,
            timestamp=self._raw_transaction['raw_data']['timestamp'],
            commission=self.commission_schema,
            amount=getattr(self, 'amount'),
            from_address=getattr(self, 'from_address'),
            to_address=getattr(self, 'to_address'),
            currency=getattr(self, 'currency'),
            type=self.type,
        )

    @classmethod
    async def create(cls, body: schemas.BodyCreateTransfer) -> BaseTransaction:
        obj = await node.client.trx.transfer(
            body.from_address,
            body.to_address,
            body.amount_sun,
        ).fee_limit(
            body.fee_limit,
        ).build()

        return cls(
            obj,
            expected_commission=await node.calculator.calculate(
                raw_data=getattr(obj, '_raw_data'),
            ),
            type=body.transaction_type,
            from_address=body.from_address,
            to_address=body.to_address,
            currency=body.currency,
        )
