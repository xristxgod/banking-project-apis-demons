from typing import Union, Dict

import aiohttp

from src.utils.es_send import send_exception_to_kibana
from config import API_URL, logger

async def post_request(url: str, **data) -> Union[Dict, None]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_URL}{url}", json=data) as resp:
                response = await resp.json()
        return response
    except Exception as error:
        logger.error(f"Error post request ({url}): {error}")
        await send_exception_to_kibana(error=error, msg="ERROR: POST REQUEST")
        return None

async def get_request(url: str) -> Union[Dict, None]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}{url}") as resp:
                response = await resp.json()
        return response
    except Exception as error:
        logger.error(f"Error get request ({url}): {error}")
        await send_exception_to_kibana(error=error, msg="ERROR: GET REQUEST")
        return None