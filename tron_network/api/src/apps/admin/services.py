import json

from src.services import common, wallet, transaction
from src.apps.admin import schemas
from src.apps.common import encoder


async def create_wallet(body: schemas.BodyAdminCreateWallet) -> schemas.ResponseAdminCreateWallet:
    new_wallet = await common.create_wallet(index=body.index)
    return schemas.ResponseAdminCreateWallet(
        index=new_wallet['index'],
        address=new_wallet['address'],
        hex_private_key=await encoder.encode(new_wallet['private_key']),
    )


async def wallet_balance(body: schemas.BodyAdminBalance) -> schemas.ResponseAdminBalance:
    return schemas.ResponseAdminBalance(
        amount=await wallet.balance(address=body.address, currency=body.currency)
    )


async def create_transfer(body: schemas.BodyAdminTransfer) -> schemas.ResponseAdminTransfer:
    raw_transaction = await transaction.transfer(
        from_address=body.from_address,
        to_address=body.to_address,
        amount=body.amount,
        currency=body.currency,
        fee_limit=body.fee_limit,
    )
    return schemas.ResponseAdminTransfer(
        raw_data=json.dumps(raw_transaction.to_json()),
        body_transaction=schemas.ResponseTransaction(

        ),
        extra=schemas.ResponseCommission(

        )
    )
