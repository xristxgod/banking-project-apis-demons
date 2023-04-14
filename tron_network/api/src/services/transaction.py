import json
import time
import asyncio
import random
from typing import Optional, List, Dict

import aiohttp
import tronpy.exceptions
from tronpy.tron import TAddress, PrivateKey, Transaction as Tx

from src import core
from src.external import CoinController, URL_MAIN, URL_TESTNET
from .services import AccountController
from ..schemas import (
    BodyCreateTransaction, BodySendTransaction,
    ResponseCreateTransaction, ResponseSendTransaction,
    TransactionData, ParticipantData
)
from config import Config, logger, decimals


TRON_API_KEYS = [
    "a684fa6d-6893-4928-9f8e-8decd5f034f2 "
]
URL = URL_MAIN if Config.NETWORK.upper() == "MAINNET" else URL_TESTNET


class Transaction:
    @staticmethod
    async def create(
            account: AccountController,
            body: BodyCreateTransaction,
            coin: Optional[str] = None
    ) -> ResponseCreateTransaction:
        to_address, amount = list(body.outputs[0].items())[0]
        if await account.optimal_fee(to_address) <= (await account.balance()).balance:
            raise ValueError("Not enough money to pay the commission")
        if coin is None:
            amount = core.utils.to_sun(float(amount))
            transaction = await core.node.trx.transfer(account.address, to=to_address, amount=amount)
        else:
            coin = await CoinController.get_token(coin)
            contract = await core.node.get_contract(coin.address)
            amount = int(float(amount) * 10 ** coin.decimals)
            if (await account.balance(coin.symbol)).balance * 10 ** coin.decimals < amount:
                raise Exception(f"You don't have enough {coin.symbol} on your balance to make a transaction!")
            transaction = await contract.functions.transfer(to_address, amount)
            transaction.with_owner(account.address)
        transaction = await transaction.build()
        create_transaction = {"rawData": transaction.to_json()["raw_data"]}
        body_transaction = await TransactionParser.packaging_for_dispatch(
            transaction.to_json(),
            transaction_type=transaction.to_json()["raw_data"]["contract"][0]["type"]
        )
        if body.adminAddress is not None:
            body_transaction.inputs.append(ParticipantData(
                address=body.adminAddress,
                amount=body.adminFee
            ))
            body_transaction.amount += body.adminFee
        create_transaction.update({"bodyTransaction": body_transaction})
        return ResponseCreateTransaction(
            createTxHex=json.dumps(create_transaction).encode("utf-8").hex(),
            bodyTransaction=body_transaction
        )

    @staticmethod
    async def send(
            account: AccountController,
            body: BodySendTransaction
    ) -> ResponseSendTransaction:
        private_key = PrivateKey(private_key_bytes=bytes.fromhex(account.private_key))
        data: Dict = json.loads(bytes.fromhex(body.createTxHex).decode("utf-8"))
        sign = Tx(client=core.node, raw_data=data.get("rawData")).sign(priv_key=private_key)
        try:
            sign.broadcast().wait()
            successfully = True
        except tronpy.exceptions.TransactionError as error:
            logger.error(f"{error}")
            successfully = False
        return ResponseSendTransaction(
            timestamp=int(time.time()),
            transactionId=sign.txid,
            bodyTransaction=TransactionData(**data.get("bodyTransaction")),
            successfully=successfully
        )


class TransactionParser:
    @staticmethod
    async def all_transactions(address: TAddress) -> List[TransactionData]:
        urls = [url.replace("<address>", address) for url in URL]
        headers = {
            "Accept": "application/json",
            "TRON-PRO-API-KEY": TRON_API_KEYS[random.randint(0, len(TRON_API_KEYS) - 1)]
        }
        data = []
        async with aiohttp.ClientSession(headers=headers) as session:
            for url in urls:
                async with session.get(url) as response:
                    data.append((await response.json()).get("data"))
        return await TransactionParser.parser(
            transactions=data
        )

    @staticmethod
    async def transaction(transaction_id: str) -> TransactionData:
        return (await TransactionParser.parser(transactions=[await core.node.get_transaction(transaction_id)]))[0]

    @staticmethod
    async def parser(transactions: List[Dict]) -> List[TransactionData]:
        fund_trx_for_send = []
        list_transactions = await asyncio.gather(*[
            TransactionParser.processing_transactions(
                transactions=transactions[right_border: (right_border + 1)],
            )
            for right_border in range(len(transactions))
        ])
        for transactions in list_transactions:
            fund_trx_for_send.extend(transactions)
        return fund_trx_for_send

    @staticmethod
    async def processing_transactions(transactions: List[Dict]):
        data = []
        for transaction in transactions:
            transaction_type = transaction["raw_data"]["contract"][0]["type"]
            data.append(await TransactionParser.packaging_for_dispatch(
                transaction=transaction,
                transaction_type=transaction_type
            ))
        return data

    @staticmethod
    async def packaging_for_dispatch(transaction: Dict, transaction_type: str) -> Optional[TransactionData]:
        transaction_value = transaction["raw_data"]["contract"][0]['parameter']["value"]
        fee_limit = await core.node.get_transaction_info(transaction["txID"])
        fee = 0 if "fee" not in fee_limit else core.utils.from_sun(fee_limit["fee"])
        value = TransactionData(
            timestamp=int(time.time()),
            transactionId=transaction["txID"],
            fee=fee,
            inputs=[ParticipantData(
                address=core.node.to_base58check_address(transaction_value["owner_address"]),
                amount=0
            )]
        )
        if transaction_type == "TransferContract":
            amount = decimals.create_decimal(core.utils.from_sun(transaction_value["amount"]))
            value.outputs = [ParticipantData(
                address=core.node.to_base58check_address(transaction_value["to_address"]),
                amount=amount
            )]
        elif transaction_type == "TriggerSmartContract":
            smart_contract = await core.smart_contract(
                data=transaction_value["data"],
                contract_address=transaction_value["contract_address"]
            )
            amount = smart_contract.get("amount")
            value.outputs = [ParticipantData(address=smart_contract.get("to_address"), amount=amount)]
            value.token = smart_contract.get("token")
        else:
            return None

        if (value.token is None and amount is None) \
                or (value.token is not None and not CoinController.is_token(value.token)):
            return None
        value.amount = amount
        value.inputs[0].amount = amount
        return value

    @staticmethod
    async def smart_contract(data: str, contract_address: TAddress):
        try:
            contract = await core.node.get_contract(addr=contract_address)
            coin = await CoinController.get_token(await contract.functions.symbol())
            return {
                "to_address": core.node.to_base58check_address("41" + data[32:72]),
                "token": coin.symbol,
                "amount": decimals.create_decimal(int("0x" + data[72:], 0) / 10 ** coin.decimals)
            }
        except tronpy.exceptions.AddressNotFound:
            pass


__all__ = [
    "Transaction", "TransactionParser"
]
