from dotenv import load_dotenv
import web3.contract
from web3 import Web3, AsyncHTTPProvider, HTTPProvider
from web3.eth import AsyncEth
from web3.middleware import geth_poa_middleware
from config import NODE_URL
from src.utils.es_send import send_exception_to_kibana
from src.utils.utils import ERC20_ABI
from src.utils.tokens_database import TokenDB


class NodeBSC:
    db = TokenDB()
    abi = ERC20_ABI

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NodeBSC, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.async_node = Web3(AsyncHTTPProvider(NODE_URL), modules={'eth': (AsyncEth,)}, middlewares=[])
        self.node = Web3(HTTPProvider(NODE_URL),)
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
                await send_exception_to_kibana(e, 'GET CONTACT ERROR')
                return False
        else:
            return False

    async def is_connect(self):
        """Find out the stability of the connection"""
        return {"status": self.node.isConnected()}

    @property
    def gas_price(self):
        """Get gas price"""
        return self.async_node.eth.gas_price


node_singleton = NodeBSC()
