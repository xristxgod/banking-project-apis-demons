from asyncio import Lock
from datetime import datetime, timedelta


lock = Lock()


class Observer:
    def __init__(self):
        self._addresses = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Observer, cls).__new__(cls)
        return cls.instance

    async def can_go(self, address) -> (bool, int):
        async with lock:
            if address not in self._addresses:
                self._addresses.update({address: datetime.now()})
                return True, 0
            seconds = (datetime.now() - self._addresses[address]).seconds

            if seconds > 60:
                self._addresses.update({address: datetime.now()})
                return True, 0
            else:
                self._addresses.update({address: self._addresses[address] + timedelta(seconds=60 - seconds)})
                return False, 60 - seconds


observer = Observer()
