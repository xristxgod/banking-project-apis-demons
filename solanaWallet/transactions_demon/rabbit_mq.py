import asyncio
import os
import aio_pika
from typing import Optional
from config import logger
import aiofiles


class RabbitMQ:
    """ Class for sending processed data """

    def __init__(self):
        """ Connect to RabbitMQ """
        self._connection: Optional[aio_pika.Connection] = None
        self.__channel: Optional[aio_pika.Channel] = None
        self.__queue_name = os.getenv("Queue")

    async def connect(self):
        try:
            if self._connection is None:
                self._connection = await aio_pika.connect_robust(
                    url="amqp://test:test@127.0.0.1/"
                    if os.getenv("isRabbitLocal") == "True"
                    else os.getenv("RabbitMQURL")
                )
                self.__channel: aio_pika.Channel = await self._connection.channel()
                await self.__channel.declare_queue(self.__queue_name)
            return True
        except Exception as e:
            logger.error(f'RABBIT MQ INIT ERROR: {e}')
            return False

    async def send_message(self, values: list) -> None:
        """ Send message to RabbitMQ """
        try:
            await self.__channel.default_exchange.publish(
                message=aio_pika.Message(body=f"{values}".encode()),
                routing_key=self.__queue_name,
            )
            return True
        except Exception as e:
            logger.error(f'RABBIT MQ SEND ERROR: {e}')
            async with aiofiles.open('backup.json', 'a') as file:
                await file.write(f'{values}\n')
            return False

    async def close_channel(self):
        """ Close channel and connection """
        await self.__channel.close()
        await self._connection.close()
