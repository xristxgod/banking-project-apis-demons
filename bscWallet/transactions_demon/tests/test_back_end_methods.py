"""
This test is used to test UTILS.
# Check everything
python -m unittest test_back_end_methods.TestProjectMethods
# TEST SUN TO TRX
python -m unittest test_back_end_methods.TestProjectMethods.test_from_sun
# TEST HEX ADDRESS TO BASE58 ADDRESS
python -m unittest test_back_end_methods.TestProjectMethods.test_to_base58check_address
# TIMESTAMP TO DATETIME
python -m unittest test_back_end_methods.TestProjectMethods.test_convert_time
# Test get trc20 token from database
python -m unittest test_back_end_methods.TestProjectMethods.test_get_asset_trc20
# Create tx for fee
python -m unittest test_back_end_methods.TestProjectMethods.test_get_transaction_for_fee
"""
import unittest

import psycopg2.extras
from src.utils import convert_time
from config import ADMIN_ADDRESS


class TestProjectMethods(unittest.IsolatedAsyncioTestCase):
    async def test_convert_time(self):
        self.assertEqual(convert_time(1646810906), "09-03-2022 10:28:26")
        self.assertEqual(convert_time(1643682141), "01-02-2022 05:22:21")

    async def test_get_asset_trc20(self):
        usdt = await get_asset_trc20(USDT)
        usdc = await get_asset_trc20(USDC)
        self.assertEqual(type(usdt), psycopg2.extras.DictRow)
        self.assertEqual(len(usdt), 7)
        self.assertEqual(usdt["symbol"], "USDT")
        self.assertEqual(type(usdc), psycopg2.extras.DictRow)
        self.assertEqual(len(usdc), 7)
        self.assertEqual(usdc["symbol"], "USDC")

    async def test_get_transaction_for_fee(self):
        transaction = get_transaction_for_fee(
            {
                "transactions": [
                    {
                        "time": 1640995261,
                        "transactionHash": "0a026ecf22083c083e47cbea43ec40f8dfe182a82e520302c75f5a66080112620a2d7479",
                        "amount": "16.66",
                        "fee": "0.267"
                    }
                ]
            }
        )
        self.assertEqual(type(transaction), dict)
        self.assertEqual(len(transaction), 6)
        self.assertEqual(transaction["time"], 1640995261)
        self.assertEqual(
            transaction["transactionHash"],
            "0a026ecf22083c083e47cbea43ec40f8dfe182a82e520302c75f5a66080112620a2d7479"
        )
        self.assertEqual(transaction["amount"], "16.66000000")
        self.assertEqual(transaction["fee"], "0.26700000")
        self.assertEqual(transaction["recipients"], [])
        self.assertEqual(len(transaction["senders"]), 1)
        self.assertEqual(transaction["senders"][0]["address"], ReportingAddress)
        self.assertEqual(
            transaction["senders"][0]["amount"],
            "%.8f" % (decimals.create_decimal('16.66') + decimals.create_decimal("0.267"))
        )
