"""
This test checks the main functions of the balancer. By creating and sending a transaction.
!!!THE MONEY FROM THE ACCOUNT WILL BE REAL!!!
# Check everything
python -m unittest test_balancer_transaction.TestBalancerTransaction
# Create and send a test transaction from the admin to the second admin (token and native).
python -m unittest test_balancer_transaction.TestBalancerTransaction.test_create_and_send_transaction
# Create and send a test transaction from the admin to the second admin to activate the account.
python -m unittest test_balancer_transaction.TestBalancerTransaction.test_activate_account_transaction
# Create and send a test transaction from the admin to the second admin to pay the commission.
python -m unittest test_balancer_transaction.TestBalancerTransaction.test_get_transaction_for_fee
"""
import unittest

from src_1.services.helper.activate_account import activate_account
from src_1.services.helper.get_trx_for_fee import get_trx_for_fee
from src_1.services.inc.send_transaction import create_transaction, sign_send_transaction

from config import AdminAddress, AdminPrivateKey, ReportingAddress, decimals

class TestBalancerTransaction(unittest.IsolatedAsyncioTestCase):

    tokens = ["tron_trc20_usdt", "tron_trc20_usdc", "tron"]
    test_amount = decimals.create_decimal("0.00001")

    async def test_create_and_send_transaction(self):
        for token in TestBalancerTransaction.tokens:
            create = await create_transaction(AdminAddress, ReportingAddress, TestBalancerTransaction.test_amount, token)
            self.assertEqual(len(create), 6)
            self.assertNotIn("error", create)
            self.assertIn("createTxHex", create)
            sign_send = await sign_send_transaction(create["createTxHex"], AdminPrivateKey)
            self.assertEqual(sign_send, True)

    async def test_activate_account_transaction(self):
        activate = await activate_account(ReportingAddress)
        self.assertEqual(activate, True)

    def test_get_transaction_for_fee(self):
        for_fee = get_trx_for_fee(ReportingAddress, TestBalancerTransaction.test_amount)
        self.assertEqual(for_fee, True)