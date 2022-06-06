import asyncio
from decimal import Decimal
from typing import List, Dict, Tuple

import requests
from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from src.utils.token_database import token_db
from src.utils.node import NodeTron
from src.utils.types import TronAccountAddress, TokenTRC20, ContractAddress, TransactionHash
from config import network, decimals


async def get_contract(addr: str) -> Tuple[str, int]:
    token_info = await token_db.get_token(addr) if network.lower() == "mainnet" else await token_db.get_test_token(addr)
    return token_info.get("symbol"), token_info.get("decimal")


async def get_from_and_to(tx_id: str) -> Tuple:
    client = None
    try:
        client = AsyncTron(
            provider=AsyncHTTPProvider(api_key="a684fa6d-6893-4928-9f8e-8decd5f034f2") if network == "mainnet" else None,
            network=network
        )
        transaction = await client.get_transaction(txn_id=tx_id)
        raw_data = transaction.get("raw_data")
        contract = raw_data.get("contract")
        parameter = contract[0].get("parameter") if isinstance(contract, list) and len(contract) > 0 else None
        if parameter is None:
            return None, None
        value = parameter.get("value")
        from_address = value.get("owner_address") if "owner_address" in value.keys() else None
        if isinstance(value.get("data"), str) \
                and contract[0].get("type") == "TriggerSmartContract" \
                and len(value.get("data")) > 72:
            to_address = client.to_base58check_address("41" + value.get("data")[32:72])
        else:
            to_address = value.get("to_address")
        from_address = client.to_base58check_address(from_address) if from_address is not None else None
        to_address = client.to_base58check_address(to_address) if to_address is not None else None
        return from_address, to_address
    finally:
        if client is not None:
            await client.close()


async def get_helper_data(tx_id: str) -> Tuple:
    """Smart contract helper"""
    client = None
    try:
        client = AsyncTron(
            provider=AsyncHTTPProvider(
                api_key="a684fa6d-6893-4928-9f8e-8decd5f034f2") if network == "mainnet" else None,
            network=network
        )
        transaction = await client.get_transaction(txn_id=tx_id)
        raw_data = transaction.get("raw_data")
        contract = raw_data.get("contract")
        parameter = contract[0].get("parameter") if isinstance(contract, list) and len(contract) > 0 else None
        if parameter is None:
            return None, None, None
        value = parameter.get("value")
        if isinstance(value.get("data"), str) \
                and contract[0].get("type") == "TriggerSmartContract" \
                and len(value.get("data")) > 72:
            data_value = value.get("data")
            to_address = client.to_base58check_address("41" + data_value[32:72])
            contract_address = value.get("contract_address")
            if contract_address is None:
                return None, None, None
            symbol, decimals_num = await get_contract(contract_address)
            amount_decimal = int("0x" + data_value[72:], 0)
            amount = amount_decimal / 10 ** decimals_num
            return decimals.create_decimal(amount), to_address, symbol
        else:
            return None, None, None


    finally:
        if client is not None:
            await client.close()


