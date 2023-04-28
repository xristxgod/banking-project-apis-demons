
from .node import Node
from .contract import Contract


class NodeController:
    def __init__(self):
        self.core = Node()

    async def update(self):
        await self.core.update_contracts()

    def has_currency(self, currency: str) -> bool:
        return self.core.contracts.get(currency) is not None


controller = NodeController()
