from src.demon import TransactionsDemon, logger, LAST_BLOCK


if __name__ == '__main__':
    logger.error(f'DEMON IS STARTING')
    logger.error(f'WRITE LAST_BLOCK TO: {LAST_BLOCK}')
    TransactionsDemon().start()
