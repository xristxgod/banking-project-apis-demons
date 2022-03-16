import json

from tronpy.tron import Transaction, PrivateKey

from src.v1.schemas import BodySignAndSendTransaction
from src.utils.utils import timer
from src.v1.transaction import transaction_parser
from src.utils.node import NodeTron

@timer
async def sign_and_send_transaction(body: BodySignAndSendTransaction) -> json:
    """Sign and Send a transaction"""
    # Verification of the private key
    private_key = PrivateKey(private_key_bytes=bytes.fromhex(body.privateKeys[0]))
    # Unpacking the original transaction data.
    raw_data = json.loads(bytes.fromhex(body.createTxHex).decode("utf-8"))
    # Signing the transaction with a private key.
    sign_transaction = Transaction(client=NodeTron().node, raw_data=raw_data).sign(priv_key=private_key)
    # Sending a transaction
    send_transaction = sign_transaction.broadcast().wait()
    # After sending, we receive the full body of the transaction (checklist)
    result = await transaction_parser.get_transaction(transaction_hash=send_transaction["id"])
    return result[0]
