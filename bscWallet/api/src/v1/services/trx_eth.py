import json
import web3.exceptions
from fastapi import HTTPException
from starlette import status
from datetime import datetime
from config import Decimal, ADMIN_ADDRESS, ADMIN_FEE, decimal
from src.utils.node import node_singleton
from src.v1.schemas import BodyCreateTransaction, ResponseCreateTransaction, ResponseSendTransaction, \
    BodySendTransaction, ResponseAddressWithAmount
from .decode_raw_tx import decode_raw_tx, DecodedTx
from .nonce_locker import nonce_iterator_lock, nonce_locker
from ...utils.es_send import send_exception_to_kibana, send_msg_to_kibana


class TransactionBSC:
    """This class works with ethereum transactions"""
    def __init__(self):
        self.node_bridge = node_singleton

    async def create_transaction(
            self, body: BodyCreateTransaction, is_admin: bool = False
    ) -> ResponseCreateTransaction:
        """
        This function only signs the transaction
        :return: Signed transaction
        """
        try:
            if isinstance(body.outputs, str):
                body.outputs = json.loads(body.outputs)
            to_address, amount = list(body.outputs[0].items())[0]
            from_address = self.node_bridge.node.toChecksumAddress(
                ADMIN_ADDRESS if is_admin else body.fromAddress
            )
            to_address = self.node_bridge.node.toChecksumAddress(to_address)
            nonce = await self.node_bridge.async_node.eth.get_transaction_count(from_address)
        except Exception as error:
            await send_exception_to_kibana(error, 'THE TRANSACTION WAS NOT CREATED')
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

            value = decimal.create_decimal(amount)
            node_fee = decimal.create_decimal(create_transaction['gas']) / (10 ** 8)
            admin_fee = decimal.create_decimal(body.adminFee) if body.adminFee is not None else ADMIN_FEE
            sender = body.fromAddress if is_admin else from_address

            admin_address = body.adminAddress if body.adminAddress is not None else ADMIN_ADDRESS

            create_transaction.update({
                'adminFee': "%.8f" % admin_fee,
                'fromAddress': sender,
                'adminAddress': admin_address
            })
            tx_hex = json.dumps(create_transaction)

            return ResponseCreateTransaction(
                fee="%.8f" % node_fee,
                maxFeeRate=create_transaction['gasPrice'],
                createTxHex=tx_hex,
                time=int(round(datetime.now().timestamp())),
                amount="%.18f" % value,
                senders=[
                    ResponseAddressWithAmount(
                        address=sender,
                        amount="%.18f" % (value + admin_fee)
                    )
                ],
                recipients=[
                    ResponseAddressWithAmount(
                        address=to_address,
                        amount="%.18f" % value
                    ),
                    ResponseAddressWithAmount(
                        address=admin_address,
                        amount="%.18f" % admin_fee
                    )
                ]
            )
        except Exception as error:
            await send_exception_to_kibana(error, 'THE TRANSACTION WAS NOT CREATED')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    async def sign_send_transaction(self, body: BodySendTransaction, is_sender_from_body: bool = False) -> json:
        try:
            async with nonce_iterator_lock:
                payload = json.loads(body.createTxHex)
                admin_fee = payload.pop('adminFee', None)
                from_address = payload.pop('fromAddress', None)
                admin_address = payload.pop('adminAddress', ADMIN_ADDRESS)

                nonce = await self.node_bridge.async_node.eth.get_transaction_count(
                    self.node_bridge.node.toChecksumAddress(ADMIN_ADDRESS)
                )
                if nonce_locker.nonce is not None and nonce_locker.nonce > nonce:
                    nonce = nonce_locker.nonce

                transfer = {
                    "nonce": nonce,
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

                await send_msg_to_kibana(
                    msg=f"THE TRANSACTION HAS BEEN SENT | TX: {self.node_bridge.async_node.toHex(transaction_hash)}"
                )

                nonce_locker.nonce = nonce + 1

                tx: DecodedTx = decode_raw_tx(signed_transaction.rawTransaction.hex())

            value = decimal.create_decimal(tx.value) / (10 ** 18)
            node_fee = decimal.create_decimal(tx.gas) / (10 ** 8)
            admin_fee = decimal.create_decimal(admin_fee) if admin_fee is not None else ADMIN_FEE

            return ResponseSendTransaction(
                time=int(round(datetime.now().timestamp())),
                transactionHash=tx.hash_tx,
                amount="%.18f" % value,
                fee="%.8f" % node_fee,
                senders=[
                    ResponseAddressWithAmount(
                        address=from_address if is_sender_from_body and from_address is not None else tx.from_,
                        amount="%.18f" % (value + admin_fee)
                    )
                ],
                recipients=[
                    ResponseAddressWithAmount(
                        address=tx.to,
                        amount="%.18f" % value
                    ),
                    ResponseAddressWithAmount(
                        address=admin_address,
                        amount="%.18f" % admin_fee
                    ),
                ],
            )
        except Exception as error:
            await send_exception_to_kibana(error, 'THE TRANSACTION WAS NOT SENT')
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
            await send_exception_to_kibana(error, 'Get Optimal Gas')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

        amount = "%d" % self.node_bridge.async_node.toWei(amount, "gwei")
        trx = {
            "from": from_,
            "to": to_,
            "value": amount
        }
        estimate_gas: int = self.node_bridge.node.eth.estimateGas(trx)
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
            await send_exception_to_kibana(error, 'UNABLE TO DECRYPT TRANSACTION')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

        transaction = {
            "blockNumber": trx["blockNumber"],
            "blockHash": self.node_bridge.async_node.toHex(trx["blockHash"]),
            "transactionHash": self.node_bridge.async_node.toHex(trx["hash"]),
            "from": trx["from"],
            "to": trx["to"],
            "amount": str(self.node_bridge.async_node.fromWei(trx["value"], "ether")),
            "gas": trx["gas"],
            "gasPrice": trx["gasPrice"],
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
