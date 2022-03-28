from typing import Optional
from config import Decimal
from src.external.client import post_request


async def create_transaction(
        from_address: str, to_address: str,
        amount: Decimal, token: Optional[str] = 'bnb',
) -> Optional[dict]:
    return await post_request(
        f'bsc_bip20_{token.lower()}/create-transaction-for-internal-services',
        data={
            'fromAddress': from_address,
            'outputs': [{to_address: "%.8f" % amount}],
            'adminFee': '0.0',
        }
    )


async def sign_send_transaction(
        payload: str, private_key: str, token: Optional[str] = 'bnb'
) -> bool:
    return await post_request(
        f'bsc_bip20_{token.lower()}/sign-send-transaction-for-internal-services',
        data={
            'createTxHex': payload,
            'privateKeys': [private_key]
        }
    )
