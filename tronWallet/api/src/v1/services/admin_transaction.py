import json
from typing import Dict

from tronpy.tron import Transaction, PrivateKey

from src.v1.schemas import BodySignAndSendTransaction, ResponseCreateTransaction, BodyCreateTransaction
from src.v1.transaction import get_txn, transaction_parser
from src.v1.services.create_transaction import create_transaction
from src.utils.node import NodeTron
from src.utils.types import TokenTRC20
from config import AdminPrivateKey, AdminWallet, decimals, ReportingAddress


class AdminTransaction(NodeTron):

    # <<<-------------------------------->>> Create admin transaction <<<-------------------------------------------->>>

    async def create_admin_transaction(self, body: BodyCreateTransaction) -> ResponseCreateTransaction:
        """Create a transaction TRX"""
        to_address, to_amount = list(body.outputs[0].items())[0]
        amount = self.toSun(float(to_amount))
        # Resources that will go to the transaction
        resources = await create_transaction.get_optimal_fee(from_address=AdminWallet, to_address=to_address)
        # Creates and build a transaction
        txn = self.node.trx.transfer(from_=AdminWallet, to=to_address, amount=amount).build()
        create_tx_hex = json.dumps({
            "rawData": txn.to_json()["raw_data"],
            "adminFee": body.adminFee,
            "adminAddress": body.adminAddress
        }).encode("utf-8").hex()
        json_body = txn.to_json()
        json_body["raw_data"]["contract"][0]["parameter"]["value"]["owner_address"] = self.node.to_hex_address(
            body.fromAddress if body.fromAddress != "string" and body.fromAddress is not None else AdminWallet
        )
        return ResponseCreateTransaction(
            # The original transaction data for signing and sending the transaction
            createTxHex=create_tx_hex,
            # The body of the transaction, you can find out all the details from it
            bodyTransaction=json_body,
            # Transaction fee
            fee=resources["fee"],
            # Energy cost per transaction.
            energy=resources["energy"],
            # Bandwidth cost per transaction.
            bandwidth=resources["bandwidth"],
            # The maximum allowable commission per transaction
            maxFeeRate="%.8f" % (decimals.create_decimal(resources["fee"]) * 2) if float(resources["fee"]) > 0 else 0
        )

    async def create_trc20_admin_transactions(self, body: BodyCreateTransaction, token: TokenTRC20) -> ResponseCreateTransaction:
        """Create a transaction TRC20"""
        to_address, to_amount = list(body.outputs[0].items())[0]
        # Token information
        token_dict = await self.db.get_token(token=token)
        # Connecting to a smart contract
        contract = self.node.get_contract(addr=token_dict["address"])
        # Let's get the amount for the offspring in decimal
        amount = int(float(to_amount) * 10 ** int(token_dict["decimal"]))
        # Checks whether the user has a tokens balance to transfer
        if contract.functions.balanceOf(AdminWallet) * 10 ** int(token_dict["decimal"]) < amount:
            raise Exception("You do not have enough funds on your balance to make a transaction!!!")
        resources = await create_transaction.get_optimal_fee(from_address=AdminWallet, to_address=to_address, token=token)
        # Creating a transaction
        txn = contract.functions.transfer(to_address, amount).with_owner(AdminWallet).build()
        create_tx_hex = json.dumps({
            "rawData": txn.to_json()["raw_data"],
            "adminFee": body.adminFee,
            "adminAddress": body.adminAddress
        }).encode("utf-8").hex()
        json_body = txn.to_json()
        json_body["raw_data"]["contract"][0]["parameter"]["value"]["owner_address"] = self.node.to_hex_address(
            body.fromAddress if body.fromAddress != "string" and body.fromAddress is not None else AdminWallet
        )
        return ResponseCreateTransaction(
            # The original transaction data for signing and sending the transaction
            createTxHex=create_tx_hex,
            # The body of the transaction, you can find out all the details from it
            bodyTransaction=json_body,
            # Transaction fee
            fee=resources["fee"],
            # Energy cost per transaction.
            energy=resources["energy"],
            # Bandwidth cost per transaction.
            bandwidth=resources["bandwidth"],
            # The maximum allowable commission per transaction
            maxFeeRate=token_dict["feeLimit"]
        )

    # <<<-------------------------------->>> Sign and send admin transaction <<<------------------------------------->>>

    async def sign_send_admin_transaction(self, body: BodySignAndSendTransaction) -> json:
        admin_private_key = PrivateKey(private_key_bytes=bytes.fromhex(AdminPrivateKey))
        user_address = PrivateKey(
            private_key_bytes=bytes.fromhex(body.privateKeys[0])
        ).public_key.to_base58check_address() if len(body.privateKeys[0]) != 0 and body.privateKeys[0] != "string" \
            else ReportingAddress
        # Unpacking the original transaction data.
        data: Dict = json.loads(bytes.fromhex(body.createTxHex).decode("utf-8"))
        raw_data = data["rawData"]
        admin_fee = decimals.create_decimal(data["adminFee"])
        reporting_address = data["adminAddress"]
        # Signing the transaction with a private key.
        sign_transaction = Transaction(client=self.node, raw_data=raw_data).sign(priv_key=admin_private_key)
        sign_transaction.broadcast().wait()
        # # After sending, we receive the full body of the transaction (checklist)
        result = await transaction_parser.get_transaction(transaction_hash=sign_transaction.txid)
        return get_txn(
            tnx=result[0],
            tnx_type=result[0]["transactionType"],
            user=user_address,
            admin_fee=admin_fee,
            reporter=reporting_address
        )


admin_transaction = AdminTransaction()
