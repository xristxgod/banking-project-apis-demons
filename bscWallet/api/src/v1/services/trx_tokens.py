import json
from fastapi import HTTPException
from starlette import status
from datetime import datetime
from config import decimal, ADMIN_FEE, ADMIN_ADDRESS
from src.utils.node import node_singleton
from src.utils.tokens_database import TokenDB
from src.v1.schemas import (
    BodyCreateTransaction, ResponseCreateTransaction,
    ResponseCreateTokenTransaction, ResponseSendTransaction, BodySendTransaction, ResponseAddressWithAmount
)
from .decode_raw_tx import decode_raw_tx, DecodedTx
from .nonce_locker import nonce_locker, nonce_iterator_lock
from ...utils.es_send import send_exception_to_kibana, send_msg_to_kibana


class TransactionToken:
    def __init__(self):
        self.node_bridge = node_singleton
        self.__contracts = {}

    """This class works with token transactions"""
    async def create_transaction(
            self, body: BodyCreateTransaction, token: str, is_admin: bool = False
    ) -> ResponseCreateTransaction:
        to_address, amount = list(body.outputs[0].items())[0]
        try:
            from_address = self.node_bridge.node.toChecksumAddress(
                ADMIN_ADDRESS if is_admin else body.fromAddress
            )
            to_address = self.node_bridge.node.toChecksumAddress(to_address)
            nonce = self.node_bridge.node.eth.get_transaction_count(from_address)
        except Exception as error:
            await send_exception_to_kibana(error, 'CREATE TX ERROR')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'CREATE TX ERROR: {error}. get_transaction_count'
            )
        symbol = token.upper()
        token_contract = await self.node_bridge.get_contract(symbol=symbol)
        if token_contract and token_contract is not None:
            coin_decimals = 10**int(token_contract.functions.decimals().call())
            value = decimal.create_decimal(amount)
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
                gas: int = self.node_bridge.node.eth.estimateGas(transfer)
                payload = {
                    key: transfer[key] for key in ['value', 'chainId', 'nonce', 'gasPrice', 'to', 'data', 'gas']
                }

                payload.update({'gas': gas})

                node_fee = decimal.create_decimal(payload['gas']) / (10 ** 8)
                admin_fee = decimal.create_decimal(body.adminFee) if body.adminFee is not None else ADMIN_FEE
                sender = body.fromAddress if is_admin else from_address

                admin_address = body.adminAddress if body.adminAddress is not None else ADMIN_ADDRESS

                payload.update({
                    'adminFee': "%.8f" % admin_fee,
                    'fromAddress': sender,
                    'adminAddress': admin_address
                })
                tx_hex = json.dumps(payload)

                return ResponseCreateTokenTransaction(
                    createTxHex=tx_hex,
                    fee=node_fee,
                    maxFeeRate=str(price),
                    token=symbol,
                    time=int(round(datetime.now().timestamp())),
                    amount="%.18f" % value,
                    senders=[
                        ResponseAddressWithAmount(
                            address=body.fromAddress if is_admin else from_address,
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
                await send_exception_to_kibana(error, 'THE TRANSACTION TOKEN WAS NOT CREATED')
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
            await send_exception_to_kibana(e, 'ERROR GET CONTRACT')
            return None

    async def processing_smart_contract(self, tx: DecodedTx):
        if len(tx.data) > 64:
            smart_contract = await self.__get_smart_contract_info(
                input_=tx.data,
                contract_address=tx.to
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

    async def sign_send_transaction(
            self, body: BodySendTransaction, is_sender_from_body: bool = False
    ) -> ResponseSendTransaction:
        """
        This function sends the transaction
        :return: Transaction hash
        """
        try:
            async with nonce_iterator_lock:
                payload = json.loads(body.createTxHex)
                admin_fee = payload.pop('adminFee', None)
                from_address = payload.pop('fromAddress', None)
                admin_address = payload.pop('adminAddress', ADMIN_ADDRESS)

                nonce = await self.node_bridge.async_node.eth.get_transaction_count(from_address)
                if nonce_locker.nonce is not None and nonce_locker.nonce > nonce:
                    nonce = nonce_locker.nonce

                payload["nonce"] = nonce

                signed_transaction = self.node_bridge.node.eth.account.sign_transaction(
                    payload, private_key=body.privateKeys[0]
                )
                send_transaction = await self.node_bridge.async_node.eth.send_raw_transaction(
                    signed_transaction.rawTransaction
                )

                nonce_locker.nonce = nonce + 1

            await send_msg_to_kibana(
                msg=f"THE TRANSACTION TOKEN WAS CREATED, SIGNED AND SENT "
                    f"| TX: {self.node_bridge.async_node.toHex(send_transaction)}"
            )

            tx = decode_raw_tx(signed_transaction.rawTransaction.hex())
            contract_values = await self.processing_smart_contract(tx)

            value = decimal.create_decimal(contract_values['amount'])
            node_fee = decimal.create_decimal(payload['gas']) / (10 ** 8)
            admin_fee = decimal.create_decimal(admin_fee) if admin_fee is not None else ADMIN_FEE

            return ResponseSendTransaction(
                time=int(round(datetime.now().timestamp())),
                transactionHash=tx.hash_tx,
                fee="%.8f" % node_fee,
                amount="%.8f" % value,
                senders=[
                    ResponseAddressWithAmount(
                        address=from_address if is_sender_from_body and from_address is not None else tx.from_,
                        amount="%.8f" % (value + admin_fee)
                    )
                ],
                recipients=[
                    ResponseAddressWithAmount(
                        address=contract_values['recipients'][0].address,
                        amount="%.8f" % value
                    ),
                    ResponseAddressWithAmount(
                        address=admin_address,
                        amount="%.8f" % admin_fee
                    )
                ]
            )
        except Exception as error:
            await send_exception_to_kibana(error, 'THE TRANSACTION TOKEN WAS NOT SENDER')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    async def get_optimal_gas(self, from_address: str, to_address: str, amount, token: str) -> json:
        try:
            from_address = self.node_bridge.async_node.toChecksumAddress(from_address)
            to_address = self.node_bridge.async_node.toChecksumAddress(to_address)
            nonce = await self.node_bridge.async_node.eth.get_transaction_count(from_address)
        except Exception as error:
            await send_exception_to_kibana(error, 'Get Optimal Gas for token')
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
                await send_exception_to_kibana(error, 'THE TRANSACTION TOKEN WAS NOT CREATED')
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


transaction_token = TransactionToken()
