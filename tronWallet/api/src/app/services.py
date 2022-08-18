from typing import Optional
from dataclasses import dataclass, field

import tronpy.exceptions
from tronpy.tron import TAddress

from src import core
from ..base import BaseController
from ..external import CoinController
from ..schemas import ResponseBalance
from config import Config


@dataclass()
class Account:
    address: TAddress
    privateKey: Optional[str] = field(default=None)


class AccountController(BaseController):
    def __init__(self, account: Account):
        self.__account = account

    def __str__(self):
        return f"<Account: {self.__account.address}>"

    @property
    def address(self) -> str:
        return self.__account.address

    @property
    def private_key(self) -> str:
        return self.__account.privateKey

    async def balance(self, coin: Optional[str] = None) -> ResponseBalance:
        result = 0
        if coin is None:
            try:
                result = core.node.get_account_balance(addr=self.address)
            except tronpy.exceptions.AddressNotFound:
                pass
        else:
            coin = CoinController.get_token(coin)
            contract = await core.node.get_contract(addr=coin.address)
            if int(await contract.functions.balanceOf(self.address)) > 0:
                result = int(await contract.functions.balanceOf(self.address)) / 10 ** coin.decimals
        return ResponseBalance(
            balance=result
        )


admin = AccountController(account=Account(
    address=Config.ADMIN_WALLET_ADDRESS,
    privateKey=Config.ADMIN_WALLET_PRIVATE_KEY
))