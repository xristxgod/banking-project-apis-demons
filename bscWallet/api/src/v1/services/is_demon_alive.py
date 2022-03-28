import aiohttp
from config import NGINX_DOMAIN, logger
from src.utils.node import node_singleton


async def is_demon_alive():
    try:
        async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}) as session:
            async with session.get(f'{NGINX_DOMAIN}/get-last-block-file') as resp:
                text = await resp.text()
        if not text.isdigit():
            return False
        inside_block = int(text)
        node_block = node_singleton.node.eth.block_number
        return (node_block - inside_block) < 30
    except Exception as e:
        logger.error(f'ERROR: {e}')
        return False
