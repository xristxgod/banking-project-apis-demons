import json
from fastapi import HTTPException
from starlette import status

from config import logger, decimal
from src.utils.node import node_singleton
from src.utils.tokens_database import TokenDB
from src.v1.schemas import (
    BodyCreateTransaction, ResponseCreateTransaction,
    ResponseCreateTokenTransaction, ResponseSendTransaction, BodySendTransaction, ResponseAddressWithAmount
)


class TransactionToken:
    def __init__(self):
        self.node_bridge = node_singleton
        self.__contracts = {}

    """This class works with token transactions"""
    async def create_transaction(self, body: BodyCreateTransaction, token: str) -> ResponseCreateTransaction:
        to_address, amount = list(body.outputs[0].items())[0]
        try:
            from_address = self.node_bridge.node.toChecksumAddress(body.fromAddress)
            to_address = self.node_bridge.node.toChecksumAddress(to_address)
            nonce = self.node_bridge.node.eth.get_transaction_count(from_address)
        except Exception as error:
            logger.error(f'CREATE TX ERROR: {error}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'CREATE TX ERROR: {error}. get_transaction_count'
            )
        symbol = token.upper()
        token_contract = await self.node_bridge.get_contract(symbol=symbol)
        if token_contract and token_contract is not None:
            coin_decimals = 10**int(token_contract.functions.decimals().call())
            amount = int(float(amount) * int(coin_decimals))
            try:
                price = await self.node_bridge.gas_price
                transfer = token_contract.functions.transfer(
                    to_address, amount
                ).buildTransaction({
                    'from': from_address,
                    "nonce": nonce,
                    "gasPrice": price,
                    'gas': 2000000,
                    'value': 0,
                })
                estimate_gas: int = self.node_bridge.node.eth.estimateGas(transfer)
                payload = {
                    key: transfer[key] for key in ['value', 'chainId', 'nonce', 'gasPrice', 'to', 'data']
                }
                gas = estimate_gas * price // (10 ** 10)
                payload.update({'gas': gas})
                return ResponseCreateTokenTransaction(
                    createTxHex=json.dumps(payload),
                    fee=str(gas),
                    maxFeeRate=str(price),
                    token=symbol
                )
            except Exception as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | ERROR: {error}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    async def __get_smart_contract_info(self, input_: str, contract_address: str) -> dict:
        """If the transaction is inside a smart counter, it will look for"""
        try:
            if contract_address is None:
                return None
            contract_address: str = contract_address.lower()
            amount = input_[-64:]
            to_address = f'0x{input_[-104:-64]}'
            for _contract in await TokenDB.get_tokens():
                if int(_contract[3].lower(), 0) == int(contract_address, 0):
                    contract = {
                        "tokenAddress": self.node_bridge.node.toChecksumAddress(_contract[3]),
                        "token": _contract[2],
                        "name": _contract[1],
                        "decimals": _contract[4]
                    }
                    break
            else:
                return {}

            format_str = f"%.{contract['decimals']}f"
            return {
                "tokenAddress": contract['tokenAddress'],
                "token": contract['token'],
                "name": contract['name'],
                "toAddress": to_address,
                "amount": format_str % (decimal.create_decimal(int("0x" + amount, 0)) / 10 ** contract['decimals'])
            }
        except Exception as e:
            logger.error(f'ERROR GET CONTRACT: {e}. CONTRACT ADDRESS: {contract_address} | {self.__contracts}')
            return None

    async def processing_smart_contract(self, tx):
        if len(tx["input"]) > 64:
            smart_contract = await self.__get_smart_contract_info(
                input_=tx["input"],
                contract_address=tx["to"]
            )
            if smart_contract is not None:
                return {
                    "token": smart_contract['token'],
                    "name": smart_contract['name'],
                    "amount": smart_contract['amount'],
                    "recipients": [ResponseAddressWithAmount(
                        address=smart_contract['toAddress'],
                        amount=smart_contract['amount'],
                    )]
                }
        return {}

    async def sign_send_transaction(self, body: BodySendTransaction) -> ResponseSendTransaction:
        """
        This function sends the transaction
        :return: Transaction hash
        """
        try:
            payload = json.loads(body.createTxHex)
            signed_transaction = self.node_bridge.node.eth.account.sign_transaction(
                payload, private_key=body.privateKeys[0]
            )
            logger.error("THE TRANSACTION TOKEN WAS SIGNED")
            send_transaction = await self.node_bridge.async_node.eth.send_raw_transaction(signed_transaction.rawTransaction)
            logger.error(
                f"THE TRANSACTION TOKEN WAS CREATED, SIGNED AND SENT "
                f"| TX: {self.node_bridge.async_node.toHex(send_transaction)}"
            )

            tx = await self.node_bridge.async_node.eth.get_transaction(send_transaction)
            contract_values = await self.processing_smart_contract(tx)
            print('++', contract_values)
            return ResponseSendTransaction(
                time=None,
                datetime=None,
                transactionHash=tx['hash'].hex(),
                amount=contract_values['amount'],
                fee="%.8f" % (decimal.create_decimal(tx['gas']) / 10 ** 8),
                senders=[ResponseAddressWithAmount(
                    address=tx['from'],
                    amount=contract_values['amount']
                )],
                recipients=contract_values['recipients'],
            )
        except Exception as error:
            logger.error(f"THE TRANSACTION TOKEN WAS NOT SENDER | ERROR: {error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    async def get_optimal_gas(self, from_address: str, to_address: str, amount, token: str) -> json:
        try:
            from_address = self.node_bridge.async_node.toChecksumAddress(from_address)
            to_address = self.node_bridge.async_node.toChecksumAddress(to_address)
            nonce = await self.node_bridge.async_node.eth.get_transaction_count(from_address)
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

        symbol = token.upper()

        token_contract = await self.node_bridge.get_contract(symbol=symbol)
        if token_contract and token_contract is not None:
            coin_decimals = 10 ** int(token_contract.functions.decimals().call())
            amount = int(float(amount) * int(coin_decimals))

            try:
                price = await self.node_bridge.gas_price
                estimate_gas = token_contract.functions.transfer(
                    to_address, amount
                ).estimateGas({
                    'from': from_address,
                    "nonce": nonce,
                    "gasPrice": price,
                    'gas': 2000000,
                    'value': 0,
                })
                return {
                    "gas": estimate_gas,
                    "estimateGas": estimate_gas,
                    "gasPrice": price
                }
            except Exception as error:
                logger.error(f"THE TRANSACTION TOKEN WAS NOT CREATED | ERROR: {error}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


transaction_token = TransactionToken()
