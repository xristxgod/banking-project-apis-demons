from typing import Optional

from src_1.utils.types import TronAccountAddress
from src_1.external.client import get_request
from config import decimals


async def get_balance(address: TronAccountAddress, token: Optional[str] = "tron"):
    balance = await get_request(f"/{token}/get-balance/{address}")
    return decimals.create_decimal(balance["balance"])
