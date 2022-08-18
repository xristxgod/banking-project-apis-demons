"""
This test checks the operability of additional mathematical and other methods (utilities).
It also checks the operability of statuses.
# Check everything.
python -m unittest test_back_end_methods.TestProjectMethods
# Check the operability of the system status check.
python -m unittest test_back_end_methods.TestProjectMethods.test_node_status
# Check the functionality of the Tron statistics module.
python -m unittest test_back_end_methods.TestProjectMethods.test_tron_station
# Check the receipt of the token from the db.
python -m unittest test_back_end_methods.TestProjectMethods.test_token_db
# Check TRX TO SUN
python -m unittest test_back_end_methods.TestProjectMethods.test_to_sun
# Check SUN TO TRX
python -m unittest test_back_end_methods.TestProjectMethods.test_from_sun
"""
import unittest
import decimal

from src_v1.utils.station import tron_station
from src_v1.utils.token_database import token_db
from src_v1.utils.utils import from_sun, to_sun
from src_v1.utils.node_status import node_status, native_balance_status, demon_status, balancer_status

from config import AdminWallet


class TestProjectMethods(unittest.IsolatedAsyncioTestCase):

    tokens = ["USDT", "USDC"]

    async def test_node_status(self):
        self.assertTrue(node_status())
        self.assertTrue(await native_balance_status())
        self.assertTrue(demon_status())
        self.assertTrue(balancer_status())

    async def test_tron_station(self):
        energy = await tron_station.calculate_burn_energy(1)
        self.assertEqual(type(energy), decimal.Decimal)
        acc_bandwidth = await tron_station.get_account_bandwidth(AdminWallet)
        self.assertEqual(type(acc_bandwidth), dict)
        self.assertEqual(len(acc_bandwidth), 3)
        acc_energy = await tron_station.get_account_energy(AdminWallet)
        self.assertEqual(type(acc_energy), dict)
        self.assertEqual(len(acc_energy), 3)

    async def test_token_db(self):
        for token in TestProjectMethods.tokens:
            token_info = await token_db.get_token(token=token)
            self.assertEqual(type(token_info), dict)
            self.assertEqual(token_info["symbol"], token)
            self.assertEqual(len(token_info), 8)

    async def test_to_sun(self):
        self.assertEqual(to_sun(0), 0)
        self.assertEqual(to_sun(1), 1_000_000)
        self.assertEqual(to_sun(1.74), 1_740_000)
        self.assertEqual(to_sun(1.00009), 1_000_090)
        self.assertEqual(to_sun(2.06507), 2_065_070)

    async def test_from_sun(self):
        self.assertEqual(from_sun(0), 0)
        self.assertEqual(from_sun(1_000_000), 1)
        self.assertEqual(str(from_sun(1_740_000)), "1.74")
        self.assertEqual(str(from_sun(1_000_090)), "1.00009")
        self.assertEqual(str(from_sun(2_065_070)), "2.06507")
