from src.demon import TransactionsDemon
from config import logger, LAST_BLOCK
from asyncio import run


if __name__ == '__main__':
    logger.error(f"DEMON IS STARTING")
    logger.error(f"WRITE LAST_BLOCK TO: {LAST_BLOCK}")
    run(TransactionsDemon().start())
