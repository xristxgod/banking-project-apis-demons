from typing import Optional

from .services import AccountController
from ..schemas import BodyCreateTransaction


class Transaction:
    @staticmethod
    async def create(account: AccountController, body: BodyCreateTransaction, coin: Optional[str] = None):

        pass


class TransactionParser:
    pass
