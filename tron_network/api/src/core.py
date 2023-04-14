from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from src.settings import settings


class Contract:
    pass


class Node:
    def __new__(cls, *args, **kwargs):
        pass

    def __init__(self):
        self.node = AsyncTron(
            provider=AsyncHTTPProvider(settings.NODE_URL),

        )