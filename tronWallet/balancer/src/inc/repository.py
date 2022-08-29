import typing
import asyncio
from datetime import datetime, timedelta

from tronpy.tron import TAddress


lock = asyncio.Lock()


class Repository:
    """Repository - Serves for temporary storage of data for celery"""
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Repository, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.__addresses: typing.Dict[TAddress] = {}

    async def get(self, address: TAddress) -> typing.Tuple[bool, int]:
        async with lock:
            if address not in self.__addresses:
                self.__addresses.update({address: datetime.now()})
            seconds = (datetime.now() - self.__addresses[address]).seconds
            if seconds > 60:
                self.__addresses.update({address: datetime.now()})
                return True, 0
            else:
                self.__addresses.update({address: self.__addresses[address] + timedelta(seconds=60 - seconds)})
                return False, 60 - seconds


__all__ = [
    "Repository"
]
