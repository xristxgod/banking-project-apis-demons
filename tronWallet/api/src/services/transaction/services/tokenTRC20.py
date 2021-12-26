import json
from decimal import Decimal

from api.src.utils.tron_typing import TokenTRC20
from api.src.node.node import NodeTron
from api.src.services.transaction.schemas import (
    BodyCreateTransaction, ResponseCreateTransaction, ResponseGetFeeLimit
)

class TRC20Transactions(NodeTron):
    """This class creates, signs and sends TRC10 transactions"""

    def create_transaction(self, body: BodyCreateTransaction) -> ResponseCreateTransaction:
        """Create a transaction TRC20"""
        if not self.node.is_address(body.fromAddress) and not self.node.is_address(body.fromAddress):
            raise RuntimeError("Address not found in the Tron system!")
        # If the transferred token is not the address of the smart contract, it will search for it in the database
        if not self.node.is_address(body.token):
            token = self.trc20_db.get_token(symbol=body.token)
            if not token:
                raise Exception(
                    "This token is not in the system, either add it via '/add-trc20-token'"
                    " or specify the smart contract addresses."
                )
        else:
            token = body.token
        # Connecting to a smart contract, and if the token is not in the system, it will add it
        contract = self.connect_to_contract(address=token)
        if isinstance(contract, str):
            raise Exception(contract)

        try:
            # Checks whether the user has enough TRX to pay the commission
            if Decimal(value=self.get_fee_limit(token=token).feeTRX) > self.node.get_account_balance(addr=body.fromAddress):
                raise Exception("You don't have enough TRX to pay the commission!!!")
            # Get the decimals of the token
            decimals = int(contract.functions.decimals())
            # Let's get the amount for the offspring in decimal
            amount = int(float(body.amount) * int(decimals))
            # Checks whether the user has a token balance to transfer
            if contract.functions.balanceOf(body.fromAddress) * decimals > amount:
                raise Exception("You do not have enough funds on your balance to make a transaction!!!")
            # Creating a transaction
            create_transaction = contract.functions.transfer(body.toAddress, amount).with_owner(body.fromAddress)
            # Build a transaction
            create_transaction = create_transaction.build()
            return ResponseCreateTransaction(
                createTxHex=json.dumps(create_transaction.to_json()["raw_data"]).encode("utf-8").hex(),
                bodyTransaction=create_transaction.to_json()
            )
        except Exception as error:
            raise error

    def get_fee_limit(self, token: TokenTRC20) -> ResponseGetFeeLimit:
        """Receive a commission for sending a token"""
        if len(token) < 15:
            token = self.trc20_db.get_token(symbol=token)
            if not token:
                raise Exception(
                    "This token is not in the system, either add it via '/add-trc20-token'"
                    " or specify the smart contract addresses."
                )
        contract = self.connect_to_contract(address=token)
        if isinstance(contract, str):
            raise Exception(contract)
        try:
            fee_trx = NodeTron().fromSun(contract.origin_energy_limit)
            return ResponseGetFeeLimit(feeTRX = str(fee_trx))
        except Exception as error:
            raise error

transaction_trc20 = TRC20Transactions()