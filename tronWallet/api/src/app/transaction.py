from typing import Optional

from tronpy.tron import Tron

from src import core
from .services import AccountController
from ..schemas import BodyCreateTransaction


class Transaction:
    @staticmethod
    async def create(account: AccountController, body: BodyCreateTransaction, coin: Optional[str] = None):
        to_address, amount = list(body.outputs[0].items())[0]
        amount = core.utils.to_sun(float(amount))
        resources = await account.optimal_fee(to_address)
        transaction = await core.node.trx.transfer(account.address, to=to_address, amount=amount)
        await transaction.build()
        return


class TransactionParser:
    pass
