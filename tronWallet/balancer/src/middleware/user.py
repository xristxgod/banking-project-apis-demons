import decimal
from typing import Optional, List
from dataclasses import dataclass, field

from tronpy.tron import TAddress

from ..external import DatabaseController
from ..inc import CoinController, core


@dataclass()
class Token:
    name: str                                           # Token name
    balance: decimal.Decimal = field(default=0)         # Token balance


@dataclass()
class User:
    address: TAddress                                   # Wallet address
    balanceNative: decimal.Decimal                      # Balance native
    tokens: List[Token]                                 # Tokens balance
    privateKey: Optional[str]                           # Wallet private key


class UserMiddleware:
    def __init__(self, user: User):
        self.__user = user

    @property
    def address(self) -> TAddress:
        return self.__user.address

    @property
    def private_key(self) -> str:
        return self.__user.privateKey

    @property
    def balance_native(self) -> decimal.Decimal:
        return self.__user.balanceNative

    @balance_native.setter
    def balance_native(self, value: float):
        self.__user.balanceNative = value

    @property
    def tokens(self) -> List[Token]:
        return self.tokens


async def middleware(address: TAddress) -> UserMiddleware:
    private_key: str = await DatabaseController.get_private_key(address=address)
    balance_native: decimal.Decimal = await core.get_account_balance(addr=address)
    tokens: List[Token] = []
    for coin in CoinController.get_all_token():
        contract = await core.get_contract(addr=coin.address)
        tokens.append(Token(
            name=coin.name,
            balance=int(await contract.functions.balanceOf(address)) / 10 ** coin.decimals
        ))
    return UserMiddleware(User(
        address=address,
        privateKey=private_key,
        balanceNative=balance_native,
        tokens=tokens
    ))


__all__ = [
    "UserMiddleware", "middleware"
]
