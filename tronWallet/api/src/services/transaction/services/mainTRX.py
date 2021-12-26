import json
from decimal import Decimal

import requests
import requests.exceptions

import tronpy.exceptions
from tronpy.tron import Transaction, PrivateKey

from api.src.services.transaction.schemas import (
    BodyCreateTransaction, ResponseCreateTransaction, BodySignAndSendTransaction,
    ResponseTransactions, ResponseGetFeeLimit
)
from api.src.node.node import NodeTron
from api.src.utils.tron_typing import TransactionHash, TronAccountAddress

class TRXTransaction(NodeTron):
    """This class creates, signs and sends TRX transactions"""
    def create_transaction(self, body: BodyCreateTransaction) -> ResponseCreateTransaction:
        """Create a transaction TRX"""
        try:
            # Checks the correctness of the data entered by users
            values: dict = self.examination_transaction(
                fromAddress=body.fromAddress,
                toAddress=body.toAddress,
                amount=body.amount
            )
        except Exception as error:
            raise error

        try:
            # Checks whether there are funds on the user's balance for transfer
            if self.toSun(self.node.get_account_balance(body.fromAddress)) < values["amount"]:
                raise Exception("You don't have enough funds on your balance to transfer!!")
            message = "1.You have about 2-5 minutes to sign and send the order. Otherwise, it will be deleted!!!"
            # Creates a transaction
            create_transaction = self.node.trx.transfer(
                from_=values["fromAddress"],
                to=values["toAddress"],
                amount=values["amount"]
            )
            # Receives account resources to generate a commission
            resource = self.node.get_account_resource(addr=values["fromAddress"])
            # If the user does not have enough bandwidth, a fixed transaction fee will be charged
            if "freeNetUsed" in resource and resource["freeNetLimit"] - resource["freeNetUsed"] < 267:
                message += " 2.Your account has run out of bandwidth, from that moment you will be charged a commission" \
                           " for each TRX and TRC10 transaction in the amount of 0.267 TRX. To make transactions free" \
                           " again, freeze silent TRX for 'BANDWIDTH'."
                # Setting a commission for a transaction, in the amount of 0.267 TRX
                create_transaction = create_transaction.fee_limit(267_000)
            # Build a transaction
            create_transaction = create_transaction.build()
            return ResponseCreateTransaction(
                # The original transaction data for signing and sending the transaction
                createTxHex=json.dumps(create_transaction.to_json()["raw_data"]).encode("utf-8").hex(),
                # The body of the transaction, you can find out all the details from it
                bodyTransaction=create_transaction.to_json(),
                message=message
            )
        except Exception as error:
            raise error

    def sign_send_transaction(self, body: BodySignAndSendTransaction) -> ResponseTransactions:
        """Sign and Send a transaction"""
        try:
            # Verification of the private key
            if isinstance(body.privateKey, str):
                # Private key HAX to Private key BYTES
                private_key = PrivateKey(private_key_bytes=bytes.fromhex(body.privateKey))
            else:
                # If the private key was already BYTES
                private_key = PrivateKey(private_key_bytes=body.privateKey)
        except tronpy.exceptions.BadKey as error:
            raise RuntimeError(str(error))

        try:
            # Unpacking the original transaction data.
            raw_data = json.loads(bytes.fromhex(body.createTxHex).decode("utf-8"))
            # Signing the transaction with a private key.
            sign_transaction = Transaction(client=self.node, raw_data=raw_data).sign(priv_key=private_key)
            # Sending a transaction
            send_transaction = sign_transaction.broadcast().wait()
            # After sending, we receive the full body of the transaction (checklist)
            trx_body = self.get_transaction(trxHash=send_transaction["id"])
            trx = dict(
                blockNumber=trx_body["blockNumber"],
                timestamp=trx_body["timestamp"],
                datetime=trx_body["datetime"],
                transactionHash=trx_body["transactionHash"],
                transactionType=trx_body["transactionType"],
                amount=trx_body["amount"],
                fee=trx_body["fee"],
                senders=trx_body["from"],
            )

            if "to" in trx_body:
                trx["recipients"] = trx_body["to"]
            else:
                trx["recipients"] = trx_body["resource"]

            if "token" in trx_body:
                trx["token"] = trx_body["token"]
            return ResponseTransactions(**trx)
        except Exception as error:
            raise error

    def get_transaction(self, trxHash: TransactionHash) -> json:
        """Returns information about the transaction"""
        trx_body = self.node.get_transaction(txn_id=trxHash)
        trx_info = self.node.get_transaction_info(txn_id=trxHash)
        try:
            value = trx_body["raw_data"]["contract"][0]["parameter"]["value"]

            txn = {
                "blockNumber": trx_info["blockNumber"],
                "transactionHash": trx_body["txID"],
                "fee": str(NodeTron().fromSun(trx_info["fee"])) if "fee" in trx_info else "0",
                "transactionType": trx_body["raw_data"]["contract"][0]["type"],
                "from": value["owner_address"]
            }
            if "timestamp" in trx_body["raw_data"]:
                txn["timestamp"] = trx_body["raw_data"]["timestamp"]
                txn["datetime"] = NodeTron().convertTime(int(str(txn["timestamp"])[:10]))
            elif "blockTimeStamp" in trx_info:
                txn["timestamp"] = trx_info["blockTimeStamp"]
                txn["datetime"] = NodeTron().convertTime(int(str(txn["timestamp"])[:10]))
            else:
                txn["timestamp"] = 0
                txn["datetime"] = ""


            if txn["transactionType"] in ["TransferContract", "TransferAssetContract"]:
                txn_value = {
                    "to": value["to_address"],
                    "amount": str(NodeTron().fromSun(value["amount"])),
                }
                if "asset_name" in value:
                    asset = self.node.get_asset(value["asset_name"])
                    txn_value["token"] = f"{asset['name']} ({asset['abbr']})"
            elif txn["transactionType"] == "TriggerSmartContract":
                try:
                    contract = self.connect_to_contract(value["contract_address"])
                    data = value["data"]
                    amount = Decimal(value=int("0x" + data[72:], 0) / 10 ** int(contract.functions.decimals()))
                    txn_value = {
                        "to": self.node.to_base58check_address("41" + data[32:72]),
                        "amount": str(round(amount, 8)),
                        "token": f"{contract.name} ({contract.functions.symbol()})"
                    }
                except Exception:
                    txn_value = {
                        "data": value["data"],
                        "contractAddress": value["contract_address"]
                    }
            elif txn["transactionType"] in ["FreezeBalanceContract", "UnfreezeBalanceContract"]:
                txn_value = {}

                if "resource" in value:
                    txn_value["resource"] = value["resource"]
                else:
                    txn_value["resource"] = "BANDWIDTH"

                if "frozen_balance" in value:
                    txn_value["amount"] = value["frozen_balance"]
                if "receiver_address" in value:
                    txn_value["to"] = value["receiver_address"]
            else:
                txn_value = {}
            return {**txn, **txn_value}
        except tronpy.exceptions.BadKey as error:
            return {"error": str(error)}
        except tronpy.exceptions.TransactionNotFound as error:
            return {"error": str(error)}

    def get_all_transactions(self, address: TronAccountAddress) -> json:
        """Get all transactions by address"""
        if not self.node.is_address(address):
            raise Exception(f"This address '{address}' was not found in the Tron system.")

        url_trx_and_trc10 = f"https://api.trongrid.io/v1/accounts/{address}/transactions"
        url_trc20 = url_trx_and_trc10 + "/trc20"
        headers = {
            "Accept": "application/json",
            "TRON-PRO-API-KEY": "a684fa6d-6893-4928-9f8e-8decd5f034f2"
        }
        transactions = []
        try:
            response_trx_and_trc10 = requests.get(url_trx_and_trc10, headers=headers).json()["data"]
            response_trc20 = requests.get(url_trc20, headers=headers).json()["data"]
            for transaction in response_trx_and_trc10:
                transactions.append(TRXTransaction().get_transaction(trxHash=transaction["txID"]))
            for transaction_trc20 in response_trc20:
                transactions.append(TRXTransaction().get_transaction(trxHash=transaction_trc20["transaction_id"]))
            return transactions
        except Exception as error:
            return {"error": str(error)}

    def get_received_or_send_or_fee(self, address: TronAccountAddress) -> dict:
        """Get all sent TRX, received TRX and given to the TRX commission"""
        if not self.node.is_address(address):
            raise Exception(f"This address '{address}' was not found in the Tron system.")
        transactions = self.get_all_transactions(address=address)
        received, send, fee = 0, 0, 0
        for txn in transactions:
            if float(txn["fee"]) > 0:
                fee += float(txn["fee"])
            if txn["transactionType"] not in ["TransferContract", "TransferAssetContract"]:
                continue

            if txn["from"] == address:
                send += float(txn["amount"])
            elif txn["to"] == address:
                received += float(txn["amount"])

        return {
            "totalReceived": str(round(Decimal(value=received), 8)),
            "totalSend": str(round(Decimal(value=send), 8)),
            "totalFee": str(round(Decimal(value=fee), 8)),
        }

    def get_fee_limit(
            self,
            from_address: TronAccountAddress
    ) -> ResponseGetFeeLimit:
        """Get transaction fees"""
        if not self.node.is_address(from_address):
            raise Exception("Address not found in the Tron system!")
        resource = self.node.get_account_resource(addr=from_address)
        if "freeNetUsed" not in resource or resource["freeNetLimit"] - resource["freeNetUsed"] > 267:
            return ResponseGetFeeLimit(feeTRX="0")
        return ResponseGetFeeLimit(feeTRX="0.267")


transaction_trx = TRXTransaction()