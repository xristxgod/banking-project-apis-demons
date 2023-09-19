from tronpy.abi import tron_abi
from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from core.blockchain.models import Network
from core.blockchain.gates.base import AbstractNode


class Node(AbstractNode):

    @classmethod
    def encode_data(cls, func_args: tuple, params: tuple) -> str:
        return tron_abi.encode_single(func_args, params).hex()

    @classmethod
    def decode_data(cls, func_args: tuple, data: str) -> tuple:
        return tron_abi.decode_single(func_args, data=data)

    def __init__(self, network: Network):
        super().__init__(network)
        self.provider = AsyncHTTPProvider(endpoint_uri=network.node_url)
        self.client = AsyncTron(provider=self.provider)

    @property
    async def is_connect(self) -> bool:
        from httpx._exceptions import HTTPStatusError
        try:
            await self.client.list_nodes()
        except HTTPStatusError:
            return False
        else:
            return True

    async def get_latest_block_number(self) -> int:
        return await self.client.get_latest_block_number()

    async def get_block_detail(self, block_number: int) -> dict:
        return await self.client.get_block(id_or_num=block_number, visible=True)
