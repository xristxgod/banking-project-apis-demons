import json

import pika as rabbit

from config import RabbitMQURL, Queue, QueueBalancer


def send_message(values: json) -> None:
    """Send transactions to RabbitMQ"""
    message = "{}".format(values)
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


def send_to_balancer(values: json) -> None:
    message = "{}".format(values)
    __connection = None
    try:
        __param = rabbit.URLParameters(url=RabbitMQURL) if RabbitMQURL != "localhost" \
            else rabbit.ConnectionParameters(host=RabbitMQURL)
        __connection = rabbit.BlockingConnection(parameters=__param)
        __channel = __connection.channel()
        __channel.queue_declare(queue=QueueBalancer, durable=True)
        __channel.basic_publish(
            exchange="",
            routing_key=QueueBalancer,
            body=message.encode(),
            properties=rabbit.BasicProperties(delivery_mode=2)
        )

    except Exception as error:
        raise error
    finally:
        if __connection is not None:
            __connection.close()
