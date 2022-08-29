import random
import asyncio
from typing import Optional, Callable, List
from dataclasses import dataclass, field

import aiohttp
import tronpy.exceptions
from tronpy.async_tron import AsyncTron, AsyncHTTPProvider, TAddress

from .external import ElasticController
from config import Config, logger


URL_SEARCHER_TESTNET = "https://api.shasta.trongrid.io/v1/accounts/<address>/transactions?limit=200"
URL_SEARCHER_MAINNET = "https://api.mainnet.trongrid.io/v1/accounts/<address>/transactions?limit=200"
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

    def __getattr__(self, method) -> Optional[Callable]:
        try:
            if not hasattr(self.node, method):
                return None
            return getattr(self.node, method)
        except tronpy.exceptions.ApiError:
            logger.error("Something is wrong on the sending side!")
            self.update()
        except tronpy.exceptions.BugInJavaTron:
            logger.error("Something is wrong on the server for years!")
            self.update()

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
            logger.error(f"Problems with the main node! Check its performance!")
            await ElasticController.send_error(message="Problems with the main note! Check its performance!", code=1)
            self.__temporary = Temporary(
                node=AsyncTron(
                    provider=AsyncHTTPProvider(api_key=PUBLIC_TRON_GRID_KEY) if Config.NETWORK.upper() == "MAINNET" else None,
                    network="mainnet" if Config.NETWORK.upper() == "MAINNET" else "shasta"
                ),
                iterations=iterations
            )
        else:
            logger.error(f"The main node is still not working! Adding {iterations} more iterations")
            self.__temporary.iterations += 20


class SearchTransactionBlock:
    """Search all transactions"""
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SearchTransactionBlock, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        # Tron Grid public keys
        self.__keys = [
            "8d375175-fa31-490d-a224-63a056adb60b",
            "16c3b7ca-d498-4314-aa1d-a224135faa26",
            "a684fa6d-6893-4928-9f8e-8decd5f034f2"
        ]

    @property
    def keys(self) -> List[str]:
        return self.__keys

    async def search(self, addresses: List[TAddress]) -> List[int]:
        return await self.__search_blocks(addresses=addresses)

    async def __search_blocks(self, addresses: List[TAddress]) -> List[int]:
        unready_blocks = await asyncio.gather(*[
            self.__block_unpacking(address=address)
            for address in addresses
        ])
        blocks = []
        for block in unready_blocks:
            blocks.extend(block)
        return sorted(list(set(blocks)))

    async def __block_unpacking(self, address: TAddress) -> List[int]:
        headers = {"Accept": "application/json", "TRON-PRO-API-KEY": self.keys[random.randint(0, 2)]}
        if Config.NETWORK == "MAINNET":
            url = URL_SEARCHER_MAINNET
        else:
            url = URL_SEARCHER_TESTNET
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url=url.replace("<address>", address)) as response:
                result = await response.json()
        if "data" in result and len(result["data"]) == 0:
            return []
        return [int(i["blockNumber"]) for i in result["data"]]


__all__ = [
    "Core", "SearchTransactionBlock"
]