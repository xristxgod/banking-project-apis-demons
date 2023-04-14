import asyncio
from typing import Optional

import aiofiles
from hdwallet import HDWallet, symbols
from mnemonic.mnemonic import Mnemonic

from src.settings import settings


LOCK = asyncio.Lock()


class WalletIndex:
    file_path = settings.WALLET_INDEX_FILE

    @classmethod
    async def get(cls) -> int:
        async with LOCK:
            async with aiofiles.open(cls.file_path, 'r') as file:
                response = await file.read()

        return int(response or '1')

    @classmethod
    async def set(cls, index: int):
        async with LOCK:
            async with aiofiles.open(cls.file_path, 'r') as file:
                await file.write(str(index))


async def create_wallet(is_admin: bool = True, mnemonic: Optional[str] = None) -> dict:
    hdwallet = HDWallet(symbols.TRX)

    if is_admin:
        hdwallet.from_mnemonic(settings.CENTRAL_WALLET['mnemonic'])
        hdwallet.from_index()
    else:
        mnemonic = mnemonic or Mnemonic(language='english').generate(256)
        hdwallet.from_mnemonic(mnemonic)
