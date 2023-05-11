import abc
import enum
import json
import decimal

import pydantic
from tronpy.keys import PrivateKey
from tronpy.async_tron import AsyncTransaction

from core.crypto import node
from core.crypto.utils import from_sun
from core.crypto.calculator import FEE_METHOD_TYPES
from apps.common import schemas


class InvalidCreateTransaction(Exception):
    pass


class TransactionType(enum.Enum):
    TRANSFER = 'transfer'
    APPROVE = 'approve'
    TRANSFER_FROM = 'transfer_from'


async def create_wallet(body: schemas.BodyCreateWallet) -> schemas.ResponseCreateWallet:
    response = node.client.generate_address_from_mnemonic(
        mnemonic=body.mnemonic,
        passphrase=body.passphrase,
    )
    return schemas.ResponseCreateWallet(
        mnemonic=body.mnemonic,
        passphrase=body.passphrase,
        private_key=response['private_key'],
        public_key=response['public_key'],
        address=response['base58check_address'],
    )


async def wallet_balance(body: schemas.BodyWalletBalance) -> schemas.ResponseWalletBalance:
    if body.currency == 'TRX':
        balance = await node.client.get_account_balance(body.address)
    else:
        balance = await body.contract.balance_of(body.address)
    return schemas.ResponseWalletBalance(
        balance=balance,
    )


async def allowance(body: schemas.BodyAllowance) -> schemas.ResponseAllowance:
    amount = await body.contract.allowance(
        owner_address=body.owner_address,
        spender_address=body.spender_address,
    )
    return schemas.ResponseAllowance(
        amount=amount,
    )


class BaseCreateTransaction(abc.ABC):
    @abc.abstractclassmethod
    async def valid(cls, body: pydantic.BaseModel, fee: decimal.Decimal, **kwargs): ...

    @abc.abstractclassmethod
    async def _create(cls, body: pydantic.BaseModel) -> dict: ...

    @abc.abstractclassmethod
    async def create(cls, body: pydantic.BaseModel) -> pydantic.BaseModel: ...


class CreateTransfer(BaseCreateTransaction):

    @classmethod
    async def valid(cls, body: schemas.BodyCreateTransfer, fee: decimal.Decimal, **kwargs):
        native_balance = await node.client.get_account_balance(body.from_address)

        if body.is_native:
            balance = native_balance
            has_native = has_amount = (balance - (body.amount + fee)) >= 0
        else:
            balance = await body.contract.balance_of(body.from_address)
            has_native = (native_balance - fee) > 0
            has_amount = (balance - body.amount) >= 0

        if not all([has_amount, has_native]):
            raise InvalidCreateTransaction('Invalid create transfer')

    @classmethod
    async def _create(cls, body: schemas.BodyCreateTransfer) -> dict:
        if body.is_native:
            transaction = node.client.trx.transfer(
                body.from_address,
                to=body.to_address,
                amount=body.sun_amount
            )
        else:
            transaction = await body.contract.transfer(
                body.from_address,
                to_address=body.to_address,
                amount=body.amount,
            )

        transaction = transaction.fee_limit(
            body.fee_limit
        )
        created_transaction = await transaction.build()
        return created_transaction.to_json()

    @classmethod
    async def create(cls, body: schemas.BodyCreateTransfer) -> schemas.ResponseCreateTransaction:
        commission = await node.calculator.calculate(
            method=node.calculator.Method.TRANSFER,
            from_address=body.from_address,
            to_address=body.to_address,
            currency=body.currency,
            amount=body.amount,
        )

        await cls.valid(body, commission['fee'])

        created_transaction_dict = await cls._create(body=body)

        payload = {
            'data': created_transaction_dict,
            'extra': {
                'amount': body.amount,
                'from_address': body.from_address,
                'to_address': body.to_address,
                'currency': body.currency,
                'type': TransactionType.TRANSFER.value,
            }
        }

        return schemas.ResponseCreateTransaction(
            payload=json.dumps(payload, default=str),
            commission=schemas.ResponseCommission(**commission),
        )


