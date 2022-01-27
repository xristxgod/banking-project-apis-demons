from config import logger, decimal
from src.node import btc


def get_balance(address: str) -> dict:
    """Get balance by private_key"""
    satoshi = btc.rpc_host.get_balance(address)
    logger.error(f'BALANCE: {satoshi}')
    return {'balance': '%.8f' % (decimal.create_decimal(int(satoshi)) / (10 ** 8))}
