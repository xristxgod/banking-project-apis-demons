import decimal
import json

from core.crypto import node
from core.crypto.utils import from_sun
from apps.common import schemas


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


class CreateTransfer:

    class InvalidCreateTransfer(Exception):
        pass

    @classmethod
    async def valid_create_transfer(cls, body: schemas.BodyCreateTransfer, fee: decimal.Decimal) -> bool:
        native_balance = await node.client.get_account_balance(body.from_address)

        if body.is_native:
            balance = native_balance
            has_native = has_amount = (balance - (body.amount + fee)) >= 0
        else:
            balance = await body.contract.balance_of(body.from_address)
            has_native = native_balance - fee
            has_amount = (balance - body.amount) >= 0

        if not all([has_amount, has_native]):
            raise cls.InvalidCreateTransfer('Invalid create transfer')

    @classmethod
    async def create_transfer(cls, body: schemas.BodyCreateTransfer) -> schemas.ResponseCreateTransfer:
        commission = await node.calculator.calculate(
            method=node.calculator.Method.TRANSFER,
            from_address=body.from_address,
            to_address=body.to_address,
            currency=body.currency,
            amount=body.amount,
        )

        await cls.valid_create_transfer(body, commission['fee'])

        if body.is_native:
            transaction = node.client.trx.transfer(
                body.from_address,
                to=body.to_address,
                amount=body.sun_amount
            )
        else:
            transaction = body.contract.transfer(
                body.from_address,
                to_address=body.to_address,
                amount=body.amount,
            )

        transaction = transaction.fee_limit(
            body.fee_limit
        )
        created_transaction = await transaction.build()

        return schemas.ResponseCreateTransfer(
            payload=json.dumps(created_transaction.to_json()),
            commission=schemas.ResponseCommission(**commission),
            extra={
                'amount': body.amount,
                'from_address': body.from_address,
                'to_address': body.to_address,
                'currency': body.currency,
            }
        )


async def send_transaction(body: schemas.BodySendTransaction) -> schemas.ResponseSendTransaction:
    created_transaction = body.create_transaction_obj()

    signed_transaction = created_transaction.sign(body.private_key_obj)
    transaction = await signed_transaction.broadcast()
    transaction_info = await transaction.wait()

    fee = transaction_info.get('fee', 0)
    if fee > 0:
        fee = from_sun(fee)

    return schemas.ResponseSendTransaction(
        transaction_id=transaction_info['id'],
        timestamp=transaction_info['blockTimeStamp'],
        fee=fee,
        amount=body.extra.get('amount'),
        from_address=body.extra.get('from_address'),
        to_address=body.extra.get('to_address'),
        currency=body.extra.get('currency'),
    )