class TransactionParser(NodeTron):

    async def get_transaction(self, transaction_hash: TransactionHash):
        return await self.__get_transactions(transactions=[await self.async_node.get_transaction(txn_id=transaction_hash)])

    async def get_all_transactions(self, address: TronAccountAddress, token: TokenTRC20 = None):
        headers = {"Accept": "application/json", "TRON-PRO-API-KEY": "a684fa6d-6893-4928-9f8e-8decd5f034f2"}
        url = f"https://api.{'' if network == 'mainnet' else f'{network.lower()}.'}trongrid.io/v1/accounts/{address}/transactions"
        url += f"/trc20?limit=200&contract_address={(await token_db.get_token(token=token))['address']}" if token is not None else "?limit=200"
        transactions = requests.get(url, headers=headers).json()["data"]
        return await self.__get_transactions(transactions=transactions, token=token)

    async def __get_transactions(self, transactions: List, token: TokenTRC20 = None) -> List:
        """Get all transactions by address"""
        fund_trx_for_send = []
        list_transactions = await asyncio.gather(*[
            self.__processing_transactions(
                transactions=transactions[right_border: (right_border + 1)],
                token=token if token else None
            )
            for right_border in range(len(transactions))
        ])
        for transactions in list_transactions:
            fund_trx_for_send.extend(transactions)
        return fund_trx_for_send

    async def __processing_transactions(self, transactions: Dict, token: TokenTRC20 = None) -> List:
        """
        Unpacking transactions and checking for the presence of required addresses in them
        :param transactions: Set of transactions
        """
        funded_trx_for_sending = []
        for txn in transactions:
            if token:
                funded_trx_for_sending.append(await self.__packaging_for_dispatch_token(txn=txn))
            else:
                txn_type = txn["raw_data"]["contract"][0]["type"]
                funded_trx_for_sending.append(await self.__packaging_for_dispatch(txn=txn, txn_type=txn_type))
        return funded_trx_for_sending

    async def __packaging_for_dispatch_token(self, txn: Dict) -> Dict:
        """
        Packaging the necessary transaction to send
        :param txn: Transaction
        :param txn_type: Transaction type
        """
        tx_fee = await self.async_node.get_transaction_info(txn_id=txn["transaction_id"])
        if "fee" in tx_fee:
            fee = "%.8f" % decimals.create_decimal(self.fromSun(tx_fee["fee"]))
        else:
            fee = "%.8f" % decimals.create_decimal(0)
        amount = "%.8f" % decimals.create_decimal(int(txn["value"]) / (10 ** int(txn["token_info"]["decimals"])))
        if txn["from"] is None or txn["to"] is None:
            from_, to_ = await get_from_and_to(tx_id=txn["transaction_id"])
        else:
            from_, to_ = txn["from"], txn["to"]
        return {
            "time": txn["block_timestamp"],
            "transactionHash": txn["transaction_id"],
            "fee": fee,
            "amount": amount,
            "senders": [
                {
                    "address": from_,
                    "amount": amount
                }
            ],
            "recipients": [
                {
                    "address": to_,
                    "amount": amount
                }
            ],
            "token": txn["token_info"]["symbol"]
        }

    async def __packaging_for_dispatch(self, txn: Dict, txn_type: str) -> Dict:
        """
        Packaging the necessary transaction to send
        :param txn: Transaction
        :param txn_type: Transaction type
        """
        try:
            txn_values = txn["raw_data"]["contract"][0]['parameter']["value"]
            try:
                fee_limit = await self.async_node.get_transaction_info(txn["txID"])
                if "fee" not in fee_limit:
                    raise Exception
                fee = "%.8f" % decimals.create_decimal(self.fromSun(fee_limit["fee"]))
            except Exception:
                fee = "%.8f" % decimals.create_decimal(0)
            values = {
                "time": txn["raw_data"]["timestamp"] if "timestamp" in txn["raw_data"] else "",
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
                    try:
                        smart_contract = await get_helper_data(txn["txID"])
                        amount, to_address, token = smart_contract
                        values["senders"][0]["amount"] = "%.8f" % amount
                        values["recipients"] = [{
                            "address": to_address,
                            "amount": "%.8f" % amount
                        }]
                        values["token"] = token
                        values["amount"] = "%.8f" % amount
                    except Exception:
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
            return values
        except Exception as error:
            return {}

    async def __smart_contract_transaction(self, data: str, contract_address: ContractAddress) -> Dict:
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
    amount = decimals.create_decimal(tnx["amount"])
    sender_amount = amount + admin_fee
    tx = {
        "time": tnx.get("time"),
        "transactionHash": tnx.get("transactionHash"),
        "amount": "%.8f" % amount,
        "fee": "%.8f" % decimals.create_decimal(tnx["fee"]),
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
                "amount": "%.8f" % admin_fee
            }
        ]
    }
    if tnx_type == "TriggerSmartContract":
        tx["token"] = tnx["token"]
    return tx


transaction_parser = TransactionParser()
