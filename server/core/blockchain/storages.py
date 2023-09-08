from typing import Optional


class BlockNumberStorage:
    def __init__(self, storage_name: str):
        pass

    async def set(self, block_number: int):
        pass

    async def get(self) -> Optional[int]:
        pass
