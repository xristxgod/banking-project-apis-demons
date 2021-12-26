import tronpy.exceptions

from api.src.node.node import NodeTron
from api.src.utils.tron_typing import TronAccountAddress, TokenTRC10
from api.src.services.wallet.schemas import ResponseGetBalance

class TRC10Tokens(NodeTron):
    """This class interacts with the TRC10 token"""

    def get_balance(self, address: TronAccountAddress, token: TokenTRC10) -> ResponseGetBalance:
        """Get TRC10 token balance"""
        if not self.node.is_address(address):
            raise Exception(f"This address '{address}' was not found in the Tron system.")
        try:
            if isinstance(token, int) or token.isdigit():
                __id = int(token)
            else:
                __id = self.trc10_db.get_token(token=token)
                if __id == 0:
                    raise Exception("Token not found")
            asset = self.node.get_asset(id=__id)
        except Exception as error:
            raise error

        try:
            balance = self.node.get_account_asset_balance(addr=address, token_id=int(asset["id"]))
        except tronpy.exceptions.AddressNotFound as error:
            raise error

        if balance > 0:
            balance = str(NodeTron().fromSun(balance))
        else:
            balance = "0"
        return ResponseGetBalance(
            balance=balance,
            token=f"{asset['name']} ({asset['abbr']})"
        )

trc10_tokens = TRC10Tokens()