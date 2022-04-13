from unittest import IsolatedAsyncioTestCase
from src.external_data.database import DB


class TestDemon(IsolatedAsyncioTestCase):
    async def test_get_addresses(self):
        addresses = await DB.get_addresses()
        assert isinstance(addresses, list)

    async def test_get_all_transactions_hash(self):
        tx_hash = await DB.get_all_transactions_hash()
        assert tx_hash is not None
        assert isinstance(tx_hash, list)

    def test_get_contracts(self):
        contracts = DB.get_tokens()
        assert isinstance(contracts, list)
