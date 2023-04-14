from typing import Optional
from dataclasses import dataclass, field

import tronpy.exceptions
from tronpy.tron import TAddress

from src import core
from ..external import CoinController
from ..schemas import ResponseBalance
from config import Config


@dataclass()
class Account:
    address: Optional[TAddress] = field(default=None)
    privateKey: Optional[str] = field(default=None)


class AccountController:
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
        if coin is None or CoinController.is_native(coin=coin):
            try:
                result = await core.node.get_account_balance(addr=self.address)
            except tronpy.exceptions.AddressNotFound:
                pass
        else:
            coin = await CoinController.get_token(coin)
            contract = await core.node.get_contract(addr=coin.address)
            if int(await contract.functions.balanceOf(self.address)) > 0:
                result = int(await contract.functions.balanceOf(self.address)) / 10 ** coin.decimals
        return ResponseBalance(
            balance=result
        )

    async def optimal_fee(self, address: TAddress, coin: Optional[str] = None) -> float:
        fee, energy, bandwidth = 0, 0, 0
        if coin is None:
            try:
                _ = await core.node.get_account(address)
            except tronpy.exceptions.AddressNotFound:
                fee += 1
            bandwidth += 267
        else:
            coin = await CoinController.get_token(coin)
            if (await self.balance(coin.symbol)).balance > 0:
                energy += coin.fullEnergy
            else:
                energy += coin.notEnergy
            fee += await core.get_energy(self.address, energy=energy) / await core.calculate_burn_energy(1)
            bandwidth += coin.bandwidth
        if int((await core.get_account_bandwidth(self.address))["totalBandwidth"]) <= bandwidth:
            fee += 267 / 1_000
        return fee


admin = AccountController(account=Account(
    address=Config.ADMIN_WALLET_ADDRESS,
    privateKey=Config.ADMIN_WALLET_PRIVATE_KEY
))


__all__ = [
    "AccountController", "Account", "admin"
]
