from .base import AbstractTransactionScraper
from .tron import TransactionScraper as TronTransactionScraper
from .evm import TransactionScraper as EVMTransactionScraper

from core.blockchain.models import Network, NetworkFamily


async def get_transaction_scraper(network: Network) -> AbstractTransactionScraper:
    match network.family:
        case NetworkFamily.tron:
            return TronTransactionScraper(network=network)
        case NetworkFamily.evm:
            return EVMTransactionScraper(network=network)
        case _:
            raise ValueError('Transaction scraper not found!')
