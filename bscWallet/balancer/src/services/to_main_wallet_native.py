from typing import Optional

from config import ADMIN_ADDRESS, decimal, Decimal, DUST_MULTIPLICATOR, logger
from src.external.client import post_request
from src.services.get_balance import get_balance
from src.services.get_private_key import get_private_key
from src.services.send_transaction import create_transaction, sign_send_transaction


async def is_native_dust(value: Decimal, gas: Decimal, limit: Optional[Decimal] = None) -> bool:
    if limit is not None:
        diff = value - limit
    else:
        diff = value - gas * DUST_MULTIPLICATOR
    return diff < decimal.create_decimal('0.0')


async def send_to_main_wallet_native(address: str, limit: Optional[Decimal] = None):
    balance = await get_balance(address)

    gas_json = await post_request(
        f'bsc_bip20_bnb/get-optimal-gas',
        data={
            'fromAddress': address,
            'toAddress': ADMIN_ADDRESS,
            'amount': "%.8f" % balance
        }
    )
    gas = decimal.create_decimal(gas_json['gas'])
    gas_native = gas / decimal.create_decimal(10 ** 18)

    if await is_native_dust(balance - gas_native, gas_native, limit=limit):
        return

    created_tx = await create_transaction(
        from_address=address,
        to_address=ADMIN_ADDRESS,
        amount=balance - gas_native
    )
    private_key = await get_private_key(address=address)
    if private_key is not None:
        signed = await sign_send_transaction(
            payload=created_tx['createTxHex'],
            private_key=private_key
        )
        logger.error(f'SENDED TO MAIN WALLET (BSC) {signed}')
