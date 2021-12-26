import os
import pika as rabbit
from config import logger


class RabbitMQ:
    """ Class for sending processed data """

    def send_message(self, values: list) -> None:
        """ Send message to RabbitMQ """
        message = "{}".format(values)
        logger.error(f'NEW TX: {message}')
        connection = None
        try:
            if os.getenv("isRabbitLocal") == "True":
                param = rabbit.ConnectionParameters(host="localhost")
            else:
                param = rabbit.URLParameters(url=os.getenv("RabbitMQURL"))
            connection = rabbit.BlockingConnection(param)
            channel = connection.channel()
            channel.queue_declare(queue=os.getenv("Queue"), durable=True)
            channel.basic_publish(
                exchange='',
                routing_key=os.getenv("Queue"),
                body=message,
                properties=rabbit.BasicProperties(delivery_mode=2)
            )
        except Exception as e:
            raise e
        finally:
            if connection is not None:
                connection.close()
