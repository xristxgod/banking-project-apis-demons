import json
import web3.exceptions
from config import logger, CONTRACT_TOKEN_SEND, CONTRACT_TOKEN_SEND_ABI
from src.utils.node import NodeETH
from src.utils.utils import convert_time


class TransactionToken(NodeETH):
    """This class works with token transactions"""
    def create_transaction(
            self, from_address, outputs, symbol, gas=40000,
            admin_address=None,
            admin_fee=None
    ) -> json:
        """
        This function creates and signs the transaction
        :param from_address: Sender's address
          :type from_address: str
        :param outputs: Recipients and values
          :type outputs: List of dicts {address: amount}
        :param symbol: Token name
          :type symbol: str
        :param gas: Transaction fees. Default 40_000
          :type gas: int or str
        :param admin_address: Address for sending service's fee
          :type admin_address: str
        :param admin_fee: Amount of service's fee
          :type admin_fee: int or str

        :return: transaction
        """

        # TMP until we use only one address
        to_address, amount = list(outputs[0].items())[0]

        try:
            from_address = self.node.toChecksumAddress(from_address)
            to_address = self.node.toChecksumAddress(to_address)
            nonce = self.node.eth.get_transaction_count(from_address)
        except web3.exceptions.InvalidAddress as error:
            return {"error": str(error)}

        with_admin = admin_address is not None and admin_fee is not None
        symbol = symbol.upper()
        token_contract = self.get_contract(symbol=symbol)
        if token_contract and token_contract is not None:
            coin_decimals = 10**int(token_contract.functions.decimals().call())
            amount = int(float(amount) * int(coin_decimals))
            if with_admin:
                admin_fee = int(float(amount) * int(coin_decimals))

            try:
                price = self.gas_price

                if with_admin:
                    contract = self.node.eth.contract(
                        address=self.node.toChecksumAddress(CONTRACT_TOKEN_SEND), abi=CONTRACT_TOKEN_SEND_ABI
                    )
                    to_1 = self.node.toChecksumAddress(admin_address)
                    amounts = [admin_fee, amount]
                    transfer = contract.functions.multisend(
                        self.get_contract_address(symbol=symbol), [to_1, to_address], amounts
                    ).buildTransaction({
                        "nonce": nonce,
                        "gasPrice": price,
                        "gas": gas,
                    })
                else:
                    transfer = token_contract.functions.transfer(
                        to_address, amount
                    ).buildTransaction({
                        "nonce": nonce,
                        "gas": gas,
                        "gasPrice": price
                    })

                return {
                    "payload": transfer,
                    "fee": gas,
                    "maxFeeRate": price,
                    "symbol": symbol.upper()
                }
            except web3.exceptions.InvalidTransaction as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED. InvalidTransaction | ERROR: {error}")
                return {"error": str(error)}
            except web3.exceptions.TransactionNotFound as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED. TransactionNotFound | ERROR: {error}")
                return {"error": str(error)}
            except Exception as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | ERROR: {error}")
                return {"error": str(error)}

    def sign_send_transaction(self, private_keys, payload: dict) -> json:
        """
        This function sends the transaction
        :return: Transaction hash
        """
        try:
            signed_transaction = self.node.eth.account.sign_transaction(
                payload, private_key=private_keys[0]
            )
            send_transaction = self.node.eth.send_raw_transaction(signed_transaction.rawTransaction)
            logger.error(
                f"THE TRANSACTION TOKEN WAS CREATED, SIGNED AND SENT "
                f"| TX: {self.node.toHex(send_transaction)}"
            )

            tx = self.node.eth.get_transaction(send_transaction)
            block = self.node.eth.get_block(tx['blockNumber'])
            return {
                "time": block['timestamp'],
                "datetime": convert_time(block['timestamp']),
                "transactionHash": tx['hash'].hex(),
                "amount": self.node.toWei(tx['value'], "ether"),
                "fee": self.node.toWei(tx['gas'], 'ether'),
                "senders": [tx['from']],
                "recipients": [tx['to']]
            }
        except web3.exceptions.InvalidTransaction as error:
            logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED. InvalidTransaction | ERROR: {error}")
            return {"error": str(error)}
        except web3.exceptions.TransactionNotFound as error:
            logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED. Transaction not found | ERROR: {error}")
            return {"error": str(error)}
        except Exception as error:
            logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | ERROR: {error}")
            return {"error": str(error)}


transaction_token = TransactionToken()
