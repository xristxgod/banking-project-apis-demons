import sys
import argparse
from src.demon import TransactionsDemon, logger
from src.search_by_addresses import AddressesDemon


def create_parser():
    """:return: Getting scrypt params"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', default=0)
    parser.add_argument('-e', '--end', default=None)
    parser.add_argument('-a', '--addresses', default=None)
    return parser


def run(start, end, addresses):
    logger.error(f'CREATING DEMON INSTANCE')
    args = [start, end]
    if addresses is None:
        demon = TransactionsDemon()
    else:
        demon = AddressesDemon()
        args.append(addresses)
    logger.error(f'START SEARCH IN HISTORY')
    is_success = demon.start(*args)
    logger.info(f'SCRIPT RAN SUCCESS: {is_success}')


if __name__ == '__main__':
    namespace = create_parser().parse_args(sys.argv[1:])
    run(
        int(namespace.start) if namespace.start is not None else None,
        int(namespace.end) + 1 if namespace.end is not None else None,
        namespace.addresses.split(' ') if namespace.addresses is not None else None
    )
