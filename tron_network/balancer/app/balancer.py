import json
import asyncio
from typing import Union, Optional, List, Dict, Coroutine

import aio_pika

from src.inc import Repository
from src.middleware import user_middleware
from worker import app
from config import Config, logger


class Balancer:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Balancer, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.repository = Repository()

    async def processing_message(self, message: aio_pika.IncomingMessage) -> Optional:
        """
        Decrypt the message from the queue and send it for forwarding.
        :param message: Message from queue
        """
        async with message.process():
            msg: Union[List[Dict], Dict] = json.loads(message.body)
            logger.info(f"Taking message: {msg}")
            if isinstance(msg, dict) and len(msg.keys()) == 2 and msg.get("address") is not None:
                address, token = msg.get("address"), msg.get("amount")
            can_go, wait_time = self.repository.get(address)
            extra = {"countdown": wait_time} if not can_go and wait_time > 5 else {}
            app.send_task(
                f'worker.celery_worker.send_transaction',
                args=[await user_middleware(address), token],
                **extra
            )

    async def run(self, loop: asyncio.AbstractEventLoop) -> Optional:
        while True:
            try:
                connection: Optional[aio_pika.RobustConnection] = None
                while connection is None or connection.is_closed:
                    try:
                        # Connect to RabbitMQ by url
                        connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
                            Config.RABBITMQ_URL, loop=loop
                        )
                    finally:
                        logger.info(f"Wait connect to RabbitMQ")
                    await asyncio.sleep(2)
                async with connection:
                    # Connect to the RabbitMQ channel
                    channel: aio_pika.Channel = await connection.channel()
                    # Connections to the queue in RabbitMQ by name.
                    __queue = await channel.declare_queue(Config.BALANCER_QUEUE, durable=True)
                    async with __queue.iterator() as queue_iter:
                        async for message in queue_iter:
                            await self.processing_message(message=message)
            except Exception as error:
                logger.error(f"{error}")


__all__ = [
    "Balancer"
]
