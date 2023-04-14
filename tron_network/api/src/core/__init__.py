
from .node import Node
from .contract import Contract


class NodeController:
    def __init__(self):
        self.core = Node()

    async def update(self):
        await self.core.update_contracts()


controller = NodeController()
