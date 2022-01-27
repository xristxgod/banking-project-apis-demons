from typing import Optional
from src.external.client import post_request
from config import decimal, Decimal


async def get_balance(address: str, token: Optional[str] = 'bnb') -> Decimal:
    balance_json = await post_request(
        f'bsc_bip20_{token.lower()}/get-balance',
        data={'address': address}
    )
    return decimal.create_decimal(balance_json['balance'])
