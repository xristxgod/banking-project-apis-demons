from core.crypto.node import Node

__all__ = (
    'BaseNodeService',
)


class BaseNodeService:
    def __init__(self, *args, **kwargs):
        self.core = Node()
        self.node = self.core.node
