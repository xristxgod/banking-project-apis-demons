from src.v1.services.wallet_eth import wallet_bsc
from config import ADMIN_ADDRESS, MIN_MAIN_BALANCE, decimal


async def is_native() -> bool:
    """Checks if there is a balance on the central wallet"""
    balance = (await wallet_bsc.get_balance(address=ADMIN_ADDRESS)).balance
    if decimal.create_decimal(balance) < MIN_MAIN_BALANCE:
        return False
    return True
