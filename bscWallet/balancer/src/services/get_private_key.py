from ..external.db import DB


async def get_private_key(address: str):
    return await DB.get_private_key(address)
