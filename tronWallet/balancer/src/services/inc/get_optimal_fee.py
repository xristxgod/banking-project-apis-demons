from typing import Dict
from decimal import Decimal

from src.external.client import get_request
from src.utils.types import TronAccountAddress
from config import AdminAddress, AdminPrivateKey, logger, decimals

async def get_optimal_fee(from_address: TronAccountAddress, to_address: TronAccountAddress, token_network: str = "tron") -> Decimal:
    values: Dict = await get_request(f"/{token_network}/get-optimal-fee/{from_address}&{to_address}")
    fee: Decimal = decimals.create_decimal(values["fee"])
    if fee > 0:
        return fee * decimals.create_decimal(1.2)
    else:
        return decimals.create_decimal(1.2)