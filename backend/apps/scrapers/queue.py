from typing import Callable

import aio_pika


class Queue:
    def __init__(self):
        pass

    async def send(self, message: aio_pika.Message) -> bool:
        pass

    async def take(self, message_count: int = 1) -> list[aio_pika.Message]:
        pass

    async def attach(self, func: Callable):
        pass
