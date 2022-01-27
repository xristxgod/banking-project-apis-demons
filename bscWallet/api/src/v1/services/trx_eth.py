import json
import web3.exceptions
from fastapi import HTTPException
from starlette import status

from config import logger, Decimal
from src.utils.node import node_singleton

from src.v1.schemas import BodyCreateTransaction, ResponseCreateTransaction, ResponseSendTransaction, \
    BodySendTransaction, ResponseAddressWithAmount


class TransactionBSC:
    """This class works with ethereum transactions"""
    def __init__(self):
        self.node_bridge = node_singleton

    async def create_transaction(self, body: BodyCreateTransaction) -> ResponseCreateTransaction:
        """
        This function only signs the transaction
        :return: Signed transaction
        """
        try:
            if isinstance(body.outputs, str):
                body.outputs = json.loads(body.outputs)
            to_address, amount = list(body.outputs[0].items())[0]
            from_address = self.node_bridge.node.toChecksumAddress(body.fromAddress)
            to_address = self.node_bridge.node.toChecksumAddress(to_address)
            nonce = await self.node_bridge.async_node.eth.get_transaction_count(from_address)
        except Exception as error:
            logger.error(f"THE TRANSACTION WAS NOT CREATED | ERROR: {error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
        try:
            create_transaction = {
                "nonce": nonce,
                "from": from_address,
                "to": to_address,
                "value": self.node_bridge.async_node.toWei(amount, "ether"),
                "gasPrice": await self.node_bridge.gas_price,
                "gas": body.fee
            }
            return ResponseCreateTransaction(
                fee=create_transaction['gas'],
                maxFeeRate=create_transaction['gasPrice'],
                createTxHex=json.dumps(create_transaction)
            )
        except Exception as error:
            logger.error(f"THE TRANSACTION WAS NOT CREATED | ERROR: {error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    async def sign_send_transaction(self, body: BodySendTransaction) -> json:
        try:
            payload = json.loads(body.createTxHex)
            transfer = {
                "nonce": payload['nonce'],
                "to": payload['to'],
                "value": payload['value'],
                "gasPrice": payload['gasPrice'],
                "gas": payload['gas'],
                "data": b"",
            }
            signed_transaction = self.node_bridge.node.eth.account.sign_transaction(
                transfer, private_key=body.privateKeys[0]
            )
            transaction_hash = await self.node_bridge.async_node.eth.send_raw_transaction(
                transaction=self.node_bridge.async_node.toHex(signed_transaction.rawTransaction)
            )
            logger.error(f"THE TRANSACTION HAS BEEN SENT | TX: {self.node_bridge.async_node.toHex(transaction_hash)}")
            tx = await self.node_bridge.async_node.eth.get_transaction(transaction_hash)
            # block = await self.async_node.eth.get_block(tx['blockNumber'])
            return ResponseSendTransaction(
                time=None,
                datetime=None,
                transactionHash=tx['hash'].hex(),
                amount=tx['value'],
                fee=tx['gas'],
                senders=[ResponseAddressWithAmount(address=tx['from'], amount=tx['value'])],
                recipients=[ResponseAddressWithAmount(address=tx['to'], amount=tx['value'])],
            )
        except Exception as error:
            logger.error(f"THE TRANSACTION WAS NOT SENT | STEP 109 ERROR: {error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    async def get_optimal_gas(self, from_address: str, to_address: str, amount) -> json:
        """
        Get optimal fee
        :param from_address: Sender's address
          :type from_address: str
        :param to_address: Recipient's address
          :type to_address: str
        :param amount: Number of files to send
        """
        try:
            from_: str = self.node_bridge.async_node.toChecksumAddress(from_address)
            to_: str = self.node_bridge.async_node.toChecksumAddress(to_address)
        except web3.exceptions.InvalidAddress as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

        amount = "%d" % self.node_bridge.async_node.toWei(amount, "gwei")
        trx = {
            "from": from_,
            "to": to_,
            "value": amount
        }
        estimate_gas: int = self.node_bridge.node.eth.estimateGas(trx)
        logger.error(f"GET OPTIMAL GAS: {estimate_gas} | {from_} -- {amount} -> {to_}")
        gas_price: int = await self.node_bridge.gas_price

        return {
            "gas": str(estimate_gas * gas_price),
            "estimateGas": str(estimate_gas),
            "gasPrice": str(gas_price)
        }

    async def get_transaction(self, transaction_hash: str) -> json:
        """
        Get transaction by transaction hash
        :param transaction_hash: Transaction hash sent etched transaction
        """
        try:
            trx = dict(await self.node_bridge.async_node.eth.get_transaction(transaction_hash=transaction_hash))
        except Exception as error:
            logger.error(f"UNABLE TO DECRYPT TRANSACTION | ERROR: {error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

        transaction = {
            "blockNumber": trx["blockNumber"],
            "blockHash": self.node_bridge.async_node.toHex(trx["blockHash"]),
            "transactionHash": self.node_bridge.async_node.toHex(trx["hash"]),
            "from": trx["from"],
            "to": trx["to"],
            "amount": str(self.node_bridge.async_node.fromWei(trx["value"], "ether")),
            "gas": trx["gas"],
            "gasPrice": trx["gasPrice"]
        }

        if len(trx["input"]) > 10:
            try:
                transaction["smartContract"] = await self.__smart_contract_transaction(
                    input_=trx["input"],
                    contract_address=self.node_bridge.async_node.toChecksumAddress(trx["to"])
                )
            except Exception:
                transaction["smartContract"] = {"input": trx["input"]}
        else:
            transaction["smartContract"] = {}
        return transaction

    async def __smart_contract_transaction(self, input_: str, contract_address: str) -> dict:
        try:
            contract = self.node_bridge.async_node.eth.contract(address=contract_address, abi=self.node_bridge.abi)
            return {
                "to": self.node_bridge.async_node.toChecksumAddress("0x" + input_[34:74]),
                "token": str(contract.functions.symbol().call()),
                "amount": str(round(Decimal(int("0x" + input_[122:], 0) / 10 ** int(contract.functions.decimals().call()), ), 9))
            }
        except TypeError:
            return {}
        except web3.exceptions.ABIFunctionNotFound:
            return {}
        except Exception:
            return {"input": input_}


transaction_bsc = TransactionBSC()
