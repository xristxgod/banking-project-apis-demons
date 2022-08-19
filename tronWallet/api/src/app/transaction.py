import json
import time
from typing import Optional, Dict

import tronpy.exceptions
from tronpy.tron import PrivateKey, Transaction as Tx

from src import core
from src.external import CoinController
from .services import AccountController
from ..schemas import (
    BodyCreateTransaction, BodySendTransaction,
    ResponseCreateTransaction, ResponseSendTransaction,
    TransactionData
)
from config import logger


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
            coin = CoinController.get_token(coin)
            contract = await core.node.get_contract(coin.address)
            amount = int(float(amount) * 10 ** coin.decimals)
            if (await account.balance(coin.symbol)).balance * 10 ** coin.decimals < amount:
                raise Exception(f"You don't have enough {coin.symbol} on your balance to make a transaction!")
            transaction = await contract.functions.transfer(to_address, amount)
            transaction.with_owner(account.address)
        transaction = await transaction.build()
        return ResponseCreateTransaction(
            createTxHex=json.dumps(transaction.to_json()["raw_data"]).encode("utf-8").hex(),
            bodyTransaction=TransactionParser.packaging(transaction.to_json())
        )

    @staticmethod
    async def send(
            account: AccountController,
            body: BodySendTransaction
    ) -> ResponseSendTransaction:
        private_key = PrivateKey(private_key_bytes=bytes.fromhex(account.private_key))
        raw_data = json.loads(bytes.fromhex(body.createTxHex).decode("utf-8"))
        sign = Tx(client=core.node, raw_data=raw_data).sign(priv_key=private_key)
        try:
            sign.broadcast().wait()
            successfully = True
        except tronpy.exceptions.TransactionError as error:
            logger.error(f"{error}")
            successfully = False
        return ResponseSendTransaction(
            timestamp=int(time.time()),
            transactionId=sign.txid,
            successfully=successfully
        )


class TransactionParser:
    @staticmethod
    def parser(transaction_id: str) -> str:
        pass

    @staticmethod
    def packaging(data: Dict) -> TransactionData:
        pass
