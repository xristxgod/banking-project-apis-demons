from typing import Union

from src_1.external.db import get_private_key as get_private
from src_1.utils.types import TronAccountAddress, TronAccountPrivateKey


async def get_private_key(address: TronAccountAddress) -> Union[TronAccountPrivateKey, None]:
    return await get_private(address=address)

