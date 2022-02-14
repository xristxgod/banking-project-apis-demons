import json
import asyncio
import requests
from decimal import Decimal
from typing import List, Dict

from src.utils.node import NodeTron
from src.utils.types import TransactionHash, TronAccountAddress, ContractAddress
from config import decimals, network

class TransactionParser(NodeTron):

    async def get_transaction(self, transaction_hash: TransactionHash):
        return await self.__get_transactions(transactions=[await self.async_node.get_transaction(txn_id=transaction_hash)])

    async def get_all_transactions(self, address: TronAccountAddress) -> json:
        """Get all transactions by address"""
        url = "" if network == "mainnet" else f"{network.lower()}."
        url_trx_and_trc10 = f"https://api.{url}trongrid.io/v1/accounts/{address}/transactions"
        headers = {
            "Accept": "application/json",
            "TRON-PRO-API-KEY": "a684fa6d-6893-4928-9f8e-8decd5f034f2"
        }
        transactions = requests.get(url_trx_and_trc10, headers=headers).json()["data"]
        return await self.__get_transactions(transactions=transactions)

    async def __get_transactions(self, transactions: List) -> List:
        """Get all transactions by address"""
        fund_trx_for_send = []
        list_transactions = await asyncio.gather(*[
            self.__processing_transactions(
                transactions=transactions[right_border: (right_border + 1)]
            )
            for right_border in range(len(transactions))
        ])
        for transactions in list_transactions:
            fund_trx_for_send.extend(transactions)
        return fund_trx_for_send

    async def __processing_transactions(self, transactions: dict) -> list:
        """
        Unpacking transactions and checking for the presence of required addresses in them
        :param transactions: Set of transactions
        """
        funded_trx_for_sending = []
        for txn in transactions:
            txn_type = txn["raw_data"]["contract"][0]["type"]
            funded_trx_for_sending.append(
                await self.__packaging_for_dispatch(
                    txn=txn,
                    txn_type=txn_type,
                )
            )
        return funded_trx_for_sending

    async def __packaging_for_dispatch(self, txn: dict, txn_type: str) -> dict:
        """
        Packaging the necessary transaction to send
        :param txn: Transaction
        :param txn_type: Transaction type
        """
        try:
            txn_values = txn["raw_data"]["contract"][0]['parameter']["value"]

            fee = 0
            if "fee_limit" in txn["raw_data"]:
                try:
                    fee_limit = await self.async_node.get_transaction_info(txn["txID"])
                    if "fee" not in fee_limit:
                        raise Exception
                    fee = "%.8f" % decimals.create_decimal(self.fromSun(fee_limit["fee"]))
                except Exception:
                    fee = 0
            values = {
                "time": txn["raw_data"]["timestamp"] if "timestamp" in txn["raw_data"] else "",
                "datetime": self.convertTime(int(str(txn["raw_data"]["timestamp"])[:10])) if "timestamp" in txn["raw_data"] else "",
                "transactionHash": txn["txID"],
                "transactionType": txn_type,
                "fee": fee,
                "amount": 0,
                "senders": [
                    {
                        "address": self.node.to_base58check_address(txn_values["owner_address"])
                    }
                ],
                "recipients": []
            }
            # TRX or TRC10
            if txn_type in ["TransferContract", "TransferAssetContract"]:
                amount = "%.8f" % decimals.create_decimal(self.fromSun(txn_values["amount"]))
                values["amount"] = amount
                values["recipients"] = [{
                    "address": self.node.to_base58check_address(txn_values["to_address"]),
                    "amount": amount
                }]
                values["senders"][0]["amount"] = amount
                if "asset_name" in txn_values:
                    values["token"] = self.node.get_asset(id=txn_values["asset_name"])
            # TRC20
            elif txn_type == "TriggerSmartContract":
                smart_contract = await self.__smart_contract_transaction(
                    data=txn_values["data"], contract_address=txn_values["contract_address"]
                )
                if "data" in smart_contract:
                    values["data"] = smart_contract["data"]
                else:
                    amount = smart_contract["amount"]
                    values["senders"][0]["amount"] = amount
                    values["recipients"] = [{
                        "address": smart_contract["to_address"],
                        "amount": amount
                    }]
                    values["token"] = smart_contract["token"]
                    values["amount"] = amount
            # Freeze or Unfreeze balance
            elif txn_type in ["FreezeBalanceContract", "UnfreezeBalanceContract"]:
                if "resource" in txn_values:
                    values["resource"] = txn_values["resource"]
                else:
                    values["resource"] = "BANDWIDTH"

                if "receiver_address" in txn_values:
                    values["recipients"] = [{
                        "address": self.node.to_base58check_address(txn_values["receiver_address"]),
                        "amount": 0
                    }]
                else:
                    values["recipients"] = [{
                        "address": values["senders"][0]["address"],
                        "amount": 0
                    }]

                if "frozen_balance" in txn_values:
                    amount = str(self.fromSun(txn_values["frozen_balance"]))
                    values["amount"] = amount
                    values["senders"][0]["amount"] = amount
                    values["recipients"][0]["address"] = amount
            # Vote
            elif txn_type == "VoteWitnessContract":
                try:
                    values["recipients"] = [{
                        "address": txn_values["votes"][0]["vote_address"],
                        "voteCount": txn_values["votes"][0]["vote_count"]
                    }]
                except Exception as error:
                    pass
            return values
        except Exception as error:
            return {}

    async def __smart_contract_transaction(self, data: str, contract_address: ContractAddress) -> dict:
        """
        Unpacking a smart contract
        :param data: Smart Contract Information
        :param contract_address: Smart contract (Token TRC20) address
        """
        try:
            contract = self.node.get_contract(addr=contract_address)
            token_name = contract.functions.symbol()
            dec = contract.functions.decimals()
            amount = Decimal(value=int("0x" + data[72:], 0) / 10 ** int(dec))
            to_address = self.node.to_base58check_address("41" + data[32:72])
            return {
                "to_address": to_address,
                "token": token_name,
                "amount": "%.8f" % amount
            }
        except Exception as error:
            return {"data": str(data)}

def get_txn(tnx: Dict, user: TronAccountAddress, admin_fee: int, tnx_type: str, reporter: TronAccountAddress) -> Dict:
    amount, tx_fee = decimals.create_decimal(tnx["amount"]), decimals.create_decimal(tnx["fee"])
    tx_amount = amount + tx_fee if tnx_type == "TransferContract" else amount
    sender_amount = amount + admin_fee
    admin_amount = admin_fee - tx_fee if tnx_type == "TransferContract" else admin_fee
    tx = {
        "time": tnx["time"],
        "transactionHash": tnx["transactionHash"],
        "amount": "%.8f" % tx_amount,
        "fee": tnx["fee"],
        "senders": [
            {
                "address": user,
                "amount": "%.8f" % sender_amount
            }
        ],
        "recipients": [
            {
                "address": tnx["recipients"][0]["address"],
                "amount": "%.8f" % amount
            },
            {
                "address": reporter,
                "amount": "%.8f" % admin_amount
            }
        ]
    }
    if tnx_type == "TriggerSmartContract":
        tx["token"] = tnx["token"]
    return tx

transaction_parser = TransactionParser()