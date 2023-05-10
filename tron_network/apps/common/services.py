from core.crypto import node
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


class Transfer:
    @classmethod
    async def create_transfer(cls, body: schemas.BodyCreateTransfer) -> schemas.ResponseCreateTransfer:
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
