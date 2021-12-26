import binascii

from mnemonic import Mnemonic

import hdwallet.exceptions
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.hdwallet import BIP44HDWallet

from src.utils.node import NodeETH
from src.utils.utils import PublicKey
import json
from decimal import Decimal
import web3.exceptions
from config import logger


class WalletETH(NodeETH):
    """This class creates ethereum wallets and checks their balance"""
    def create_wallet(self, words: str = None) -> json:
        """
        Create ethereum wallet
        :param words: Mnemonic phrase consisting of 12 or 24 unique words
        """
        if not words:
            words = Mnemonic("english").generate(strength=128)
        try:
            self.node.eth.account.enable_unaudited_hdwallet_features()
            __wallet = self.node.eth.account.from_mnemonic(mnemonic=words)
            logger.error(f"USER CREATE WALLET")
            return {
                "mnemonicWords": words,
                "privateKey": self.node.toHex(__wallet.key),
                "publicKey": binascii.hexlify(bytes(PublicKey(__wallet.key))).decode("utf-8"),
                "address": __wallet.address,
            }
        except web3.exceptions.ValidationError as error:
            logger.error(f"ERROR IN WALLET CREATION | ERROR: STEP 24 {error}")
            return {"error": str(error)}
        except Exception as error:
            logger.error(f"ERROR IN WALLET CREATION | ERROR: STEP 24 {error}")
            return {"error": str(error)}

    def create_deterministic_wallet(self, words: str = None, child: int = 10) -> json:
        """
        Create deterministic Ethereum wallet
        :param words: Mnemonic phrase consisting of 12 or 24 unique words
        :param child: The number of deterministic addresses created
        """
        if not words:
            words = Mnemonic("english").generate(strength=128)

        try:
            __wallet = BIP44HDWallet(cryptocurrency=EthereumMainnet).from_mnemonic(words, language="english")
            values = {
                "mnemonicPhrase": words,
                "privateKey": "0x" + __wallet.private_key(),
                "publicKey": __wallet.public_key(),
                "addresses": {}
            }
            __wallet.clean_derivation()
            for num in range(child):
                keys = BIP44Derivation(
                    cryptocurrency=EthereumMainnet,
                    account=0,
                    change=False,
                    address=num + 1
                )
                __wallet.from_path(path=keys)
                values["addresses"][f"{__wallet.path()}"] = {
                    "address": __wallet.address(),
                    "privateKey": "0x" + __wallet.private_key(),
                    "publicKey": __wallet.public_key()
                }
                __wallet.clean_derivation()
            logger.error(f"USER CREATE DETERMINISTIC WALLET")
            return values
        except hdwallet.exceptions.DerivationError as error:
            logger.error(f"ERROR IN DETERMINISTIC WALLET CREATION | ERROR: STEP 50 {error}")
            return {"error": str(error)}
        except Exception as error:
            logger.error(f"ERROR IN DETERMINISTIC WALLET CREATION | ERROR: STEP 50 {error}")
            return {"error": str(error)}

    def get_balance(self, address: str) -> json:
        """
        Get balance the ethereum wallet
        :param address: Wallet address
        """
        try:
            address = self.node.toChecksumAddress(address)
        except web3.exceptions.InvalidAddress as error:
            return {"error": str(error)}
        try:
            balance: Decimal = self.node.fromWei(
                self.node.eth.get_balance(address),
                "ether"
            )
            logger.error(f"USER '{address}' BALANCE: {balance}")
            return {"balance": str(balance)}
        except Exception as error:
            logger.error(f"BALANCE RECEIPT ERROR | USER: '{address}' | ERROR: STEP 92 {error}")
            return {"error": str(error)}


wallet_ethereum = WalletETH()
