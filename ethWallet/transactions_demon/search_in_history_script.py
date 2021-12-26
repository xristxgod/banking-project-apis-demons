import sys
import argparse
from run_demon import TransactionsDemon, logger
from asyncio import run


def create_parser():
    """:return: Getting script params"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", default=0)
    parser.add_argument("-e", "--end", default=None)
    return parser


async def async_run(*args):
    logger.error(f"CREATING DEMON INSTANCE")
    demon = TransactionsDemon()
    logger.error(f"START SEARCH IN HISTORY")
    is_success = await demon.start(*args)
    logger.info(f"SCRIPT RAN SUCCESS: {is_success}")


if __name__ == '__main__':
    namespace = create_parser().parse_args(sys.argv[1:])
    run(async_run(
        int(namespace.start) if namespace.start is not None else None,
        int(namespace.end) if namespace.end is not None else None
    ))
