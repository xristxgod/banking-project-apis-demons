import requests.exceptions

import tronpy.contract
import tronpy.exceptions
from tronpy.tron import Tron
from tronpy.keys import PrivateKey

from .external_data.database_trc10 import TRC10DB
from .external_data.database_trc20 import TRC20DB
from api.src.utils.utils import from_sun, to_sun, convert_time
from api.src.utils.tron_typing import ContractAddress
from api.src.config import config, TronGridApiKey, network

class NodeTron:

    # Providers
    __config = config

    # API key for TronGird.io
    __api_key = TronGridApiKey

    # Network
    __network = network.lower()

    # Converts
    fromSun = staticmethod(from_sun)
    toSun = staticmethod(to_sun)

    # Time convert
    convertTime = staticmethod(convert_time)

    # Tokens DB
    trc10_db = TRC10DB()
    trc20_db = TRC20DB()

    def __init__(self):
        """Connect to Node"""
        self.node = Tron(provider=self.__api_key, conf=self.__config, network=self.__network)

    def connect_to_contract(self, address: ContractAddress) -> tronpy.contract.Contract or str:
        """
        Connect to smart contract (token)
        :param address: Smart contract (token) address
        :return: tronpy.contract.Contract
        """
        try:
            contract = self.node.get_contract(addr=address)
            # Checks if the given token is in the database. If not, then it records
            if not self.trc20_db.is_token(address=address):
                self.trc20_db.add_new_token(
                    symbol=contract.functions.symbol(),
                    address=address
                )
            return contract
        except tronpy.exceptions.AddressNotFound as error:
            return str(error)
        except requests.exceptions.HTTPError as error:
            return str(error)
        except Exception as error:
            return str(error)

    def examination_transaction(self, **kwargs) -> dict:
        """Check if everything was specified correctly"""
        values = {}
        if not self.node.is_address(kwargs["fromAddress"]):
            raise RuntimeError("Address not found in the Tron system!")
        else:
            values["fromAddress"] = kwargs["fromAddress"]
        if not self.node.is_address(kwargs["toAddress"]):
            raise RuntimeError("Address not found in the Tron system!")
        else:
            values["toAddress"] = kwargs["toAddress"]

        if "amount" in kwargs:
            if float(self.node.get_account_balance(addr=values['fromAddress'])) < float(kwargs["amount"]):
                raise Exception("The amount sent is more than the balance.")
            try:
                values["amount"] = self.toSun(float(kwargs["amount"]))
            except Exception as error:
                raise RuntimeError(str(error))
        else:
            values["amount"] = 0

        if "privateKey" in kwargs:
            try:
                if isinstance(kwargs["privateKey"], str):
                    values["privateKey"] = PrivateKey(private_key_bytes=bytes.fromhex(kwargs["privateKey"]))
                else:
                    values["privateKey"] = PrivateKey(private_key_bytes=kwargs["privateKey"])
            except tronpy.exceptions.BadKey as error:
                raise RuntimeError(str(error))

        if "token" in kwargs:
            try:
                if isinstance(kwargs["token"], int) or kwargs["token"].isdigit():
                    __id = int(kwargs["token"])
                else:
                    __id = self.trc10_db.get_token(token=kwargs["token"])
                    if __id == 0:
                        raise RuntimeError("Token not found")
                values["token"] = self.node.get_asset(id=__id)["id"]
            except ValueError as error:
                raise RuntimeError(str(error))
            except requests.exceptions.HTTPError as error:
                raise RuntimeError(str(error))
            except tronpy.exceptions.AssetNotFound as error:
                raise RuntimeError(str(error))
            except Exception as error:
                raise RuntimeError(str(error))

        return values
