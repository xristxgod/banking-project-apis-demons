"""
This test checks the main functions of the balancer. Which access the Api and DB.
# Check everything
python -m unittest test_balancer.TestBalancer
# Check the receipt of wallets
python -m unittest test_balancer.TestBalancer.test_get_wallets
# Check receipt of private keys
python -m unittest test_balancer.TestBalancer.test_get_private_key
# Check the receipt of the balance (tokens and native) on the wallet.
python -m unittest test_balancer.TestBalancer.test_get_balance
# Check receipt of an optimal fee for a transaction.
python -m unittest test_balancer.TestBalancer.test_optimal_fee
# Create a test transaction
python -m unittest test_balancer.TestBalancer.test_create_transaction
"""
import unittest
import random
import decimal

from src_1.services.inc.get_balance import get_balance
from src_1.services.inc.get_optimal_fee import get_optimal_fee
from src_1.services.inc.send_transaction import create_transaction
from src_1.external.db import get_private_key, get_wallets

from config import AdminAddress, ReportingAddress, decimals

class TestBalancer(unittest.IsolatedAsyncioTestCase):

    tokens = ["tron_trc20_usdt", "tron_trc20_usdc", "tron"]
    test_amount = decimals.create_decimal("0.00001")

    async def test_get_wallets(self):
        wallets = await get_wallets()
        self.assertIsNot(wallets, None)
        self.assertEqual(type(wallets), list)
        self.assertIsNot(len(wallets), 0)
        self.assertIn(wallets[random.randint(0, len(wallets))][0].upper(), ["T", "4"])

    async def test_get_private_key(self):
        private_key = await get_private_key((await get_wallets())[random.randint(0, 4)])
        self.assertEqual(type(private_key), str)
        self.assertIsNot(private_key, None)

    async def test_get_balance(self):
        address = (await get_wallets())[random.randint(0, 4)]
        for token in TestBalancer.tokens:
            balance = await get_balance(address=address, token=token)
            self.assertIsNot(balance, None)
            self.assertEqual(type(balance), decimal.Decimal)

    async def test_optimal_fee(self):
        for token in TestBalancer.tokens:
            fee = await get_optimal_fee(AdminAddress, ReportingAddress, token_network=token)
            self.assertIsNot(fee, None)
            self.assertEqual(type(fee), decimal.Decimal)

    async def test_create_transaction(self):
        for token in TestBalancer.tokens:
            create = await create_transaction(AdminAddress, ReportingAddress, TestBalancer.test_amount, token)
            self.assertEqual(len(create), 6)
            self.assertNotIn("error", create)
            self.assertIn("createTxHex", create)