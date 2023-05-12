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
        sender_address=body.sender_address,
    )
    return schemas.ResponseAllowance(
        amount=amount,
    )
