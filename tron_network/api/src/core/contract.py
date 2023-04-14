from __future__ import annotations

import decimal
from typing import Optional

from tronpy.tron import TAddress
from tronpy.async_contract import AsyncContract
from tronpy.async_tron import AsyncTransaction

from src.settings import settings


class WriteMethods:
    def __init__(self, contract: Contract):
        self._contract = contract

    def _get_correct_amount(self, amount: decimal.Decimal):
        return amount / 10 ** self._contract.context.prec

    async def transfer(self, from_address: TAddress, to_address: TAddress,
                       amount: decimal.Decimal, fee_limit: Optional[int] = None) -> AsyncTransaction:
        transaction = self._contract.client.functions.transfer(
            to_address, self._get_correct_amount(amount)
        ).with_owner(
            from_address
        )
        transaction.fee_limit(
            fee_limit or settings.GLOBAL_FEE_LIMIT
        )
        return transaction


class ReadMethods:
    def __init__(self, contract: Contract):
        self._contract = contract

    async def balance_of(self, address: TAddress) -> decimal.Decimal:
        raw_amount = await self._contract.client.functions.balanceOf(address)
        return decimal.Decimal(raw_amount, context=self._contract.context)


class Contract:
    def __init__(self, client: AsyncContract, address: TAddress, symbol: str, decimal_places: int):
        self.client = client
        self.address = address
        self.symbol = symbol

        self.context = decimal.Context(prec=decimal_places)

        self._read = ReadMethods(self)
        self._write = WriteMethods(self)

    def __str__(self):
        return f'Contract: {self.symbol}'

    @property
    def read(self) -> ReadMethods:
        return self._read

    @property
    def write(self) -> WriteMethods:
        return self._write
