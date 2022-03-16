"""
READ ME!!!
When you run this script, a transaction will be sent, and I will withdraw money from the account.
TRX will go to pay the commission, without enthusiasm. So, before you start, think twice.
In this case (test_send_admin_transaction.py ) the money will be withdrawn from the central wallet.
They will go to the specified wallet (if not specified, then to "TRzfVw3rgezwYCfeSxJPr9qdG6pMGegTNY").
# Check everything.
python -m unittest test_send_admin_transaction.ApiTestAdminTransaction
# Create and send a test transaction from the native admin wallet.
python -m unittest test_send_admin_transaction.ApiTestAdminTransaction.test_send_transaction_admin_native
# Create and send a test transaction from the token admin wallet.
python -m unittest test_send_admin_transaction.ApiTestAdminTransaction.test_send_transaction_admin_token
"""
import unittest
from . import _get_response
from config import API_URL, ReportingAddress, AdminFee, AdminFeeToken

# Enter the recipient's address and private key. Otherwise, the recipients will be "TRzfVw3rgezwYCfeSxJPr9qdG6pMGegTNY".
test_to_address = None

class ApiTestAdminTransaction(unittest.TestCase):
    __API_URL = API_URL

    CREATE_TRANSACTION_ADMIN_NATIVE = "{}/tron/create-transaction".format(__API_URL)
    CREATE_TRANSACTION_ADMIN_TOKEN = [
        {"url": "{}/tron_trc20_usdt/create-transaction".format(__API_URL), "token": "USDT"},
        {"url": "{}/tron_trc20_usdc/create-transaction".format(__API_URL), "token": "USDC"}
    ]
    SIGN_SEND_TRANSACTION_ADMIN = "{}/tron/sign-send-transaction".format(__API_URL)

    def test_send_transaction_admin_native(self):
        """
        This test creates and poisons a test transaction (NATIVE)
        """
        create_transaction = _get_response("POST", ApiTestAdminTransaction.CREATE_TRANSACTION_ADMIN_NATIVE, {
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
        sign_send_transaction = _get_response("POST", ApiTestAdminTransaction.SIGN_SEND_TRANSACTION_ADMIN, {
            "createTxHex": create_transaction.json().get("createTxHex"),
            "maxFeeRate": create_transaction.json().get("maxFeeRate")
        })
        self.assertEqual(sign_send_transaction.status_code, 200)
        self.assertNotIn("error", sign_send_transaction.json())
        self.assertIn("transactionHash", sign_send_transaction.json())
        print(f"TRX | TX: {sign_send_transaction.json().get('transactionHash')}")

    def test_send_transaction_admin_token(self):
        """
        This test creates and poisons a test transaction (TOKEN)
        """
        for dict_url in ApiTestAdminTransaction.CREATE_TRANSACTION_ADMIN_TOKEN:
            create_transaction = _get_response("POST", dict_url["url"], {
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
            sign_send_transaction = _get_response("POST", ApiTestAdminTransaction.SIGN_SEND_TRANSACTION_ADMIN, {
                "createTxHex": create_transaction.json().get("createTxHex"),
                "maxFeeRate": create_transaction.json().get("maxFeeRate")
            })
            self.assertEqual(sign_send_transaction.status_code, 200)
            self.assertNotIn("error", sign_send_transaction.json())
            self.assertIn("transactionHash", sign_send_transaction.json())
            print(f"Token: {dict_url['token']} | TX: {sign_send_transaction.json().get('transactionHash')}")