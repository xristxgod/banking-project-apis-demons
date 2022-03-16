"""
This script will run through and only create transactions, sending will not be checked.
To do this, there is: "test_send_admin_transaction.py " - to verify transactions from the admin
or "test_send_balancer_transaction.py " - to verify the transaction in the balancer.
# Check everything
python -m unittest test_api.ApiTest
# Create a test wallet
python -m unittest test_api.ApiTest.test_create_wallet
# Check the receipt of the native balance.
python -m unittest test_api.ApiTest.test_get_balance_native
# Check the receipt of the token balance.
python -m unittest test_api.ApiTest.test_get_balance_token
# Check the receipt of the optimal commission for the native transaction.
python -m unittest test_api.ApiTest.test_get_optimal_fee_native
# Check the receipt of the optimal commission for the token transaction.
python -m unittest test_api.ApiTest.test_get_optimal_fee_token
# Verify receipt of the transaction by hash.
python -m unittest test_api.ApiTest.test_get_transaction_by_hash
# Create a test transaction for the native balancer.
python -m unittest test_api.ApiTest.test_create_transaction_for_balancer_native
# Create a test transaction for the token balancer.
python -m unittest test_api.ApiTest.test_create_transaction_for_balancer_token
# Create a test transaction from a native admin wallet.
python -m unittest test_api.ApiTest.test_create_transaction_admin_native
# Create a test transaction from a token admin wallet.
python -m unittest test_api.ApiTest.test_create_transaction_admin_token
"""
import unittest
from . import _get_response
from config import API_URL, AdminWallet, ReportingAddress, AdminFee, network

if network == "mainnet":
    tx_hash = "e0f10d7fa5e51505c2b9cee233656eea208af3d42f9b0bbb630e87abf50abfb2"
elif network == "shasta":
    tx_hash = "c7c75bbbf906c87bcf4bdac1b07ec291c9ec792dfc0d09ce8d5e439b31007ad1"

