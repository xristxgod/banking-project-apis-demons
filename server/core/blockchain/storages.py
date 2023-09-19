from typing import Optional

import settings
from config.redis import RedisConnector


class BlockNumberStorage:
    def __init__(self, storage_name: str):
        self._key = storage_name
        self._storage = RedisConnector(uri=settings.DAEMON_STORAGE_BACKEND_URL)

    async def set(self, block_number: int):
        await self._storage.async_set(key=self._storage, value=block_number)

    async def get(self) -> Optional[int]:
        return await self._storage.async_get(key=self._storage)
