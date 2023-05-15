from __future__ import annotations

import asyncio
import decimal
from typing import NoReturn, Optional

from tronpy.async_tron import AsyncTransaction, PrivateKey

from core.crypto import node
from core.crypto.contract import FUNCTION_SELECTOR
from apps.transaction import schemas

lock = asyncio.Lock()


class BaseTransaction:

    class TransactionNotSign(Exception):
        pass

    class TransactionSent(Exception):
        pass

    def __init__(self, obj: AsyncTransaction, expected_commission: dict, type: schemas.TransactionType, **kwargs):
        self.obj = obj
        self.type = type

        self._expected_commission = expected_commission
        self._commission: Optional[dict] = None

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._is_signed = False
        self._is_send = False

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
            commission=self.expected_commission_schema,
        )

    @property
    def is_expired(self) -> bool:
        return self.obj.is_expired

    async def update(self) -> NoReturn:
        await self.obj.update()

    async def sign(self, private_key: PrivateKey) -> NoReturn:
        self.obj = self.obj.sign(private_key)
        self._is_signed = True

    async def _valid_send(self) -> NoReturn:
        if self._is_send:
            raise self.TransactionSent(f'{self.id} has already been sent!')
        if not self._is_signed:
            raise self.TransactionNotSign()
        if not self.obj.is_expired:
            await self.update()

    async def send(self) -> schemas.BaseResponseSendTransactionSchema:
        await self._valid_send()

        async with lock:
            self._raw_transaction = await self.obj.broadcast()
            self._transaction_info = await self._raw_transaction.wait()

        await self._post_send()
        return await self._make_response()

    async def _post_send(self) -> NoReturn:
        self._commission = dict(
            fee=decimal.Decimal(self._transaction_info.get('fee', 0)),
            bandwidth=self._transaction_info.get('receipt', {}).get('net_usage', 0),
            energy=self._transaction_info.get('receipt', {}).get('energy_usage_total', 0),
        )

    async def _make_response(self, **kwargs) -> schemas.BaseResponseSendTransactionSchema:
        raise NotImplementedError()

    @classmethod
    async def create(cls, body: schemas.BaseCreateTransactionSchema) -> BaseTransaction:
        raise NotImplementedError()


class NativeTransfer(BaseTransaction):

    async def _make_response(self, **kwargs) -> schemas.ResponseSendTransfer:
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
            amount=body.amount,
        )


class Transfer(NativeTransfer):
    """
    Method: transfer(address recipient, uint256 amount)
    MethodID: a9059cbb
    """

    @classmethod
    async def create(cls, body: schemas.BodyCreateTransfer) -> BaseTransaction:
        contract = body.contract

        raw_obj = await contract.transfer(
            from_address=body.from_address,
            to_address=body.to_address,
            amount=body.amount,
        )

        obj = await raw_obj.fee_limit(
            body.fee_limit,
        ).build()

        return cls(
            obj,
            expected_commission=await node.calculator.calculate(
                raw_data=getattr(obj, '_raw_data'),
                owner_address=body.from_address,
                function_selector=FUNCTION_SELECTOR.TRANSFER,
                parameter=[
                    body.to_address,
                    contract.to_int(body.amount),
                ],
                currency=body.currency,
            ),
            type=body.transaction_type,
            from_address=body.from_address,
            to_address=body.to_address,
            currency=body.currency,
            amount=body.amount,
        )


class Approve(BaseTransaction):

    async def _make_response(self, **kwargs) -> schemas.ResponseSendApprove:
        return schemas.ResponseSendApprove(
            id=self.id,
            timestamp=self._raw_transaction['raw_data']['timestamp'],
            commission=self.commission_schema,
            amount=getattr(self, 'amount'),
            owner_address=getattr(self, 'owner_address'),
            sender_address=getattr(self, 'sender_address'),
            currency=getattr(self, 'currency'),
            type=self.type,
        )

    @classmethod
    async def create(cls, body: schemas.BodyCreateApprove) -> BaseTransaction:
        contract = body.contract
        raw_obj = await contract.approve(
            owner_address=body.owner_address,
            sender_address=body.sender_address,
            amount=body.amount,
        )

        obj = await raw_obj.fee_limit(
            body.fee_limit,
        ).build()

        return cls(
            obj,
            expected_commission=await node.calculator.calculate(
                raw_data=getattr(obj, '_raw_data'),
                owner_address=body.owner_address,
                function_selector=FUNCTION_SELECTOR.APPROVE,
                parameter=[
                    body.sender_address,
                    contract.to_int(body.amount),
                ],
                currency=body.currency,
            ),
            type=body.transaction_type,
            owner_address=body.owner_address,
            sender_address=body.sender_address,
            currency=body.currency,
            amount=body.amount,
        )


class TransferFrom(BaseTransaction):

    async def _make_response(self, **kwargs) -> schemas.ResponseSendTransferFrom:
        return schemas.ResponseSendTransferFrom(
            id=self.id,
            timestamp=self._raw_transaction['raw_data']['timestamp'],
            commission=self.commission_schema,
            amount=getattr(self, 'amount'),
            owner_address=getattr(self, 'owner_address'),
            sender_address=getattr(self, 'sender_address'),
            recipient_address=getattr(self, 'recipient_address'),
            currency=getattr(self, 'currency'),
            type=self.type,
        )

    @classmethod
    async def create(cls, body: schemas.BodyCreateTransferFrom) -> BaseTransaction:
        contract = body.contract
        raw_obj = await contract.transfer_from(
            owner_address=body.owner_address,
            sender_address=body.sender_address,
            recipient_address=body.recipient_address,
            amount=body.amount,
        )

        obj = await raw_obj.fee_limit(
            body.fee_limit,
        ).build()

        return cls(
            obj,
            expected_commission=await node.calculator.calculate(
                raw_data=getattr(obj, '_raw_data'),
                owner_address=body.owner_address,
                function_selector=FUNCTION_SELECTOR.TRANSFER_FROM,
                parameter=[
                    body.sender_address,
                    body.recipient_address,
                    contract.to_int(body.amount),
                ],
                currency=body.currency,
            ),
            type=body.transaction_type,
            owner_address=body.owner_address,
            sender_address=body.sender_address,
            recipient_address=body.recipient_address,
            currency=body.currency,
            amount=body.amount,
        )


