import os
from json import dumps
import pika as rabbit
from config import logger, SEND_TO_MAIN_WALLET_LIMIT


class RabbitMQ:
    """ Class for sending processed data """
    @staticmethod
    def send_founded_message(values) -> None:
        values = dumps(values)
        """ Send message to RabbitMQ """
        if os.getenv("isRabbitLocal") == "True":
            param = rabbit.ConnectionParameters(host="127.0.0.1")
        else:
            param = rabbit.URLParameters(url=os.getenv("RabbitMQURL"))
        connection = rabbit.BlockingConnection(param)
        channel = connection.channel()
        channel.queue_declare(queue=os.getenv("Queue"), durable=True)
        message = "{}".format(values)
        channel.basic_publish(
            exchange='',
            routing_key=os.getenv("Queue"),
            body=message,
            properties=rabbit.BasicProperties(delivery_mode=2)
        )
        logger.error(f'NEW TX: {message}')
        channel.close()
        connection.close()

    @staticmethod
    def request_for_sending_to_main_wallet(token: str, address: str):
        RabbitMQ.__send_to_internal_rabbit(
            dumps({"token": token, "address": address, 'limit': "%.18f" % SEND_TO_MAIN_WALLET_LIMIT}),
            'SendToMainWalletQueue'
        )

    @staticmethod
    def got_fee_for_sending_token_to_main_wallet(address: str):
        RabbitMQ.__send_to_internal_rabbit(
            dumps({"address": address, 'limit': "%.18f" % SEND_TO_MAIN_WALLET_LIMIT}),
            'ReceiveTokenAndSendToMainWalletQueue'
        )

    @staticmethod
    def __send_to_internal_rabbit(value, queue):
        logger.error(f'SEND TO {queue}: {value}')
        param = rabbit.URLParameters(url=os.getenv('INTERNAL_RABBIT_URL', "amqp://root:password@127.0.0.1:5672/"))
        connection = rabbit.BlockingConnection(param)
        channel = connection.channel()
        channel.queue_declare(queue, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=value,
            properties=rabbit.BasicProperties(delivery_mode=2)
        )
        channel.close()
        connection.close()
        logger.error(f'SENDED TO {queue}: {value}')
