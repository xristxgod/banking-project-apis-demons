from __future__ import annotations

import decimal

from tronpy.async_contract import AsyncContract


class ReadMethods:
    def __init__(self, contract: Contract):
        self._contract = contract

    async def balance_of(self, address: str):
        raw_amount = await self._contract.client.functions.balanceOf(address)
        return decimal.Decimal(raw_amount, context=self._contract.context)


class Contract:
    def __init__(self, client: AsyncContract, address: str, symbol: str, decimal_places: int):
        self.client = client
        self.address = address
        self.symbol = symbol

        self.context = decimal.Context(prec=decimal_places)

        self._read = ReadMethods(self)
        self._write = ''

    def __str__(self):
        return f'Contract: {self.symbol}'

    @property
    def read(self) -> ReadMethods:
        return self._read

    @property
    def write(self):
        pass
