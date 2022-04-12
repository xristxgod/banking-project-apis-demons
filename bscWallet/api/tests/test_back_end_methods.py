"""
This test checks the operability of additional mathematical and other methods (utilities).
It also checks the operability of statuses.
# Check everything.
python -m unittest test_back_end_methods.TestProjectMethods
# Check the operability of the system status check.
python -m unittest test_back_end_methods.TestProjectMethods.test_node_status
# Check the receipt of the token from the db.
python -m unittest test_back_end_methods.TestProjectMethods.test_token_db
"""
import unittest
from src.utils.tokens_database import TokenDB
from src.utils.node_status import is_native
from src.v1.services.is_balancer_alive import is_balancer_alive
from src.v1.services.is_demon_alive import is_demon_alive
from src.v1.services.wallet_eth import wallet_bsc


class TestProjectMethods(unittest.IsolatedAsyncioTestCase):
    tokens = ["USDT", "USDC"]

    async def test_node_status(self):
        self.assertTrue(await wallet_bsc.node_bridge.is_connect())
        self.assertTrue(await is_balancer_alive())
        self.assertTrue(await is_demon_alive())
        self.assertTrue(await is_native())

    async def test_token_db(self):
        for token in TestProjectMethods.tokens:
            token_info = await TokenDB.get_token(symbol=token)
            self.assertEqual(type(token_info), dict)
            self.assertEqual(token_info["symbol"], token)
            self.assertEqual(len(token_info), 8)