class CreateApprove(BaseCreateTransaction):

    @classmethod
    async def valid(cls, body: schemas.BodyCreateApprove, fee: decimal.Decimal, **kwargs):
        native_balance = await node.client.get_account_balance(body.spender_address)

        has_native = (native_balance - fee) > 0

        if not all([has_native]):
            raise InvalidCreateTransaction('Invalid create approve')

    @classmethod
    async def _create(cls, body: schemas.BodyCreateApprove) -> dict:
        transaction = await body.contract.approve(
            owner_address=body.owner_address,
            spender_address=body.spender_address,
            amount=body.amount,
        )
        transaction = transaction.fee_limit(
            body.fee_limit
        )
        created_transaction = await transaction.build()
        return created_transaction.to_json()

    @classmethod
    async def create(cls, body: schemas.BodyCreateApprove) -> schemas.ResponseCreateTransaction:
        commission = await node.calculator.calculate(
            method=node.calculator.Method.APPROVE,
            owner_address=body.owner_address,
            spender_address=body.spender_address,
            currency=body.currency,
            amount=body.amount,
        )

        await cls.valid(body, fee=commission['fee'])

        created_transaction_dict = await cls._create(body=body)

        payload = {
            'data': created_transaction_dict,
            'extra': {
                'amount': body.amount,
                'from_address': body.owner_address,
                'to_address': body.spender_address,
                'currency': body.currency,
                'type': TransactionType.APPROVE.value,
            }
        }
        return schemas.ResponseCreateTransaction(
            payload=json.dumps(payload, default=str),
            commission=schemas.ResponseCommission(**commission),
        )


class CreateTransferFrom(BaseCreateTransaction):

    @classmethod
    async def valid(cls, body: schemas.BodyCreateTransferFrom, fee: decimal.Decimal, **kwargs):
        pass

    @classmethod
    async def _create(cls, body: schemas.BodyCreateTransferFrom) -> dict:
        transaction = await body.contract.transfer_from(
            owner_address=body.owner_address,
            from_address=body.from_address,
            to_address=body.to_address,
            amount=body.amount,
        )
        transaction = transaction.fee_limit(
            body.fee_limit
        )
        created_transaction = await transaction.build()
        return created_transaction.to_json()

    @classmethod
    async def create(cls, body: schemas.BodyCreateTransferFrom) -> schemas.ResponseCreateTransaction:
        commission = await node.calculator.calculate(
            method=node.calculator.Method.TRANSFER_FROM,
            owner_address=body.owner_address,
            from_address=body.from_address,
            to_address=body.to_address,
            currency=body.currency,
            amount=body.amount,
        )

        await cls.valid(body, fee=commission['fee'])

        created_transaction_dict = await cls._create(body=body)

        payload = {
            'data': created_transaction_dict,
            'extra': {
                'amount': body.amount,
                'from_address': body.from_address,
                'to_address': body.to_address,
                'currency': body.currency,
                'owner_address': body.owner_address,
                'type': TransactionType.TRANSFER_FROM.value,
            }
        }
        return schemas.ResponseCreateTransaction(
            payload=json.dumps(payload, default=str),
            commission=schemas.ResponseCommission(**commission),
        )


class SendTransaction:
    @classmethod
    async def _send_transaction(cls, private_key_obj: PrivateKey, transaction: AsyncTransaction) -> dict:
        signed_transaction = transaction.sign(priv_key=private_key_obj)
        transaction = await signed_transaction.broadcast()
        return await transaction.wait()

    @classmethod
    async def send_transaction(cls, body: schemas.BodySendTransaction) -> schemas.ResponseSendTransaction:
        created_transaction = await body.create_transaction_obj()

        transaction_info = await cls._send_transaction(body.private_key_obj, created_transaction)

        fee = transaction_info.get('fee', decimal.Decimal(0))
        if fee > 0:
            fee = from_sun(fee)

        return schemas.ResponseSendTransaction(
            transaction_id=transaction_info['id'],
            timestamp=transaction_info['blockTimeStamp'],
            fee=fee,
            amount=decimal.Decimal(body.extra.get('amount')),
            from_address=body.extra.get('from_address'),
            to_address=body.extra.get('to_address'),
            currency=body.extra.get('currency'),
            extra=schemas.ResponseSendTransactionExtra(
                type=body.extra.get('type'),
                owner_address=body.extra.get('owner_address'),
            )
        )


async def fee_calculator(body: schemas.BodyCommission, method: FEE_METHOD_TYPES) -> schemas.ResponseCommission:
    result = await node.fee_calculator.calculate(method=method, **body.parameter)
    return schemas.ResponseCommission(**result)
