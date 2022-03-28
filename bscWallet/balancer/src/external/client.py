import aiohttp
from config import API_URL
from src.external.es_send import send_error_to_kibana, send_exception_to_kibana


async def get_request(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{API_URL}/{url}') as resp:
                if not resp.ok:
                    await send_error_to_kibana(msg=f'GET ERROR: {await resp.text()}', code=-1)
                    return None
                response = await resp.json()
        return response
    except Exception as e:
        await send_exception_to_kibana(e, f'ERROR GET REQUEST ({url})')
        return None


async def post_request(url: str, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{API_URL}/{url}', json=data) as resp:
                if not resp.ok:
                    await send_error_to_kibana(msg=f'GET ERROR: {await resp.text()}', code=-1)
                    return None
                response = await resp.json()
        return response
    except Exception as e:
        await send_exception_to_kibana(e, f'ERROR POST REQUEST ({url})')
        return None
