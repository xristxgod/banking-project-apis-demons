import sys
import argparse
from src.demon import TransactionsDemon, logger


def create_parser():
    """:return: Getting scrypt params"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', default=0)
    parser.add_argument('-e', '--end', default=None)
    return parser


def run(*args):
    logger.error(f'CREATING DEMON INSTANCE')
    demon = TransactionsDemon()
    logger.error(f'START SEARCH IN HISTORY')
    is_success = demon.start(*args)
    logger.info(f'SCRIPT RAN SUCCESS: {is_success}')


if __name__ == '__main__':
    namespace = create_parser().parse_args(sys.argv[1:])
    run(
        int(namespace.start) if namespace.start is not None else None,
        int(namespace.end) + 1 if namespace.end is not None else None
    )
