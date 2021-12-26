import json

import pika as rabbit

from transactions_demon.config import RabbitMQURL, logger, Queue

def send_message(values: json) -> None:
    """Send transactions to RabbitMQ"""
    message = "{}".format(values)
    logger.error(f"New TX in Block: {json.loads(message)[0]['block']}")
    __connection = None
    try:
        __param = rabbit.URLParameters(url=RabbitMQURL) if RabbitMQURL != "localhost"\
            else rabbit.ConnectionParameters(host=RabbitMQURL)

        __connection = rabbit.BlockingConnection(parameters=__param)
        __channel = __connection.channel()
        __channel.queue_declare(queue=Queue, durable=True)
        __channel.basic_publish(
            exchange="",
            routing_key=Queue,
            body=message.encode(),
            properties=rabbit.BasicProperties(delivery_mode=2)
        )
    except Exception as error:
        raise error
    finally:
        if __connection is not None:
            __connection.close()