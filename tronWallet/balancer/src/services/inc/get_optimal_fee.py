from typing import Dict
from decimal import Decimal

from src.external.client import get_request
from src.services.helper.activate_account import activate_account
from src.utils.types import TronAccountAddress
from config import decimals

async def get_optimal_fee(from_address: TronAccountAddress, to_address: TronAccountAddress, token_network: str = "tron") -> Decimal:
    values: Dict = await get_request(f"/{token_network}/get-optimal-fee/{from_address}&{to_address}")
    if "error" in values and values["error"] == "account not found on-chain":
        is_activate = await activate_account(from_address=from_address)
        if is_activate:
            values: Dict = await get_request(f"/{token_network}/get-optimal-fee/{from_address}&{to_address}")
            fee: Decimal = decimals.create_decimal(values["fee"])
        else:
            raise Exception("Account has not been activated")
    else:
        fee: Decimal = decimals.create_decimal(values["fee"])
    if fee > 0:
        return fee * decimals.create_decimal(1.2)
    else:
        return decimals.create_decimal(1.2)