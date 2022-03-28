from json import loads
from aio_pika import connect_robust, IncomingMessage, RobustConnection
from asyncio import sleep as async_sleep
from config import INTERNAL_RABBIT_URL
from src.external.es_send import send_msg_to_kibana, send_exception_to_kibana
from src.observer import observer
from worker.celery_app import celery_app


async def __processing_message(message: IncomingMessage):
    async with message.process():
        msg: dict = loads(message.body)
        address = msg['address']
        token = msg['token']
        can_go, wait_time = await observer.can_go(address)
        extra = {'countdown': wait_time} if not can_go and wait_time > 5 else {}
        celery_app.send_task(f'worker.celery_worker.send_transaction', args=[address, token], **extra)


async def init_sending_to_main_wallet(loop):
    while True:
        try:
            connection = None
            while connection is None or connection.is_closed:
                try:
                    connection: RobustConnection = await connect_robust(INTERNAL_RABBIT_URL, loop=loop)
                finally:
                    await send_msg_to_kibana(msg=f'WAIT CONNECT TO RABBITMQ - SendToMainWalletQueue')
                await async_sleep(2)

            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue("SendToMainWalletQueue", durable=True)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await __processing_message(message)
        except Exception as e:
            await send_exception_to_kibana(e, "ERROR INIT_SENDING_TO_MAIN_WALLET")
