from config import Decimal, tokens, ADMIN_ADDRESS, ADMIN_PRIVATE_KEY, decimal, logger, NATIVE_LIMIT
from src.services.get_balance import get_balance
from src.services.get_private_key import get_private_key
from src.services.send_transaction import create_transaction, sign_send_transaction


async def is_dust(value: Decimal, token: str) -> bool:
    return value < tokens.__getattribute__(f'TOKEN_COST_{token.upper()}')


async def send_to_main_wallet_token(address: str, token: str):
    balance = await get_balance(address=address, token=token)
    logger.error(f'BALANCE {token}: {balance}')
    if await is_dust(balance, token):
        return
    native_balance = await get_balance(address=address)

    if native_balance < NATIVE_LIMIT:
        created_tx = await create_transaction(
            from_address=ADMIN_ADDRESS,
            to_address=address,
            amount=NATIVE_LIMIT
        )
        await sign_send_transaction(
            payload=created_tx['createTxHex'],
            private_key=ADMIN_PRIVATE_KEY,
        )
    else:
        created_tx = await create_transaction(
            from_address=address,
            to_address=ADMIN_ADDRESS,
            amount=balance,
            token=token
        )
        logger.error(f'CREAETED ({token}) {created_tx}')
        private_key = await get_private_key(address=address)
        if private_key is not None:
            signed = await sign_send_transaction(
                payload=created_tx['createTxHex'],
                private_key=private_key,
                token=token
            )
            logger.error(f'SENDED TO MAIN WALLET ({token}) {signed}')
