import decimal
from typing import Optional

import aiohttp
from tronpy.tron import TAddress

from src import UserMiddleware, admin
from config import Config, decimals, logger


class UserTransaction:
    URLs = {
        "optimalFee": f"{Config.API_URL}/<network>/transaction/<fromAddress>/to/<toAddress>/fee",
        "createTransaction": ""
    }

    def __init__(self, user: UserMiddleware):
        self.user = user

    async def optimal_fee(self, address: TAddress, token: Optional[str] = None) -> decimal.Decimal:
        url = self.URLs.get("optimalFee")
        if token is None:
            url.replace("<network>", "tron")
        else:
            url.replace("<network>", f"tron_trc20_{token.lower()}")
        url.replace("<fromAddress>", self.user.address).replace("<toAddress>", address)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
        return decimals.create_decimal(result.get("fee", 0))

    async def create(self, address: TAddress, token: Optional[str] = None):
        pass



async def send_native(user: UserMiddleware) -> Optional:
    user_transaction = UserTransaction(user=user)
    amount = user.balance_native - (await user_transaction.optimal_fee(address=admin.address))
    if amount < Config.MIN_BALANCE_FOR_TRANSFER_NATIVE:
        logger.error((
            "The balance does not meet the minimum forwarding threshold. "
            f"Minimum threshold: {Config.MIN_BALANCE_FOR_TRANSFER_NATIVE}"
        ))
        return




async def send_token(user: UserMiddleware, token: str):
    pass


async def worker(user: UserMiddleware, token: str) -> Optional:
    if token.lower() in ["tron", "trx"]:
        await send_native(user=user)
    else:
        await send_token(user=user, token=token)
