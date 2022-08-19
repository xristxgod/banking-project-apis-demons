from typing import Optional

from tronpy.tron import Tron

from .services import AccountController
from ..schemas import BodyCreateTransaction


class Transaction:
    @staticmethod
    async def create(account: AccountController, body: BodyCreateTransaction, coin: Optional[str] = None):
        to_address, to_amount = list(body.outputs[0].items())[0]
        pass


class TransactionParser:
    pass
