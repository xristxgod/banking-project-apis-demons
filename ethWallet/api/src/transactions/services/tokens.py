import json
import web3.exceptions
from config import logger
from src.utils.node import NodeETH
from src.utils.utils import convert_time


class TransactionToken(NodeETH):
    """This class works with token transactions"""
    def create_and_sign_transaction(self, from_private_key, from_address, to_address, amount, symbol, gas=40000) -> json:
        """
        This function creates and signs the transaction
        :param from_private_key: Sender's private key
          :type from_private_key: str
        :param from_address: Sender's address
          :type from_address: str
        :param to_address: Recipient's address
          :type to_address: str
        :param amount: Number of files to send
          :type amount: float or int or str
        :param symbol: Token name
          :type symbol: str
        :param gas: Transaction fees. Default 40_000
          :type gas: int or str

        :return: Signed transaction
        """
        try:
            from_address = self.node.toChecksumAddress(from_address)
            to_address = self.node.toChecksumAddress(to_address)
            nonce = self.node.eth.get_transaction_count(from_address)
        except web3.exceptions.InvalidAddress as error:
            return {"error": str(error)}

        contract = self.get_contract(symbol=symbol.upper())
        if contract and contract is not None:
            coin_decimals = 10**int(contract.functions.decimals().call())
            amount = int(float(amount) * int(coin_decimals))

            try:
                create_transaction = contract.functions.transfer(
                    to_address, amount
                ).buildTransaction({
                    "nonce": nonce,
                    "gas": gas,
                    "gasPrice": self.gas_price
                })
                signed_transaction = self.node.eth.account.sign_transaction(
                    create_transaction, private_key=from_private_key
                )
                logger.error(
                    f"TRANSACTION TOKEN CREATED AND SIGNED | {from_address} -- {amount} -> {to_address} | TX: {signed_transaction}"
                )
                return {
                    "createTxHex": self.node.toHex(signed_transaction.rawTransaction),
                    **create_transaction
                }
            except web3.exceptions.InvalidTransaction as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | STEP 37 ERROR: {error}")
                return {"error": str(error)}
            except web3.exceptions.TransactionNotFound as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | STEP 37 ERROR: {error}")
                return {"error": str(error)}
            except Exception as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | STEP 37 ERROR: {error}")
                return {"error": str(error)}

    def send_transaction(self, from_private_key, from_address, to_address, amount, symbol, gas=40000) -> json:
        """
        This function sends the transaction
        :param from_private_key: Sender's private key
          :type from_private_key: str
        :param from_address: Sender's address
          :type from_address: str
        :param to_address: Recipient's address
          :type to_address: str
        :param amount: Number of files to send
          :type amount: float or int or str
        :param symbol: Token name
          :type symbol: str
        :param gas: Transaction fees. Default 40_000
          :type gas: int or str

        :return: Transaction hash
        """
        try:
            from_address = self.node.toChecksumAddress(from_address)
            to_address = self.node.toChecksumAddress(to_address)
            nonce = self.node.eth.get_transaction_count(from_address)
        except web3.exceptions.InvalidAddress as error:
            return json.dumps({"error": str(error)})

        contract = self.get_contract(symbol=symbol.upper())
        if contract and contract is not None:
            coin_decimals = 10 ** int(contract.functions.decimals().call())
            amount = int(float(amount) * int(coin_decimals))

            try:
                create_transaction = contract.functions.transfer(
                    to_address, amount
                ).buildTransaction({
                    "nonce": nonce,
                    "gas": gas,
                    "gasPrice": self.gas_price
                })
                signed_transaction = self.node.eth.account.sign_transaction(
                    create_transaction, private_key=from_private_key
                )
                send_transaction = self.node.eth.send_raw_transaction(signed_transaction.rawTransaction)
                logger.error(
                    f"THE TRANSACTION TOKEN WAS CREATED, SIGNED AND SENT "
                    f"| {from_address} -- {amount} -> {to_address} "
                    f"| TX: {self.node.toHex(send_transaction)}"
                )

                tx = self.node.eth.get_transaction(send_transaction)
                block = self.node.eth.get_block(tx['blockNumber'])
                return {
                    "time": block['timestamp'],
                    "datetime": convert_time(block['timestamp']),
                    "transactionHash": tx['hash'],
                    "amount": self.node.eth.toWei(tx['value'], "ether"),
                    "fee": self.node.eth.toWei(tx['gas'], 'ether'),
                    "senders": [tx['from']],
                    "recipients": [tx['to']]
                }
            except web3.exceptions.InvalidTransaction as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | STEP 84 ERROR: {error}")
                return {"error": str(error)}
            except web3.exceptions.TransactionNotFound as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | STEP 84 ERROR: {error}")
                return {"error": str(error)}
            except Exception as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | STEP 84 ERROR: {error}")
                return {"error": str(error)}


transaction_token = TransactionToken()
