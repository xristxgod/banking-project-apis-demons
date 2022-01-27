import sys
import asyncio
import argparse
from typing import List, Union

from src.utils.types import TronAccountAddress, TokenTRC20
from src.external.db import get_wallets
from src.services.to_main_wallet_native import send_to_main_wallet_native
from src.services.to_main_wallet_token import send_to_main_wallet_token

def create_parser():
    """:return: Getting script params"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", default=None)
    parser.add_argument("-t", "--token", default=None)
    return parser

async def initial_for_address(address: TronAccountAddress, token: TokenTRC20):
    if token in ["tron", "trx", None]:
        await send_to_main_wallet_native(address)
    else:
        await send_to_main_wallet_token(address, token)

async def async_run(token: TokenTRC20 = None, address: Union[List[TronAccountAddress], TronAccountAddress] = None):
    if address is None:
        addresses: List[TronAccountAddress] = await get_wallets()
    else:
        addresses: List[TronAccountAddress] = [address]

    if token is None:
        token_list = ["TRX", "USDT", "USC"]
    else:
        token_list = [token]

    for _address in addresses:
        for _token in token_list:
            await initial_for_address(address=_address, token=token)

if __name__ == '__main__':
    namespace = create_parser().parse_args(sys.argv[1:])
    asyncio.run(async_run(
        address=namespace.address,
        token=namespace.token,
    ))