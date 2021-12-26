import sys
import argparse
from run_demon import TransactionDemon, logger
from asyncio import run

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", default=0)
    parser.add_argument("-e", "--end", default=None)
    return parser

async def async_run(*args):
    logger.error(f"Creating demon instance")
    demon = TransactionDemon()
    logger.error(f"Start search in history")
    is_success = await demon.start(*args)
    logger.info(f"Script ran success: {is_success}")

if __name__ == '__main__':
    namespace = create_parser().parse_args(sys.argv[1:])
    run(async_run(
        int(namespace.start) if namespace.start is not None else None,
        int(namespace.end) if namespace.end is not None else None
    ))