class Delegate(BaseTransaction):

    async def _make_response(self, **kwargs) -> schemas.FieldStake:
        return schemas.FieldStake(
            id=self.id,
            timestamp=self._raw_transaction['raw_data']['timestamp'],
            commission=self.commission_schema,
            amount=getattr(self, 'amount'),
            from_address=getattr(self, 'from_address'),
            to_address=getattr(self, 'to_address'),
            resource=getattr(self, 'resource'),
            type=self.type,
        )

    @classmethod
    async def create(cls, body: schemas.BodyCreateFreeze) -> BaseTransaction:
        obj = await node.client.trx.delegate_resource(
            owner=body.owner_address,
            receiver=body.recipient_address,
            balance=body.amount,
            resource=body.resource,
        ).fee_limit(
            body.fee_limit,
        ).build()

        return cls(
            obj=obj,
            expected_commission=await node.calculator.calculate(
                raw_data=getattr(obj, '_raw_data'),
            ),
            type=body.sub_transaction_type,
            from_address=body.owner_address,
            to_address=body.recipient_address,
            amount=body.amount,
            resource=body.resource,
        )


class Freeze(BaseTransaction):

    def __init__(self, sub_obj: Optional[BaseTransaction] = None, **kwargs):
        super(Freeze, self).__init__(**kwargs)

        self.sub_obj: BaseTransaction = sub_obj

    @property
    def is_expired(self) -> bool:
        if self.sub_obj:
            return self.obj.is_expired and self.sub_obj.is_expired
        return self.obj.is_expired

    @property
    def to_schema(self) -> schemas.ResponseCreateFreeze:
        return schemas.ResponseCreateFreeze(
            id=self.id,
            commission=self.expected_commission_schema,
            general_commission=self.expected_general_commission_schema,
        )

    @property
    def expected_general_commission_schema(self) -> schemas.ResponseCommission:
        fee = self._expected_commission
        if self.sub_obj:
            sub_expected_commission = self.sub_obj._expected_commission
            fee = dict(
                fee=fee['fee'] + sub_expected_commission['fee'],
                bandwidth=fee['bandwidth'] + sub_expected_commission['bandwidth'],
                energy=fee['energy'] + sub_expected_commission['energy'],
            )
        return schemas.ResponseCommission(**fee)

    @property
    def general_commission_schema(self) -> schemas.ResponseCommission:
        fee = self._commission
        if self.sub_obj:
            sub_commission = self.sub_obj._commission
            fee = dict(
                fee=fee['fee'] + sub_commission['fee'],
                bandwidth=fee['bandwidth'] + sub_commission['bandwidth'],
                energy=fee['energy'] + sub_commission['energy'],
            )
        return schemas.ResponseCommission(**fee)

    async def update(self) -> NoReturn:
        if self.sub_obj:
            await self.sub_obj.obj.update()
        await super(Freeze, self).update()

    async def sign(self, private_key: PrivateKey) -> NoReturn:
        if self.sub_obj:
            await self.sub_obj.sign(private_key)
        await super(Freeze, self).sign(private_key)

    async def send(self) -> schemas.ResponseSendFreeze:
        await self._valid_send()

        async with lock:
            self._raw_transaction = await self.obj.broadcast()
            self._transaction_info = await self._raw_transaction.wait()

        sub_schema = None
        if self.sub_obj:
            sub_schema = await self.send()

        await self._post_send()
        return await self._make_response(sub_schema=sub_schema)

    async def _make_response(self, **kwargs) -> schemas.ResponseSendFreeze:
        return schemas.ResponseSendFreeze(
            freeze=schemas.FieldStake(
                id=self.id,
                timestamp=self._raw_transaction['raw_data']['timestamp'],
                commission=self.commission_schema,
                amount=getattr(self, 'amount'),
                from_address=getattr(self, 'owner_address'),
                to_address=getattr(self, 'owner_address'),
                resource=getattr(self, 'resource'),
                type=self.type,
            ),
            delegate=kwargs.get('sub_schema', None),
            general_commission=self.general_commission_schema,
            resource=getattr(self, 'resource'),
        )

    @classmethod
    async def create(cls, body: schemas.BodyCreateFreeze) -> BaseTransaction:
        obj = None
        if not body.use_free_frozen_balance:
            obj = await node.client.trx.freeze_balance(
                owner=body.owner_address,
                amount=body.amount_sun,
                resource=body.resource,
            ).fee_limit(
                body.fee_limit,
            ).build()

        delegate_obj = None
        if body.with_delegate:
            delegate_obj = await Delegate.create(body=body)

        if not obj:
            return delegate_obj

        return cls(
            sub_obj=delegate_obj,
            obj=obj,
            expected_commission=await node.calculator.calculate(
                raw_data=getattr(obj, '_raw_data'),
            ),
            type=body.transaction_type,
            owner_address=body.owner_address,
            recipient_address=body.recipient_address,
            amount=body.amount,
            resource=body.resource,
        )
