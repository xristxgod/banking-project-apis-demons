import os
from dotenv import load_dotenv
import web3.contract
from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth
from web3.middleware import geth_poa_middleware
from config import logger
from src.utils.utils import ERC20_ABI
from src.utils.tokens_database import TokenDB

load_dotenv()


class NodeBSC:
    db = TokenDB()
    abi = ERC20_ABI

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NodeBSC, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.async_node = Web3(
            AsyncHTTPProvider(
                os.environ.get("NodeURL", 'https://data-seed-prebsc-2-s3.binance.org:8545/')
            ),
            modules={'eth': (AsyncEth,)},
            middlewares=[]
        )
        self.node = Web3(
            HTTPProvider(os.environ.get("NodeURL", 'https://data-seed-prebsc-2-s3.binance.org:8545/')),
        )
        self.node.middleware_onion.inject(geth_poa_middleware, layer=0)

    async def get_contract(self, symbol: str) -> web3.contract.Contract or bool:
        """Get a contract for a token, if it is in the system"""
        contract_address = await self.db.get_token(symbol=symbol)
        if contract_address and contract_address is not None:
            try:
                address = self.async_node.toChecksumAddress(contract_address)
                contract = self.node.eth.contract(address=address, abi=self.abi)
                return contract
            except Exception as e:
                logger.error(f'GET CONTACT ERROR: {e}')
                return False
        else:
            return False

    async def is_connect(self):
        """Find out the stability of the connection"""
        return {"status": await self.async_node.isConnected() and self.node.isConnected()}

    @property
    def gas_price(self):
        """Get gas price"""
        return self.async_node.eth.gas_price


node_singleton = NodeBSC()
