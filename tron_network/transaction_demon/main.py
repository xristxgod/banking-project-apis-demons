import sys
import argparse
from typing import Optional

import app
from src.schemas import Start
from config import Config, logger


class Parser:
    @staticmethod
    def create() -> Optional:
        parser = argparse.ArgumentParser()
        parser.add_argument("-b", "--blocks", default=None)
        parser.add_argument("-s", "--start", default=None)
        parser.add_argument("-e", "--end", default=None)
        parser.add_argument("-a", "--addresses", default=None)
        return parser

    @staticmethod
    async def run(data: Optional[Start] = None):
        logger.error(f"Creating daemon instance. Network: {Config.NETWORK}")
        worker = app.Daemon()
        await worker.start(data=data)


def main():
    namespace = Parser.create().parse_args(sys.argv[1:])
    Parser.run(data=Start(
        startBlock=int(namespace.start),
        endBlock=int(namespace.end),
        addresses=str(namespace.addresses).split(" "),
        listBlock=list(filter(lambda x: int(x), str(namespace.blocks).split(" ")))
    ))


if __name__ == '__main__':
    main()