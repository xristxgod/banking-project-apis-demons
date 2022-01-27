import binascii

from fastapi import HTTPException
from mnemonic import Mnemonic
from starlette import status

from src.utils.node import node_singleton
from src.utils.utils import PublicKey
from decimal import Decimal
import web3.exceptions
from config import logger
from src.v1.schemas import ResponseCreateWallet, GetBalance


class WalletBSC:
    """This class creates ethereum wallets and checks their balance"""
    def __init__(self):
        self.node_bridge = node_singleton

    async def create_wallet(self, words: str = None) -> ResponseCreateWallet:
        """
        Create ethereum wallet
        :param words: Mnemonic phrase consisting of 12 or 24 unique words
        """
        if not words:
            words = Mnemonic("english").generate(strength=128)
        try:
            self.node_bridge.node.eth.account.enable_unaudited_hdwallet_features()
            __wallet = self.node_bridge.node.eth.account.from_mnemonic(mnemonic=words)
            logger.error(f"USER CREATE WALLET")
            return ResponseCreateWallet(
                mnemonicWords=words,
                privateKey=self.node_bridge.async_node.toHex(__wallet.key),
                publicKey=binascii.hexlify(bytes(PublicKey(__wallet.key))).decode("utf-8"),
                address=__wallet.address.lower(),
            )
        except Exception as error:
            logger.error(f"ERROR IN WALLET CREATION | ERROR: STEP 24 {error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))

    async def get_balance(self, address: str) -> GetBalance:
        """
        Get balance the ethereum wallet
        :param address: Wallet address
        """
        try:
            address = self.node_bridge.async_node.toChecksumAddress(address)
        except web3.exceptions.InvalidAddress as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
        try:
            balance: Decimal = self.node_bridge.async_node.fromWei(
                await self.node_bridge.async_node.eth.get_balance(address),
                "ether"
            )
            logger.error(f"USER '{address}' BALANCE: {balance}")
            return GetBalance(balance=str(balance))
        except Exception as error:
            logger.error(f"BALANCE RECEIPT ERROR | USER: '{address}' | ERROR: {error}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))


wallet_bsc = WalletBSC()
