from json import loads
from aio_pika import connect_robust, IncomingMessage, RobustConnection
from asyncio import sleep as async_sleep
from config import logger, INTERNAL_RABBIT_URL
from src.services.to_main_wallet_native import send_to_main_wallet_native
from src.services.to_main_wallet_token import send_to_main_wallet_token


async def __processing_message(message: IncomingMessage):
    async with message.process():
        msg: dict = loads(message.body)
        logger.error(f'GET INIT MSG: {msg}')
        address = msg['address']
        token = msg['token']

        if token in ['bnb', None]:
            await send_to_main_wallet_native(address)
        else:
            await send_to_main_wallet_token(address, token)


async def init_sending_to_main_wallet(loop):
    while True:
        try:
            connection = None
            while connection is None or connection.is_closed:
                try:
                    connection: RobustConnection = await connect_robust(INTERNAL_RABBIT_URL, loop=loop)
                finally:
                    logger.error(f'WAIT CONNECT TO RABBITMQ - SendToMainWalletQueue')
                await async_sleep(2)

            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue("SendToMainWalletQueue", durable=True)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await __processing_message(message)
        except Exception as e:
            logger.error(f"ERROR INIT_SENDING_TO_MAIN_WALLET: {e}")
