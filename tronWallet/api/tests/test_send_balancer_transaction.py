"""
READ ME!!!
When you run this script, a transaction will be sent, and I will withdraw money from the account.
TRX will go to pay the commission, without enthusiasm. So, before you start, think twice.
In this case (test_send_balancer_transaction.py ) the money will go from the specified address
(if it is not specified, then from the central one) to the specified wallet
(if not specified, then to "TRzfVw3rgezwYCfeSxJPr9qdG6pMGegTNY").
# Check everything.
python -m unittest test_send_balancer_transaction.ApiTestBalancerTransaction
# Create and send a test transaction for the native balancer.
python -m unittest test_send_balancer_transaction.ApiTestBalancerTransaction.test_send_transaction_for_balancer_native
# Create and send a test transaction for the token balancer.
python -m unittest test_send_balancer_transaction.ApiTestBalancerTransaction.test_send_transaction_for_balancer_token
"""
import unittest
from . import _get_response
from config import API_URL, AdminWallet, ReportingAddress, AdminFee, AdminPrivateKey, AdminFeeToken


# Enter the sender's address and private key. Otherwise, the Admin address and private key will be used.
test_from_address = None
test_from_private_key = None
# Enter the recipient's address and private key. Otherwise, the recipients will be "TRzfVw3rgezwYCfeSxJPr9qdG6pMGegTNY".
test_to_address = None


class ApiTestBalancerTransaction(unittest.TestCase):

    __API_URL = API_URL

    CREATE_TRANSACTION_FOR_BALANCER_NATIVE = "{}/tron/create-transaction-for-internal-services".format(__API_URL)
    CREATE_TRANSACTION_FOR_BALANCER_TOKEN = [
        {"url": "{}/tron_trc20_usdt/create-transaction-for-internal-services".format(__API_URL), "token": "USDT"},
        {"url": "{}/tron_trc20_usdc/create-transaction-for-internal-services".format(__API_URL), "token": "USDC"}
    ]
    SIGN_SEND_TRANSACTION_FOR_BALANCER = "{}/tron/sign-send-transaction-for-internal-services".format(__API_URL)

    def test_send_transaction_for_balancer_native(self):
        """
        This test creates and poisons a test transaction (NATIVE)
        """
        create_transaction = _get_response("POST", ApiTestBalancerTransaction.CREATE_TRANSACTION_FOR_BALANCER_NATIVE, {
            "fromAddress": test_from_address if test_from_address is not None else AdminWallet,
            "outputs": [
                {test_to_address if test_to_address is not None else "TRzfVw3rgezwYCfeSxJPr9qdG6pMGegTNY": "0.000001"}
            ],
            "adminAddress": ReportingAddress,
            "adminFee": AdminFee
        })
        self.assertEqual(create_transaction.status_code, 200)
        self.assertEqual(len(create_transaction.json()), 6)
        self.assertNotIn("error", create_transaction.json())
        self.assertIn("createTxHex", create_transaction.json())
        sign_send_transaction = _get_response("POST", ApiTestBalancerTransaction.SIGN_SEND_TRANSACTION_FOR_BALANCER, {
            "createTxHex": create_transaction.json().get("createTxHex"),
            "privateKeys": [
                test_from_private_key if test_from_private_key is not None else AdminPrivateKey
            ],
            "maxFeeRate": create_transaction.json().get("maxFeeRate")
        })
        self.assertEqual(sign_send_transaction.status_code, 200)
        self.assertNotIn("error", sign_send_transaction.json())
        self.assertIn("transactionHash", sign_send_transaction.json())
        print(f"TRX | TX: {sign_send_transaction.json().get('transactionHash')}")

    def test_send_transaction_for_balancer_token(self):
        """
        This test creates and poisons a test transaction (TOKEN)
        """
        for dict_url in ApiTestBalancerTransaction.CREATE_TRANSACTION_FOR_BALANCER_TOKEN:
            create_transaction = _get_response("POST", dict_url["url"], {
                "fromAddress": test_from_address if test_from_address is not None else AdminWallet,
                "outputs": [
                    {
                        test_to_address if test_to_address is not None else "TRzfVw3rgezwYCfeSxJPr9qdG6pMGegTNY": "0.00001"
                    }
                ],
                "adminAddress": ReportingAddress,
                "adminFee": AdminFeeToken
            })
            self.assertEqual(create_transaction.status_code, 200)
            self.assertEqual(len(create_transaction.json()), 6)
            self.assertNotIn("error", create_transaction.json())
            self.assertIn("createTxHex", create_transaction.json())
            sign_send_transaction = _get_response(
                "POST", ApiTestBalancerTransaction.SIGN_SEND_TRANSACTION_FOR_BALANCER,
                {
                    "createTxHex": create_transaction.json().get("createTxHex"),
                    "privateKeys": [
                        test_from_private_key if test_from_private_key is not None else AdminPrivateKey
                    ],
                    "maxFeeRate": create_transaction.json().get("maxFeeRate")
                })
            self.assertEqual(sign_send_transaction.status_code, 200)
            self.assertNotIn("error", sign_send_transaction.json())
            self.assertIn("transactionHash", sign_send_transaction.json())
            print(f"Token: {dict_url['token']} | TX: {sign_send_transaction.json().get('transactionHash')}")
