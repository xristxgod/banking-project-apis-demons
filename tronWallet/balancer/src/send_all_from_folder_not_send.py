import json
import os
from aio_pika import connect_robust, RobustConnection, Channel, Message

from src.utils.is_error import is_error
from config import rabbit_url, queue, logger, NOT_SEND

def send_all_from_folder_not_send():
    """Send those transits that were not sent due to any errors"""
    logger.error("--> Started looking for unsent transactions")
    files = os.listdir(NOT_SEND)
    for file_name in files:
        try:
            path = os.path.join(NOT_SEND, file_name)
            with open(path, 'r') as file:
                values = file.read()
            send_to_rabbit_mq(values=json.loads(values))
            os.remove(path)
        except Exception as error:
            logger.error(f"Error: {error}")
            logger.error(f"Not send: {file_name}")
            continue

async def send_to_rabbit_mq(values: dict):
    __connection = None
    try:
        __connection: RobustConnection = await connect_robust(
            url=rabbit_url
        )
        __channel: Channel = await __connection.channel()
        await __channel.declare_queue(queue, durable=True)
        await __channel.default_exchange.publish(
            message=Message(body=f"{values}".encode()),
            routing_key=queue
        )
    except Exception as error:
        logger.error(f"{error}")
        await is_error(value=values)
    finally:
        if __connection is not None:
            await __connection.close()
