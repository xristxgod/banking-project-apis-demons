import abc
import decimal
import functools
from typing import Any

from core.old_crypto import models


class NativeInterface(metaclass=abc.ABCMeta):
    def __init__(self, client, obj: models.AbstractCurrency):
        self.client = client
        self.obj = obj
        self.context = decimal.Context(prec=self.decimal_place)

    def __str__(self):
        return f'Currency: {self.symbol}'

    @property
    def name(self) -> str:
        return self.obj.name

    @property
    def symbol(self) -> str:
        return self.obj.symbol

    @property
    def decimal_place(self) -> str:
        return self.obj.decimal_place

    @property
    def decimals(self) -> str:
        return self.obj.decimals

    @abc.abstractclassmethod
    def build_transaction(cls, owner: str, raw_transaction: Any) -> dict: ...

    @abc.abstractmethod
    def to_decimal(self, amount: int) -> decimal.Decimal: ...

    @abc.abstractmethod
    def from_decimal(self, amount: decimal.Decimal) -> int: ...

    @abc.abstractmethod
    def balance(self, owner: str, to_decimal: bool = True) -> decimal.Decimal | int: ...

    @abc.abstractmethod
    def transfer(self, owner: str, to: str, amount: decimal.Decimal | int): ...


class StableCoinInterface(abc.ABC, NativeInterface):
    @classmethod
    def call(cls, value: Any) -> Any:
        return value

    def __init__(self, client, contract, obj: models.AbstractCurrency):
        super(StableCoinInterface, self).__init__(client, obj)
        self.contract = contract

    @property
    def address(self) -> str:
        return self.obj.address

    contract_address = address

    def to_decimal(self, amount: int) -> decimal.Decimal:
        return decimal.Decimal(
            amount / self.decimals,
            context=self.context
        )

    def from_decimal(self, amount: decimal.Decimal) -> int:
        return int(amount * self.decimals)

    def balance(self, owner: str, to_decimal: bool = True) -> decimal.Decimal | int:
        amount = self.call(self.contract.functions.balanceOf(owner))
        if to_decimal:
            amount = self.to_decimal(amount)
        return amount

    # alias
    balance_of = balanceOf = balance

    def allowance(self, owner: str, sender: str, to_decimal: bool = True) -> decimal.Decimal | int:
        amount = self.call(self.contract.functions.allowance(owner, sender))
        if to_decimal:
            amount = self.to_decimal(amount)
        return amount

    def transfer(self, owner: str, to: str, amount: decimal.Decimal | int):
        if isinstance(amount, decimal.Decimal):
            amount = self.from_decimal(amount)

        transaction = self.contract.functions.transfer(to, amount)
        return self.build_transaction(owner, transaction)

    def approve(self, owner: str, sender: str, amount: decimal.Decimal | int):
        if isinstance(amount, decimal.Decimal):
            amount = self.from_decimal(amount)

        transaction = self.contract.functions.approve(sender, amount)
        return self.build_transaction(owner, transaction)

    def transfer_from(self, owner: str, sender: str, to: str, amount: decimal.Decimal | int):
        if isinstance(amount, decimal.Decimal):
            amount = self.from_decimal(amount)

        transaction = self.contract.functions.transferFrom(sender, to, amount)
        return self.build_transaction(owner, transaction)

    # alias
    transferFrom = transfer_from
