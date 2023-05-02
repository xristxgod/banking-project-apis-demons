from core.base import BaseNodeService
from apps.common import schemas


class CommonService(BaseNodeService):
    async def create_wallet(self, body: schemas.BodyCreateWallet, *, is_encode: bool) -> schemas.ResponseCreateWallet:
        wallet_config = self.node.generate_address_from_mnemonic(
            mnemonic=body.mnemonic,
            passphrase=body.passphrase,
        )

        if is_encode:
            pass

        return schemas.ResponseCreateWallet(
            address=wallet_config['base58check_address'],
            private_key=wallet_config['private_key'],
            public_key=wallet_config['public_key'],
            **body.dict()
        )

    async def get_balance(self):
        pass
