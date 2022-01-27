import json
import web3.exceptions
from config import logger, decimal, Decimal, CONTRACT_MULTI_SEND, CONTRACT_MULTI_SEND_ABI
from src.utils.node import NodeETH
from src.utils.utils import convert_time
from typing import List


class TransactionETH(NodeETH):
    """This class works with ethereum transactions"""

    def create_transaction(
            self, from_address,
            outputs,
            gas=21000,
            admin_address=None,
            admin_fee=None
    ) -> json:
        """
        This function only signs the transaction
        :return: Signed transaction
        """
        # TMP. Only for time, when we can't send transaction to multiple wallets
        to_address, amount = list(outputs[0].items())[0]

        try:
            from_address = self.node.toChecksumAddress(from_address)
            to_address = self.node.toChecksumAddress(to_address)
            nonce = self.node.eth.get_transaction_count(from_address)
        except web3.exceptions.InvalidAddress as error:
            return {"error": str(error)}

        with_admin = admin_address is not None and admin_fee is not None
        if with_admin:
            admin_fee = self.node.toWei(admin_fee, "ether")
        create_transaction = {
            "nonce": nonce,
            "from": from_address,
            "to": to_address,
            "value": self.node.toWei(amount, "ether"),
            "gasPrice": self.gas_price,
            "gas": gas,
            'admin': {
                'adminFee': (
                    admin_fee - gas
                    if admin_fee - gas > (admin_fee / 10)
                    else (admin_fee / 10)
                ),
                'adminAddress': admin_address
            } if with_admin else None
        }
        try:
            return {
                "fee": gas,
                "maxFeeRate": create_transaction['gasPrice'],
                "payload": create_transaction
            }
        except web3.exceptions.InvalidTransaction as error:
            logger.error(f"THE TRANSACTION WAS NOT CREATED | STEP 37 ERROR: {error}")
            return {"error": str(error)}
        except web3.exceptions.TransactionNotFound as error:
            logger.error(f"THE TRANSACTION WAS NOT CREATED | STEP 37 ERROR: {error}")
            return {"error": str(error)}
        except Exception as error:
            logger.error(f"THE TRANSACTION WAS NOT CREATED | STEP 37 ERROR: {error}")
            return {"error": str(error)}

    def sign_send_transaction(self, payload: dict, private_keys: List[str]) -> json:
        """
        Submits a signed transaction
        :param payload: Signed `rawTransaction`
        :param private_keys: Private keys' list
        :return: Transaction hash
        """
        try:
            if payload['admin'] is not None:
                contract = self.node.eth.contract(
                    address=self.node.toChecksumAddress(CONTRACT_MULTI_SEND), abi=CONTRACT_MULTI_SEND_ABI
                )
                to_1 = self.node.toChecksumAddress(payload['admin']['adminAddress'])
                to_2 = self.node.toChecksumAddress(payload['to'])
                amounts = [payload['admin']['adminFee'], payload['value']]
                transfer = contract.functions.withdrawls(
                    [to_1, to_2], amounts
                ).buildTransaction({
                    "nonce": payload['nonce'],
                    "gasPrice": payload['gasPrice'],
                    "gas": payload['gas'],
                    "value": sum(amounts)
                })
            else:
                transfer = {
                    "nonce": payload['nonce'],
                    "to": payload['to'],
                    "value": payload['value'],
                    "gasPrice": payload['gasPrice'],
                    "gas": payload['gas'],
                    "data": b"",
                }
            signed_transaction = self.node.eth.account.sign_transaction(
                transfer, private_key=private_keys[0]
            )
            transaction_hash = self.node.eth.send_raw_transaction(
                transaction=self.node.toHex(signed_transaction.rawTransaction)
            )
            logger.error(f"THE TRANSACTION HAS BEEN SENT | TX: {self.node.toHex(transaction_hash)}")
            tx = self.node.eth.get_transaction(transaction_hash)
            block = self.node.eth.get_block(tx['blockNumber'])
            return {
                "time": block['timestamp'],
                "datetime": convert_time(block['timestamp']),
                "transactionHash": tx['hash'].hex(),
                "amount": tx['value'],
                "fee": tx['gas'],
                "senders": [tx['from']],
                "recipients": [tx['to']]
            }

        except web3.exceptions.InvalidTransaction as error:
            logger.error(f"THE TRANSACTION WAS NOT SENT | STEP 109 ERROR: {error}")
            return {"error": str(error)}
        except web3.exceptions.TransactionNotFound as error:
            logger.error(f"THE TRANSACTION WAS NOT SENT | STEP 109 ERROR: {error}")
            return {"error": str(error)}
        except Exception as error:
            logger.error(f"THE TRANSACTION WAS NOT SENT | STEP 109 ERROR: {error}")
            return {"error": str(error)}

    def get_optimal_gas(self, from_address: str, to_address: str, amount: int or float) -> json:
        """
        Get optimal fee
        :param from_address: Sender's address
          :type from_address: str
        :param to_address: Recipient's address
          :type to_address: str
        :param amount: Number of files to send
          :type amount: float or int or str
        """
        try:
            from_: str = self.node.toChecksumAddress(from_address)
            to_: str = self.node.toChecksumAddress(to_address)
        except web3.exceptions.InvalidAddress as error:
            return {"error": str(error)}

        gas_price: int = self.gas_price

        if isinstance(amount, float):
            amount = self.node.toWei(amount, "ether")

        trx = {
            "from": from_,
            "to": to_,
            "gasPrice": gas_price,
            "value": amount
        }
        gas_limit: int = self.node.eth.estimateGas(trx)
        logger.error(f"GET OPTIMAL GAS: {gas_limit} | {from_} -- {amount} -> {to_}")
        return {"gas": str(gas_limit)}

    def get_transaction(self, transaction_hash: str) -> json:
        """
        Get transaction by transaction hash
        :param transaction_hash: Transaction hash sent etched transaction
        """
        try:
            trx = dict(self.node.eth.get_transaction(transaction_hash=transaction_hash))
        except web3.exceptions.ValidationError as error:
            logger.error(f"UNABLE TO DECRYPT TRANSACTION | STEP 159 ERROR: {error}")
            return {"error": str(error)}
        except TypeError as error:
            logger.error(f"UNABLE TO DECRYPT TRANSACTION | STEP 159 ERROR: {error}")
            return {"error": str(error)}
        except Exception as error:
            logger.error(f"UNABLE TO DECRYPT TRANSACTION | STEP 159 ERROR: {error}")
            return {"error": str(error)}

        transaction = {
            "blockNumber": trx["blockNumber"],
            "blockHash": self.node.toHex(trx["blockHash"]),
            "transactionHash": self.node.toHex(trx["hash"]),
            "from": trx["from"],
            "to": trx["to"],
            "amount": str(self.node.fromWei(trx["value"], "ether")),
            "gas": trx["gas"],
            "gasPrice": trx["gasPrice"]
        }

        if len(trx["input"]) > 10:
            try:
                transaction["smartContract"] = self.__smart_contract_transaction(
                    input_=trx["input"],
                    contract_address=self.node.toChecksumAddress(trx["to"])
                )
            except Exception:
                transaction["smartContract"] = {"input": trx["input"]}
        else:
            transaction["smartContract"] = {}
        if len(transaction["smartContract"]) != 0:
            logger.error(f"THE TRANSACTION WAS UNPACKED")
        else:
            logger.error(f"TRANSACTION-SMART CONTRACT WAS UNPACKED")
        return transaction

    def get_transactions(self, address: str, direction_to_me: bool = None):
        pass

    def __smart_contract_transaction(self, input_: str, contract_address: str) -> dict:
        try:
            contract = self.node.eth.contract(address=contract_address, abi=self.abi)
            return {
                "to": self.node.toChecksumAddress("0x" + input_[34:74]),
                "token": str(contract.functions.symbol().call()),
                "amount": str(round(Decimal(int("0x" + input_[122:], 0) / 10 ** int(contract.functions.decimals().call()), ), 9))
            }
        except TypeError:
            return {}
        except web3.exceptions.ABIFunctionNotFound:
            return {}
        except Exception:
            return {"input": input_}


transaction_ethereum = TransactionETH()
