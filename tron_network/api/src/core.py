from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from src.settings import settings


class Node:
    def __new__(cls, *args, **kwargs):
        pass

    def __init__(self):
        self._node = AsyncTron(provider=AsyncHTTPProvider(settings.NODE_URL))

    @property
    def node(self) -> AsyncTron:
        return self._node
