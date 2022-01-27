import json

from tronpy.tron import Transaction

from ..schemas import BodySignAndSendTransaction
from ..transaction import get_transaction
from src.utils.node import NodeTron

class SignSendTransactions(NodeTron):
    """Sign and Send a transaction"""

    def sign_and_send_transaction(self, body: BodySignAndSendTransaction) -> json:
        """Sign and Send a transaction"""
        if isinstance(body.privateKeys, str):
            body.privateKeys = json.loads(body.privateKeys)
        # Verification of the private key
        values: dict = self.examination_transaction(privateKey=body.privateKeys[0])
        # Unpacking the original transaction data.
        raw_data = json.loads(bytes.fromhex(body.createTxHex).decode("utf-8"))
        # Signing the transaction with a private key.
        sign_transaction = Transaction(client=self.node, raw_data=raw_data).sign(priv_key=values["privateKey"])
        # Sending a transaction
        send_transaction = sign_transaction.broadcast().wait()
        # After sending, we receive the full body of the transaction (checklist)
        return get_transaction(transaction_hash=send_transaction["id"]).result()

sign_send_transaction = SignSendTransactions()