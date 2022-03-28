from src.services.to_main_wallet_native import send_to_main_wallet_native
from src.services.to_main_wallet_token import send_to_main_wallet_token


async def send_transaction_service(address, token):
    if token in ['bnb', None]:
        await send_to_main_wallet_native(address)
    else:
        await send_to_main_wallet_token(address, token)
