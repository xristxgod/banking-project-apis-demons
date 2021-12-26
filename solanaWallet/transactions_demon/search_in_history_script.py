import sys
import asyncio
import argparse
from demon import TransactionDemon


def create_parser():
    """:return: Getting scrypt params"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', default=0)
    parser.add_argument('-e', '--end', default=None)
    return parser


async def run(*args):
    demon = TransactionDemon()
    is_success = await demon.get_transactions_in_blocks_range(*args)
    print(f'Script ran success: {is_success}')


if __name__ == '__main__':
    namespace = create_parser().parse_args(sys.argv[1:])
    asyncio.run(run(namespace.start, namespace.end))
