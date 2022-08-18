from typing import Optional
from dataclasses import dataclass, field

from tronpy.tron import TAddress

from src import core


@dataclass()
class Account:
    address: TAddress
    privateKey: Optional[str] = field(default=None)


class AccountController:
    def __init__(self, account: Account):
        self.__account = account

    def __str__(self):
        return f"<Account: {self.__account.address}>"

    def balance(self):
        pass
