from typing import Optional, Dict
from dataclasses import dataclass, field

from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from config import Config


PUBLIC_TRON_GRID_KEY = "16c3b7ca-d498-4314-aa1d-a224135faa26"


@dataclass()
class Temporary:
    node: AsyncTron
    iterations: int = field(default=20)


class Core:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Core, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.__node = AsyncTron(
            provider=AsyncHTTPProvider(Config.NODE_URL) if Config.NETWORK.upper() == "MAINNET" else None,
            network="mainnet" if Config.NETWORK.upper() == "MAINNET" else "shasta"
        )
        self.__temporary: Optional[Temporary] = None

    def __del__(self):
        if self.__temporary is not None:
            await self.__temporary.node.close()
            del self.__temporary
        if self.__node is not None:
            await self.__node.close()
            del self.__node

    @property
    def network(self) -> str:
        return Config.NETWORK

    @property
    def url(self) -> str:
        return self.__node.provider.endpoint_uri

    @property
    def node(self) -> AsyncTron:
        if self.__temporary is not None and self.__temporary.iterations > 0:
            self.__temporary.iterations -= 1
            return self.__temporary.node
        if self.__temporary is not None and self.__temporary.iterations <= 0:
            self.__temporary = None
        return self.__node

    def update(self, iterations: int = 20) -> Optional:
        if self.__temporary is None:
            self.__temporary = Temporary(
                node=AsyncTron(
                    provider=AsyncHTTPProvider(api_key=PUBLIC_TRON_GRID_KEY) if Config.NETWORK.upper() == "MAINNET" else None,
                    network="mainnet" if Config.NETWORK.upper() == "MAINNET" else "shasta"
                ),
                iterations=iterations
            )
        else:
            self.__temporary.iterations += 20
