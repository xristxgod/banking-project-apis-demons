from typing import Tuple

import pika
import requests

from src import core
from .services import admin
from ..schemas import ResponseStatus, ResponseBlock, ResponseBalance, ResponseMessageCount
from config import Config


class Stabilizer:
    @staticmethod
    def node() -> Tuple[ResponseStatus, ResponseBlock]:
        status = True, None
        if Config.NETWORK == "MAINNET":
            our_node = core.node
            public_node = await core.utils.get_public_node()
            if int((await our_node.get_node_info())["activeConnectCount"]) == 0:
                # If there are no active connections to the node, then the node is dead!
                status = False, "Problems with the node. There are no active connections"
            our_block, public_block = await our_node.get_latest_block_number(), await public_node.get_latest_block_number()
            if (our_block != public_block) or (public_block - our_block > 20):
                status = False, "The blocks in the node are moving too slowly"
        else:
            block = await core.node.get_latest_block_number()
            our_block, public_block = block, block
        return ResponseStatus(
            message=status[1], successfully=status[0]
        ), ResponseBlock(
            ourBlock=our_block, publicBlock=public_block
        )

    @staticmethod
    async def balance() -> Tuple[ResponseStatus, ResponseBalance]:
        status = True, None
        balance = admin.balance()
        if balance <= Config.MIN_BALANCE:
            status = False, f"Admin balance equal to {balance}"
        return ResponseStatus(
            message=status[1], successfully=status[0]
        ), ResponseBalance(
            balance=balance
        )

    @staticmethod
    async def demon() -> Tuple[ResponseStatus, ResponseBlock]:
        status = True, None
        demon_last_block = int(requests.request("GET", f"{Config.NGINX_DOMAIN}/get-last-block-file").text)
        node_last_block = core.node.get_latest_block_number()
        if (node_last_block != demon_last_block) or (node_last_block - demon_last_block > 25):
            status = False, f"The allowable gap is 25, your gap is {node_last_block - demon_last_block}"
        return ResponseStatus(
            message=status[1], successfully=status[0]
        ), ResponseBlock(
            ourBlock=demon_last_block, publicBlock=node_last_block
        )

    @staticmethod
    async def balancer() -> Tuple[ResponseStatus, ResponseMessageCount]:
        connection = None
        status = True, None
        try:
            connection = pika.BlockingConnection(pika.URLParameters(url=Config.RABBITMQ_URL))
            channel = connection.channel()
            queue = channel.queue_declare(queue=Config.BALANCER_QUEUE, durable=True, exclusive=False, auto_delete=False)
            message_count = queue.method.message_count
        except Exception as error:
            message_count = 0
            status = False, f"{error}"
        finally:
            if connection is not None:
                connection.close()
        if message_count >= Config.MAX_BALANCER_MESSAGE:
            status = False, (
                f"The number of messages in the queue exceeds {Config.MAX_BALANCER_MESSAGE}."
                f" Number of messages: {message_count}"
            )
        return ResponseStatus(
            message=status[1], successfully=status[0]
        ), ResponseMessageCount(
            messageCount=message_count
        )


async def get_status(system: str = "node") -> Tuple:
    if system in [method for method in Stabilizer.__dict__ if not method.startswith("_") and not method.endswith("_")]:
        return await Stabilizer().__getattribute__(system)()
    raise Exception("There is no such method!")


__all__ = [
    "get_status"
]
