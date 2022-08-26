import json
from typing import Optional, List, Tuple
from dataclasses import asdict

import aio_pika

from .elastic import ElasticController
from ..utils import Utils
from ..schemas import BalancerMessage, Header, BodyTransaction
from config import Config, logger


class MessageBroker:

    @staticmethod
    async def send(data: json, query: str) -> Optional:
        connection: Optional[aio_pika.Connection] = None
        channel: Optional[aio_pika.Channel]
        try:
            connection = await aio_pika.connect_robust(url=Config.RABBITMQ_URL)
            channel = await connection.channel()
            await channel.declare_queue(query)
            await channel.default_exchange.publish(message=aio_pika.Message(body=data), routing_key=query)
        except Exception as error:
            logger.error(f"{error}")
        finally:
            if connection is not None:
                await connection.close()


class Balancer:
    """Work to balancer"""
    @staticmethod
    async def send(data: BalancerMessage) -> Optional:
        logger.error("Send to balancer message")
        await ElasticController.send_message(f"Send to balancer message: {asdict(data)}")
        await MessageBroker.send(data=json.dumps(asdict(data), default=Utils.json_default), query=Config.BALANCER_QUEUE)


class MainApp:
    """Work to main app"""
    @staticmethod
    async def send(data: List[Header, List[BodyTransaction]]) -> Optional:
        logger.error("Send to main app message")
        result = []
        for d in data:
            if not isinstance(d, list):
                result.append(asdict(d))
            else:
                result.append(asdict(d[0]))
        await ElasticController.send_message(f"Send to main app message: {result}")
        await MessageBroker.send(data=json.dumps(result, default=Utils.json_default), query=Config.BALANCER_QUEUE)


__all__ = [
    "Balancer", "MainApp"
]
