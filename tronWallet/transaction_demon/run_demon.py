from src.demon import TransactionDemon
from config import logger, network
from asyncio import run

if __name__ == '__main__':
    logger.error(f"Demon is starting. Network: {network}")
    run(TransactionDemon().start())