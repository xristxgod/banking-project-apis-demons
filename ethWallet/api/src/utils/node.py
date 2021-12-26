import os
import json
from dotenv import load_dotenv

import web3.exceptions
import web3.contract
from web3 import Web3, HTTPProvider

from src.utils.utils import ERC20_ABI
from src.utils.tokens_database import TokenDB

load_dotenv()


class NodeETH:
    db = TokenDB()
    abi = ERC20_ABI

    def __init__(self):
        self.node = Web3(HTTPProvider(
            os.environ.get("NodeURL", 'https://mainnet.infura.io/v3/7dc5bd3523794cd8acea7199da9e108e')
        ))

    def get_contract(self, symbol: str) -> web3.contract.Contract or bool:
        """Get a contract for a token, if it is in the system"""
        contract_address = self.db.get_token(symbol=symbol)
        if contract_address and contract_address is not None:
            try:
                address = self.node.toChecksumAddress(contract_address)
                contract = self.node.eth.contract(address=address, abi=self.abi)
                return contract
            except web3.exceptions.ContractLogicError:
                return False
            except web3.exceptions.ABIFunctionNotFound:
                return False
            except Exception:
                return False
        else:
            return False

    @property
    def is_connect(self) -> json:
        """Find out the stability of the connection"""
        return json.dumps({"status": self.node.isConnected()})

    @property
    def gas_price(self):
        """Get gas price"""
        return self.node.eth.gas_price
