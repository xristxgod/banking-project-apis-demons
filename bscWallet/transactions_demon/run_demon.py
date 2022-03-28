from src.demon import TransactionsDemon
from asyncio import run


if __name__ == '__main__':
    run(TransactionsDemon().start())
