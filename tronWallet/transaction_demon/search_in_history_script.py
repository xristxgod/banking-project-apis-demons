import sys
import argparse
from run_demon import TransactionDemon, logger, AddressesDemon, AdminAddresses

from asyncio import run

from config import network

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--blocks", default=None)
    parser.add_argument("-s", "--start", default=0)
    parser.add_argument("-e", "--end", default=None)
    parser.add_argument("-a", "--addresses", default=None)
    return parser

async def async_run(**kwargs):
    logger.error(f"Creating demon instance. Network: {network}")
    logger.error(f"Start search in history")
    if "list_addresses" in kwargs and kwargs["list_addresses"] is not None:
        for address in kwargs.get("list_addresses"):
            if address in AdminAddresses:
                logger.error(f"This wallet: '{address}' will not be tracked")
        try:
            demon = AddressesDemon()
            is_success = await demon.start(**kwargs)
            await demon.node.close()
        except Exception:
            is_success = True
    else:
        try:
            demon = TransactionDemon()
            is_success = await demon.start(**kwargs)
            await demon.node.close()
        except Exception:
            is_success = True
    logger.info(f"Script ran success: {is_success}")

if __name__ == '__main__':
    namespace = create_parser().parse_args(sys.argv[1:])
    run(async_run(**dict(
        start_block=int(namespace.start) if namespace.start is not None else None,
        end_block=int(namespace.end) if namespace.end is not None else None,
        list_addresses=str(namespace.addresses).split(" ") if namespace.addresses is not None else None,
        list_blocks=str(namespace.blocks).split(" ") if namespace.blocks is not None else None,
    )))
