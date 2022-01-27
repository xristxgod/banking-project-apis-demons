import aiohttp

from config import API_URL, logger


async def get_request(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{API_URL}/{url}') as resp:
                if not resp.ok:
                    logger.error(f'GET ERROR: {await resp.text()}')
                    return None
                response = await resp.json()
        return response
    except Exception as e:
        logger.error(f'ERROR POST REQUEST ({url}): {e}')
        return None


async def post_request(url: str, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{API_URL}/{url}', json=data) as resp:
                if not resp.ok:
                    logger.error(f'POST ERROR: {await resp.text()}. DATA: {data}')
                    return None
                response = await resp.json()
        return response
    except Exception as e:
        logger.error(f'ERROR POST REQUEST ({url}): {e}')
        return None
