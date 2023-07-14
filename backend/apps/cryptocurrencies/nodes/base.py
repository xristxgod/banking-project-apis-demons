import abc
from typing import Mapping


class AbstractNode(metaclass=abc.ABCMeta):
    __slots__ = (
        'client',
        'provider',
    )

    @abc.abstractmethod
    async def get_balance(self, address: str) -> int: ...

    @abc.abstractmethod
    async def get_latest_block_number(self) -> int: ...

    @abc.abstractmethod
    async def get_block(self, block_number: int) -> Mapping: ...
