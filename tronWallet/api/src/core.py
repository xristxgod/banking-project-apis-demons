from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from config import Config


class NodeCore:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NodeCore, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.node = AsyncTron(
            provider=AsyncHTTPProvider(Config.NODE_URL) if Config.NETWORK.upper() == "MAINNET" else None,
            network=Config.NETWORK.lower()
        )

