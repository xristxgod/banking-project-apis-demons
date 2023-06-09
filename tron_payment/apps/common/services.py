from mnemonic import Mnemonic

from apps.common import schemas
from core.node import node


async def create_wallet(body: schemas.BodyCreateWallet):
    mnemonic = body.mnemonic
    if not mnemonic:
        mnemonic = Mnemonic('english').generate()

    result = node.client.generate_address_from_mnemonic(
        mnemonic=mnemonic,
        passphrase=body.passphrase,
    )

    return schemas.ResponseCreateWallet(
        mnemonic=mnemonic,
        passphrase=body.passphrase,
        address=result['base58check_address'],
        public_key=result['public_key'],
        private_key=result['private_key'],
    )


async def get_balance(body: schemas.BodyBalance):
    if body.is_native:
        amount = await node.native.balance(body.address, True)
    else:
        amount = await body.stable_coin.balance(body.address, True)

    return schemas.ResponseBalance(
        amount=amount,
        **body.dict(),
    )

