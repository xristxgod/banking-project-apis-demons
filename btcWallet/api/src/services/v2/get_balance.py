from config import decimal
from src.node import btc


def get_balance(address: str) -> dict:
    """Get balance by private_key"""
    satoshi = btc.rpc_host.get_balance(address)
    return {'balance': '%.8f' % (decimal.create_decimal(int(satoshi)) / (10 ** 8))}
