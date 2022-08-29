import asyncio
from src_1.sending_to_main_wallet import sending_to_main_wallet

async def main(loop):
    await asyncio.gather(*[
        sending_to_main_wallet(loop)
    ])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()