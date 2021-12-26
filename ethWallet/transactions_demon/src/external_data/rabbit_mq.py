import os
import pika as rabbit
from config import logger


class RabbitMQ:
    """ Class for sending processed data """

    def __init__(self):
        """ Connect to RabbitMQ """
        if os.getenv("isRabbitLocal") == "True":
            self.param = rabbit.ConnectionParameters(host="localhost")
        else:
            self.param = rabbit.URLParameters(url=os.getenv("RabbitMQURL"))
        try:
            pass
            self._connection = rabbit.BlockingConnection(self.param)
        except Exception as e:
            raise RuntimeError("Error: Step 55 {}".format(e))
        self._channel = self._connection.channel()

    def send_message(self, values: list) -> None:
        """ Send message to RabbitMQ """
        self._channel.queue_declare(queue=os.getenv("Queue"), durable=True)
        message = "{}".format(values)
        self._channel.basic_publish(
            exchange='',
            routing_key=os.getenv("Queue"),
            body=message,
            properties=rabbit.BasicProperties(delivery_mode=2)
        )
        print('Data has been sent to the queue: {}'.format(os.getenv("Queue")))

    def close_channel(self):
        """ Close channel and connection """
        self._channel.close()
        self._connection.close()
