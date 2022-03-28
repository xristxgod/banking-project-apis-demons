import sys
import argparse
from src.demon import TransactionsDemon, logger
from asyncio import run

from src.search_by_addresses import AddressesDemon


def create_parser():
    """:return: Getting script params"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", default=0)
    parser.add_argument("-e", "--end", default=None)
    parser.add_argument("-a", "--addresses", default=None)
    return parser


async def async_run(start, end, addresses):
    logger.error(f"CREATING DEMON INSTANCE")
    if addresses is None:
        demon = TransactionsDemon()
        logger.error(f"START SEARCH IN HISTORY")
    else:
        demon = AddressesDemon()
        logger.error(f"START SEARCH BY ADDRESSES")
    is_success = await demon.start(start, end, addresses)
    logger.info(f"SCRIPT RAN SUCCESS: {is_success}")


if __name__ == '__main__':
    namespace = create_parser().parse_args(sys.argv[1:])
    run(async_run(
        int(namespace.start) if namespace.start is not None else None,
        (int(namespace.end) + 1) if namespace.end is not None else None,
        namespace.addresses.split(' ') if namespace.addresses is not None else None
    ))
