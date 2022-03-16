from tronpy.tron import Tron, HTTPProvider
from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from src.utils.token_database import token_db
from src.utils.utils import from_sun, to_sun

from config import network, node

class NodeTron:
    # Provider config
    __provider = HTTPProvider(node)
    __async_provider = AsyncHTTPProvider(node)
    # Network
    network: str = network

    # Converts
    fromSun = staticmethod(from_sun)
    toSun = staticmethod(to_sun)

    # Token db
    db = token_db

    def __init__(self):
        """Connect to Tron Node"""
        self.node = Tron(
            provider=self.__provider if self.network == "mainnet" else None,
            network=self.network
        )
        self.async_node = AsyncTron(
            provider=self.__async_provider if self.network == "mainnet" else None,
            network=self.network
        )