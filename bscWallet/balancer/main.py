import asyncio
from src.init_sending_to_main_wallet import init_sending_to_main_wallet
from src.recive_fee_and_send_token import receive_fee_and_send_token


async def main(loop):
    await asyncio.sleep(10)
    await asyncio.gather(*[
        init_sending_to_main_wallet(loop),
        receive_fee_and_send_token(loop)
    ])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
