import eth_abi
from web3 import AsyncWeb3, AsyncHTTPProvider

from core.blockchain.models import Network
from core.blockchain.gates.base import AbstractNode


class Node(AbstractNode):
    @classmethod
    def encode_data(cls, func_args: tuple, params: tuple) -> str:
        return eth_abi.encode(func_args, params).hex()

    @classmethod
    def decode_data(cls, func_args: tuple, data: str) -> tuple:
        return eth_abi.decode(func_args, data=data)

    def __init__(self, network: Network):
        super().__init__(network)
        self.provider = AsyncHTTPProvider(endpoint_uri=network.node_url)
        self.client = AsyncWeb3(provider=self.provider)

    @property
    async def is_connect(self) -> bool:
        return await self.client.is_connected()

    async def get_latest_block_number(self) -> int:
        return await self.client.eth.get_block_number

    async def get_block_detail(self, block_number: int) -> dict:
        return await self.client.eth.get_block(
            block_identifier=block_number,
            full_transactions=True,
        )
