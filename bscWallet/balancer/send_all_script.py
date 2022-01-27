import sys
import asyncio
import argparse
from config import logger, tokens
from src.external.db import DB
from src.services.to_main_wallet_native import send_to_main_wallet_native
from src.services.to_main_wallet_token import send_to_main_wallet_token


def create_parser():
    """:return: Getting script params"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", default=None)
    parser.add_argument("-t", "--token", default=None)
    parser.add_argument("-l", "--limit", default=None)
    return parser


async def initial_for_address(address: str, token: str, limit):
    if token in ['bsc', None]:
        await send_to_main_wallet_native(address, limit=limit)
    else:
        await send_to_main_wallet_token(address, token)


async def async_run(address, token, limit):
    if address is None:
        addresses = await DB.get_wallets()
    else:
        addresses = [address]

    if token is None:
        token_list = ['BSC'] + tokens.get_tokens()
    else:
        token_list = [token]

    for _address in addresses:
        logger.error(f'ADDRESS: {_address}')
        for _token in token_list:
            logger.error(f' + TOKEN: {_token}')
            await initial_for_address(_address, _token.lower(), limit)


if __name__ == "__main__":
    namespace = create_parser().parse_args(sys.argv[1:])
    asyncio.run(async_run(
        address=namespace.address,
        token=namespace.token,
        limit=namespace.limit
    ))
