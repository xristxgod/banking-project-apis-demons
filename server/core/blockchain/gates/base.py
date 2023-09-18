import abc

from core.blockchain.models import Network


class AbstractNode(metaclass=abc.ABCMeta):
    __slots__ = (
        'network',
        'provider',
        'client',
    )

    @abc.abstractclassmethod
    def encode_data(cls, func_args: tuple, params: tuple) -> str: ...

    @abc.abstractclassmethod
    def decode_data(cls, func_args: tuple, data: str) -> tuple: ...

    def __init__(self, network: Network):
        self.network = network

    @abc.abstractproperty
    async def is_connect(self) -> bool: ...

    @abc.abstractmethod
    async def get_latest_block_number(self) -> int: ...

    @abc.abstractmethod
    async def get_block_detail(self, block_number: int) -> dict: ...
