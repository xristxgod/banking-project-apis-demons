from typing import Dict

from tronpy.tron import Tron, HTTPProvider, PrivateKey

from .token_database import token_db
from src.utils.utils import from_sun, to_sun, convert_time

from config import network, node

class NodeTron:
    # Provider config
    __provider = HTTPProvider(node)
    # Network
    network: str = network

    # Converts
    fromSun = staticmethod(from_sun)
    toSun = staticmethod(to_sun)

    # Time convert
    convertTime = staticmethod(convert_time)

    # Token db
    db = token_db

    def __init__(self):
        """Connect to Tron Node"""
        self.node = Tron(
            provider=self.__provider if self.network == "mainnet" else None,
            network=self.network
        )

    # <<<----------------------------------->>> Transaction helper <<<----------------------------------------------->>>

    def examination_transaction(self, **kwargs) -> Dict:
        """Check if everything was specified correctly"""
        values = {}

        # If the argument was passed `fromAddress`
        if "fromAddress" in kwargs and kwargs["fromAddress"] is not None:
            if not self.node.is_address(kwargs["fromAddress"]):
                raise Exception("Address not found in the Tron system!")
            else:
                values["fromAddress"] = kwargs["fromAddress"]
        # If the argument was passed `toAddress`
        if "toAddress" in kwargs and kwargs["toAddress"] is not None:
            if not self.node.is_address(kwargs["toAddress"]):
                raise Exception("Address not found in the Tron system!")
            else:
                values["toAddress"] = kwargs["toAddress"]
        # If the argument was passed `amount`
        if "amount" in kwargs and kwargs["amount"] is not None:
            if "fromAddress" in kwargs \
                    and float(self.node.get_account_balance(addr=values['fromAddress'])) < float(kwargs["amount"]):
                raise Exception("The amount sent is more than the balance.")
            else:
                values["amount"] = self.toSun(float(kwargs["amount"]))
        # If the argument was passed `privateKey`
        if "privateKey" in kwargs and kwargs["privateKey"] is not None:
            try:
                if isinstance(kwargs["privateKey"], str):
                    # Private key HAX to Private key BYTES
                    values["privateKey"] = PrivateKey(private_key_bytes=bytes.fromhex(kwargs["privateKey"]))
                else:
                    # If the private key was already BYTES
                    values["privateKey"] = PrivateKey(private_key_bytes=kwargs["privateKey"])
            except Exception as error:
                raise error
        # If the argument was passed `token`
        return values