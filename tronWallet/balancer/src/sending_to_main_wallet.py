import json
from typing import Dict

from aio_pika import connect_robust, IncomingMessage, RobustConnection, Channel
from asyncio import sleep as async_sleep

from src.utils.types import TronAccountAddress, TokenTRC20
from src.utils.es_send import send_msg_to_kibana, send_exception_to_kibana
from src.services.to_main_wallet_native import send_to_main_wallet_native
from src.services.to_main_wallet_token import send_to_main_wallet_token
from config import logger, rabbit_url, queue, ReportingAddress, AdminAddress

adminAddresses = [AdminAddress, ReportingAddress]


async def send_to_main_wallet(address: TronAccountAddress, token: TokenTRC20):
    if address in adminAddresses:
        return None
    if token.lower() in [None, "trx", "tron"]:
        logger.error(f"--> TRX | Address: {address} | Received from RabbitMQ")
        await send_msg_to_kibana(msg=f"TRX | Address: {address} | Preparing to empty the balance")
        await send_to_main_wallet_native(address=address)
    else:
        logger.error(f"--> {token.upper()} | Address: {address} | Received from RabbitMQ")
        await send_msg_to_kibana(msg=f"{token.upper()} | Address: {address} | Preparing to empty the balance")
        await send_to_main_wallet_token(address=address, token=token)


async def __processing_message(message: IncomingMessage):
    """
    Decrypt the message from the queue and send it for forwarding.
    :param message: Message from queue
    """
    async with message.process():
        # The message in the queue looks like this: {"address": "TronWalletAddress", "token": "TokenSymbolORTRX"}
        msg: Dict = json.loads(message.body)
        logger.error(f"Get init msg: {msg}")
        if len(msg) == 1:
            address: TronAccountAddress = msg[0]["address"]
            token: TokenTRC20 = msg[0]["token"] if "token" in msg[0] else None
            await send_to_main_wallet(address=address, token=token)
        else:
            for m in msg:
                address: TronAccountAddress = m["address"]
                token: TokenTRC20 = m["token"] if "token" in m else None
                await send_to_main_wallet(address=address, token=token)


async def sending_to_main_wallet(loop):
    while True:
        try:
            connection = None
            while connection is None or connection.is_closed:
                try:
                    # Connect to RabbitMQ by url
                    connection: RobustConnection = await connect_robust(rabbit_url, loop=loop)
                finally:
                    logger.error(f'WAIT CONNECT TO RABBITMQ')
                await async_sleep(2)
            async with connection:
                # Connect to the RabbitMQ channel
                channel: Channel = await connection.channel()
                # Connections to the queue in RabbitMQ by name.
                __queue = await channel.declare_queue(queue, durable=True)
                async with __queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await __processing_message(message=message)
        except Exception as error:
            logger.error(f"--> Error | SENDING_TO_MAIN_WALLET: {error}")
            await send_exception_to_kibana(error, "ERROR: SENDING_TO_MAIN_WALLET")
