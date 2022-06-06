from src.utils.node import NodeTron
from src.utils.types import TronAccountAddress, TokenTRC20
from src.v1.schemas import BodyCreateWallet, ResponseCreateWallet, ResponseGetBalance
from config import decimals


class Wallet(NodeTron):
    """This class creates and use a Tron account"""

    # <<<---------------------------------------->>> TRX <<<--------------------------------------------------------->>>

    def create_wallet(self, body: BodyCreateWallet) -> ResponseCreateWallet:
        """Create a tron wallet"""
        __wallet = self.node.get_address_from_passphrase(passphrase=body.words)
        return ResponseCreateWallet(
            words=body.words,
            privateKey=__wallet["private_key"],
            publicKey=__wallet["public_key"],
            address=__wallet["base58check_address"],
        )

    async def get_balance(self, address: TronAccountAddress) -> ResponseGetBalance:
        """Get TRX balance"""
        balance = await self.async_node.get_account_balance(addr=address)
        return ResponseGetBalance(balance="%.8f" % balance if balance > 0 else 0)

    # <<<---------------------------------------->>> Token <<<------------------------------------------------------->>>

    async def get_token_balance(self, address: TronAccountAddress, token: TokenTRC20) -> ResponseGetBalance:
        """
        Get TRC20 tokens balance
        :param address: Wallet address
        :param token: Token symbol or contract address
        """
        balance = 0
        token_dict = await self.db.get_token(token=token)
        # Connecting to a smart contract
        result = self.node.get_contract(addr=token_dict["address"]).functions.balanceOf(address)
        if int(result) > 0:
            balance = decimals.create_decimal(result) / decimals.create_decimal(10 ** token_dict["decimal"])
        return ResponseGetBalance(
            balance="%.8f" % balance if float(balance) > 0 else balance,
            token=token_dict["symbol"]
        )


wallet = Wallet()
