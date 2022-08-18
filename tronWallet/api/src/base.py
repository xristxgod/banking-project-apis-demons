from typing import Optional

from .schemas import ResponseBalance


class BaseController:
    @property
    def address(self) -> str:
        raise NotImplementedError

    @property
    def private_key(self) -> str:
        raise NotImplementedError

    async def balance(self, coin: Optional[str] = None) -> ResponseBalance:
        raise NotImplementedError


__all__ = [
    "BaseController"
]
