"""
This test is used to check the operability of the database and the method of accessing it.
# Check everything
python -m unittest test_demon.TestDemon
# Check receipt of all addresses
python -m unittest test_demon.TestDemon.test_get_addresses
# Check receipt of all transaction hash
python -m unittest test_demon.TestDemon.test_get_all_transactions_hash
# Check receipt of all tokens from the database
python -m unittest test_demon.TestDemon.test_get_contracts
"""
import unittest
import random

from src.external_data.database import get_addresses, get_all_transactions_hash, get_contracts, get_transaction_hash


class TestDemon(unittest.IsolatedAsyncioTestCase):

    async def test_get_addresses(self):
        addresses = await get_addresses()
        self.assertEqual(type(addresses), list)
        self.assertIsNot(addresses, [])
        self.assertIsNotNone(addresses)
        self.assertIn(addresses[random.randint(0, len(addresses))][0].upper(), ["T", "4"])

    async def test_get_all_transactions_hash(self):
        tx_hash = await get_all_transactions_hash()
        self.assertIsNotNone(tx_hash)
        self.assertEqual(type(tx_hash), list)
        if len(tx_hash) > 0:
            tx = get_transaction_hash(transaction_hash=tx_hash[0])
            self.assertEqual(type(tx), dict)

    def test_get_contracts(self):
        contracts = get_contracts()
        self.assertEqual(type(contracts), list)
        for contract in contracts:
            self.assertIn(contract["symbol"], ["USDT", "USDC"])
