import pika
from config import INTERNAL_RABBIT_URL


async def is_balancer_alive():
    try:
        pika_conn_params = pika.URLParameters(url=INTERNAL_RABBIT_URL)
        connection = pika.BlockingConnection(pika_conn_params)
        channel = connection.channel()
        queue_1 = channel.queue_declare(
            queue="SendToMainWalletQueue", durable=True,
            exclusive=False, auto_delete=False
        )
        queue_2 = channel.queue_declare(
            queue="ReceiveTokenAndSendToMainWalletQueue", durable=True,
            exclusive=False, auto_delete=False
        )
        q_1 = queue_1.method.message_count
        q_2 = queue_2.method.message_count
        connection.close()
        return (q_1 < 20) and (q_2 < 20)
    except:
        return False
