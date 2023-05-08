from __future__ import annotations

import decimal

from tronpy.tron import TAddress
from tronpy.async_tron import AsyncTron, AsyncContract


class ReadContractMixin:
    async def balance_of(self, address: TAddress) -> decimal.Decimal:
        amount = await self.contract.functions.balanceOf(address)
        if amount > 0:
            amount = amount / self.decimals
        return decimal.Decimal(amount, context=self.context)


class WriteContractMixin:
    async def transfer(self):
        pass


class ContractMethodMixin(ReadContractMixin, WriteContractMixin):
    pass


class Contract(ContractMethodMixin):
    def __init__(self, contract: AsyncContract, client: AsyncTron, **kwargs):
        self.contract = contract
        self.client = client

        self._address = self.contract.address
        self._name = self.contract.name or kwargs.pop('name')
        self._symbol = kwargs.pop('symbol')
        self._decimal_place = kwargs.pop('decimal_place')

        self.context = decimal.Context(prec=self._decimal_place)

    def __str__(self):
        return f'Contract: {self._symbol}'

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def decimals(self) -> int:
        return 10 ** self._decimal_place
