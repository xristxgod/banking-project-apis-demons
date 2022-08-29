from typing import Optional, Dict
from decimal import Decimal

from src_1.utils.types import TronAccountAddress, TronAccountPrivateKey
from src_1.external.client import post_request


async def create_transaction(
        from_address: TronAccountAddress, to_address: TronAccountAddress,
        amount: Decimal, token: Optional[str] = "tron"
) -> Optional[Dict]:
    return await post_request(
        f"/{token}/create-transaction-for-internal-services",
        fromAddress=from_address,
        outputs=[{to_address: "%.6f" % amount}]
    )


async def sign_send_transaction(
        createTxHex: str, private_key: TronAccountPrivateKey
) -> bool:
    return await post_request(
        f"/tron/sign-send-transaction-for-internal-services",
        createTxHex=createTxHex,
        privateKeys=[private_key]
    ) is not None
