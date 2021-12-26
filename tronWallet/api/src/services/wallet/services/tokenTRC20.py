from decimal import Decimal

from api.src.node.node import NodeTron
from api.src.utils.tron_typing import TronAccountAddress, TokenTRC10
from api.src.services.wallet.schemas import (
    ResponseGetBalance, BodyAddNewTokenTRC20, ResponseAddNewTokenTRC20
)

class TRC20Tokens(NodeTron):
    """This class interacts with the TRC10 token"""

    def get_balance(self, address: TronAccountAddress, token: TokenTRC10) -> ResponseGetBalance:
        """Get TRC20 token balance"""
        if not self.node.is_address(address):
            raise Exception(f"This address '{address}' was not found in the Tron system.")

        if len(token) < 15:
            token = self.trc20_db.get_token(symbol=token)
            if not token:
                raise Exception(
                    "This token is not in the system, either add it via '/add-trc20-token'"
                    " or specify the smart contract addresses."
                )
        else:
            token = token

        contract = self.connect_to_contract(address=token)
        if isinstance(contract, str):
            raise Exception(contract)

        try:
            # We get the balance as an integer number
            int_balance = int(contract.functions.balanceOf(address))

            if int_balance > 0:
                # We get decimals for calculating the balance
                decimals = int(contract.functions.decimals())

                # We calculate the balance
                balance = str(round(
                    Decimal(value=int_balance / 10 ** decimals),
                    8
                ))
            else:
                balance = "0"

            return ResponseGetBalance(
                balance=balance,
                token=f"{contract.name} ({contract.functions.symbol()})"
            )
        except Exception as error:
            raise Exception(error)

    def add_new_token(self, body: BodyAddNewTokenTRC20) -> ResponseAddNewTokenTRC20:
        """Add a new token to the system"""
        token = self.trc20_db.is_token(address=body.address)
        if token:
            return ResponseAddNewTokenTRC20(
                message=f"The token '{token}' is already in the system"
            )
        contract = self.connect_to_contract(address=body.address)
        if isinstance(contract, str):
            return ResponseAddNewTokenTRC20(
                message=contract
            )
        return ResponseAddNewTokenTRC20(
            message=f"Token '{contract.functions.symbol()}' has been added"
        )

trc20_tokens = TRC20Tokens()