class ApiTest(unittest.TestCase):
    __API_URL = API_URL

    CREATE_WALLET_URL = "{}/tron/create-wallet".format(__API_URL)
    GET_BALANCE_NATIVE = "{}/tron/get-balance/{}".format(__API_URL, AdminWallet)
    GET_BALANCE_TOKEN = [
        {"url": "{}/tron_trc20_usdt/get-balance/{}".format(__API_URL, AdminWallet), "token": "USDT"},
        {"url": "{}/tron_trc20_usdc/get-balance/{}".format(__API_URL, AdminWallet), "token": "USDC"}
    ]

    GET_OPTIMAL_FEE_NATIVE = "{}/tron/get-optimal-fee/{}&{}".format(__API_URL, AdminWallet, ReportingAddress)
    GET_OPTIMAL_FEE_TOKEN = [
        "{}/tron_trc20_usdt/get-optimal-fee/{}&{}".format(__API_URL, AdminWallet, ReportingAddress),
        "{}/tron_trc20_usdC/get-optimal-fee/{}&{}".format(__API_URL, AdminWallet, ReportingAddress),
    ]

    GET_TRANSACTION_BY_HASH = "{}/tron/get-transaction/{}".format(__API_URL, tx_hash)

    CREATE_TRANSACTION_FOR_BALANCER_NATIVE = "{}/tron/create-transaction-for-internal-services".format(__API_URL)
    CREATE_TRANSACTION_FOR_BALANCER_TOKEN = [
        "{}/tron_trc20_usdt/create-transaction-for-internal-services".format(__API_URL),
        "{}/tron_trc20_usdc/create-transaction-for-internal-services".format(__API_URL)
    ]

    CREATE_TRANSACTION_ADMIN_NATIVE = "{}/tron/create-transaction".format(__API_URL)
    CREATE_TRANSACTION_ADMIN_TOKEN = [
        "{}/tron_trc20_usdt/create-transaction".format(__API_URL),
        "{}/tron_trc20_usdc/create-transaction".format(__API_URL),
    ]

    # <<<------------------------------------>>> Wallet <<<---------------------------------------------------------->>>

    def test_create_wallet(self):
        response = _get_response("POST", ApiTest.CREATE_WALLET_URL, {"words": "tests"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)
        self.assertNotIn("error", response.json())
        self.assertEqual(response.json().get("words"), "tests")
        self.assertEqual(
            response.json().get("privateKey"),
            "59830ebc3a4184110566bf1a290d08473dfdcbd492ce498b14cd1a5e2fa2e441"
        )
        self.assertEqual(
            response.json().get("publicKey"),
            "678e108eff94e584b67fe0b62ecb112d649b0ecf28fcbebc843b4b49258d57c6aac611ac0f93cf6c7e9bbd9cf683c5dd8274852313338f09bd2603005f05f234"
        )
        self.assertEqual(
            response.json().get("address"),
            "T9ytHnnZXJS8Rz7Em79kSrTKhjtoQF3ZrY"
        )

    def test_get_balance_native(self):
        response = _get_response("GET", ApiTest.GET_BALANCE_NATIVE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertIn("balance", response.json())
        self.assertNotIn("error", response.json())

    def test_get_balance_token(self):
        for dict_url in ApiTest.GET_BALANCE_TOKEN:
            response = _get_response("GET", dict_url["url"])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 2)
            self.assertIn("balance", response.json())
            self.assertIn("token", response.json())
            self.assertEqual(response.json().get("token").upper(), dict_url["token"])
            self.assertNotIn("error", response.json())

    # <<<------------------------------------>>> Transaction Fee <<<------------------------------------------------->>>

    def test_get_optimal_fee_native(self):
        response = _get_response("GET", ApiTest.GET_OPTIMAL_FEE_NATIVE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        self.assertNotIn("error", response.json())

    def test_get_optimal_fee_token(self):
        for url in ApiTest.GET_OPTIMAL_FEE_TOKEN:
            response = _get_response("GET", url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 3)
            self.assertNotIn("error", response.json())

    # <<<------------------------------------>>> Transaction Info <<<------------------------------------------------>>>

    def test_get_transaction_by_hash(self):
        response = _get_response("GET", ApiTest.GET_TRANSACTION_BY_HASH)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["transactionHash"], tx_hash)
        self.assertEqual(response.json()[0]["time"], 1646126333056)
        self.assertNotIn("error", response.json())

    # <<<------------------------------------>>> Transaction <<<----------------------------------------------------->>>

    def test_create_transaction_for_balancer_native(self):
        response = _get_response("POST", ApiTest.CREATE_TRANSACTION_FOR_BALANCER_NATIVE, {
            "fromAddress": AdminWallet,
            "outputs": [
                {ReportingAddress: "0.000001"}
            ]
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 6)
        self.assertNotIn("error", response.json())
        self.assertIn("createTxHex", response.json())

    def test_create_transaction_for_balancer_token(self):
        for url in ApiTest.CREATE_TRANSACTION_FOR_BALANCER_TOKEN:
            response = _get_response("POST", url, {
                "fromAddress": AdminWallet,
                "outputs": [
                    {ReportingAddress: "0.000001"}
                ]
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 6)
            self.assertNotIn("error", response.json())
            self.assertIn("createTxHex", response.json())

    # <<<------------------------------------>>> Admin Transaction <<<----------------------------------------------->>>

    def test_create_transaction_admin_native(self):
        response = _get_response("POST", ApiTest.CREATE_TRANSACTION_ADMIN_NATIVE, {
            "outputs": [
                {"TPvxLpLeC1Rd13CymBVWnXJiURjWk3SfRx": "0.000001"}
            ],
            "adminAddress": ReportingAddress,
            "adminFee": AdminFee
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 6)
        self.assertNotIn("error", response.json())
        self.assertIn("createTxHex", response.json())

    def test_create_transaction_admin_token(self):
        for url in ApiTest.CREATE_TRANSACTION_ADMIN_TOKEN:
            response = _get_response("POST", url, {
                "outputs": [
                    {"TPvxLpLeC1Rd13CymBVWnXJiURjWk3SfRx": "0.000001"}
                ],
                "adminAddress": ReportingAddress,
                "adminFee": AdminFee
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 6)
            self.assertNotIn("error", response.json())
            self.assertIn("createTxHex", response.json())