from json import loads, dumps
from os import environ

from aio_pika import connect_robust, IncomingMessage, RobustConnection, Message
from asyncio import sleep as async_sleep

from config import tokens, INTERNAL_RABBIT_URL
from src.external.es_send import send_msg_to_kibana, send_exception_to_kibana
from src.services.get_balance import get_balance
from src.services.to_main_wallet_token import is_dust


async def post_to_send_to_main_wallet_queue(value: str):
    connection = await connect_robust(environ.get('INTERNAL_RABBIT_URL', "amqp://root:password@127.0.0.1:5672/"))
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            Message(body=value.encode()), routing_key="SendToMainWalletQueue"
        )


async def __processing_message(message: IncomingMessage):
    async with message.process():
        msg: dict = loads(message.body)
        address = msg['address']
        for token in await tokens.get_tokens():
            balance = await get_balance(address=address, token=token)
            if not await is_dust(balance, token):
                await post_to_send_to_main_wallet_queue(dumps({"token": token, **msg}))


async def receive_fee_and_send_token(loop):
    while True:
        try:
            connection = None
            while connection is None or connection.is_closed:
                try:
                    connection: RobustConnection = await connect_robust(INTERNAL_RABBIT_URL, loop=loop)
                finally:
                    await send_msg_to_kibana(msg=f'WAIT CONNECT TO RABBITMQ - ReceiveTokenAndSendToMainWalletQueue')
                await async_sleep(2)

            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue("ReceiveTokenAndSendToMainWalletQueue", durable=True)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await __processing_message(message)
        except Exception as e:
            await send_exception_to_kibana(e, f'ERROR RECEIVE_FEE_AND_SEND_TOKEN')
