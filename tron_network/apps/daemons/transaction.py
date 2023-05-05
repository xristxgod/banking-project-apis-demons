from core import Node


class Core:
    async def get_last_block_number(self) -> str:
        # From cache
        pass

    async def save_last_block_number(self) -> str:
        # To cache
        pass


class Daemon:
    def __init__(self):
        self.core = Node()
        self.node = self.core.node

    def parsing_block(self, block_number: int):
        pass

    def parsing_transaction(self):
        pass

    def handler(self):
        pass
