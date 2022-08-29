from typing import Optional
from enum import Enum

from .middleware import UserMiddleware


class TransactionStatus(Enum):
    successfully = 0
    notFee = 1
    notBalance = 2
    otherError = 3


class UserTransaction:
    def __init__(self, user: UserMiddleware):
        self.user = user
        self.transaction = None

    def create(self, token: Optional[str] = None) -> TransactionStatus:
        pass

    def send(self):
        pass
