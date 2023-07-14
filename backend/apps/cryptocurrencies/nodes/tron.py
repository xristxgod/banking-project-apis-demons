from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from apps.cryptocurrencies.models import Network
from apps.cryptocurrencies.nodes.base import AbstractNode


class Node(AbstractNode):
    def __init__(self, network: Network):
        self.provider = AsyncHTTPProvider(
            endpoint_uri=network.url,
        )
        self.client = AsyncTron(
            provider=self.provider,
        )

    async def get_balance(self, address: str) -> int:
        account = await self.client.get_account(address)
        return account.get("balance", 0)

    async def get_latest_block_number(self) -> int:
        return await self.client.get_latest_block_number()

    async def get_block(self, block_number: int) -> dict:
        return await self.client.get_block(block_number, visible=True)
