import json
from typing import Any
from datetime import datetime, timedelta

import settings
from config.redis import RedisConnector
from core.common.caches.ram import Cache


class BaseCache(Cache):
    uri: str

    def setup(self):
        self._storage = RedisConnector(uri=self.uri)

    def _sync_get_actual_result(self, key: str, ttl: int | float) -> tuple:
        result, t = (None, datetime.min)
        if value := self._storage.sync_get(key):
            result, t = json.loads(value)

        if datetime.now() > t + timedelta(seconds=ttl):
            self._storage.sync_delete(key)
            result = None
        return result, t

    async def _async_get_actual_result(self, key: str, ttl: int | float) -> tuple:
        result, t = (None, datetime.min)
        if value := await self._storage.async_get(key):
            result, t = json.loads(value)

        if datetime.now() > t + timedelta(seconds=ttl):
            await self._storage.async_delete(key)
            result = None
        return result, t

    def _sync_set_actual_result(self, key: str, result: Any):
        self._storage.sync_set(key, json.dumps(result, default=str))

    async def _async_set_actual_result(self, key: str, result: Any):
        await self._storage.async_set(key, json.dumps(result, default=str))


class DefaultCached(BaseCache):
    uri = settings.CACHED_BACKEND_URL


cached = DefaultCached()
