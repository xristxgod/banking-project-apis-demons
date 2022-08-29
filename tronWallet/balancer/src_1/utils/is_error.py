from typing import Dict
from aiofiles import open as async_open
import json
import os
import uuid
import pika as rabbit
from config import NOT_SEND, rabbit_url, queue


async def is_error(value: Dict):
    new_not_send_file = os.path.join(NOT_SEND, f'{uuid.uuid4()}.json')
    async with async_open(new_not_send_file, 'w') as file:
        # Write all the verified data to a json file, and do not praise the work
        await file.write(str(value))
    if isinstance(value, dict) and "address" in dict.keys():
        send_again(value=value)


def send_again(value: Dict):
    message = "{}".format(json.dumps(value))
    __connection = None
    try:
        __param = rabbit.URLParameters(url=rabbit_url) if rabbit_url != "localhost" \
            else rabbit.ConnectionParameters(host=rabbit_url)
        __connection = rabbit.BlockingConnection(parameters=__param)
        __channel = __connection.channel()
        __channel.queue_declare(queue=queue, durable=True)
        __channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=message.encode(),
            properties=rabbit.BasicProperties(delivery_mode=2)
        )
    except Exception as error:
        raise error
    finally:
        if __connection is not None:
            __connection.close()
