import asyncio

from art import tprint

from app import Balancer
from config import logger


async def main(loop: asyncio.AbstractEventLoop):
    """Run balancer"""
    await asyncio.sleep(20)
    await asyncio.gather(*[
        Balancer().run(loop)
    ])


if __name__ == '__main__':
    tprint("TRON BALANCER", font="bulbhead")
    loop = None
    try:
        logger.error("START BALANCER")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(loop=loop))
        loop.close()
    except Exception as error:
        logger.error(f"ERROR: {error}")
    finally:
        logger.error("STOP BALANCER")
        if loop is not None and not loop.is_closed():
            loop.close()