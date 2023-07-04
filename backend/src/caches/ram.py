from datetime import timedelta

from django.utils import timezone

from src.meta import Singleton

__all__ = (
    'cached',
)


class CashedStorage(metaclass=Singleton):
    def __init__(self):
        self.storage = {}

    def cached(self, name: str, ttl: float):
        def decorator(function):
            async def wrapper(*args, **kwargs):
                index = name.format(*args, **kwargs)
                now = timezone.now()
                if index in self.storage.keys():
                    is_yesterday = self.storage[index]['time'].day < now.day
                    if not is_yesterday or self.storage[index]['time'] + self.storage[index]['ttl'] < now:
                        return self.storage[index]['value']

                value = await function(*args, **kwargs)
                self.storage[index] = {
                    'time': now,
                    'ttl': timedelta(seconds=ttl),
                    'value': value
                }
                return value
            return wrapper
        return decorator

    def __call__(self, name: str, ttl: float):
        return self.cached(name=name, ttl=ttl)


cached = CashedStorage()
