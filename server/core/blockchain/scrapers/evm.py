from core.blockchain.scrapers.base import AbstractTransactionScraper


class TransactionScraper(AbstractTransactionScraper):
    async def scrape_transaction(self, transaction: dict, search_data: dict):
        pass
