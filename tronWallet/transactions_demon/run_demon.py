from src.demon import TransactionDemon
from config import logger, LAST_BLOCK
from asyncio import run

if __name__ == '__main__':
    logger.error(f"Demon is starting")
    logger.error(f"Write last block to: {LAST_BLOCK}")
    run(TransactionDemon().start())