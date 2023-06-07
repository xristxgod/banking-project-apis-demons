import decimal
import functools

from tronpy.async_tron import AsyncTron, AsyncContract

from core.native import Native


class StableCoinInterface(Native):
    def __init__(self, client: AsyncTron, contract: AsyncContract, symbol: str, name: str, decimal_place: int):
        super(StableCoinInterface, self).__init__(client)
        self.contract = contract

        self.symbol = symbol
        self.name = name
        self.decimal_place = decimal_place

        self.context = decimal.Context(prec=self.decimal_place)

    @property
    def address(self) -> str:
        return self.contract.address

    @property
    @functools.lru_cache(None)
    def decimals(self) -> int:
        return 10 ** self.decimal_place

    def to_decimal(self, amount: int) -> decimal.Decimal:
        return decimal.Decimal(
            amount / self.decimals,
            context=self.context
        )

    def from_decimal(self, amount: decimal.Decimal) -> int:
        return int(amount * self.decimals)

    async def balance(self, owner: str, to_decimal: bool = True) -> decimal.Decimal | int:
        amount = await self.contract.functions.balanceOf(owner)
        if to_decimal:
            amount = self.to_decimal(amount)
        return amount

    # alias
    balance_of = balanceOf = balance

    async def allowance(self, owner: str, sender: str, to_decimal: bool = True) -> decimal.Decimal | int:
        amount = await self.contract.functions.allowance(owner, sender)
        if to_decimal:
            amount = self.to_decimal(amount)
        return amount

    def transfer(self, to: str, amount: decimal.Decimal | int):
        if isinstance(amount, decimal.Decimal):
            amount = self.from_decimal(amount)

        transaction = await self.contract.functions.transfer(to, amount)
        return self._make_transaction(transaction)

    def approve(self, sender: str, amount: decimal.Decimal | int):
        if isinstance(amount, decimal.Decimal):
            amount = self.from_decimal(amount)

        transaction = await self.contract.functions.approve(sender, amount)
        return self._make_transaction(transaction)

    def transfer_from(self, sender: str, to: str, amount: decimal.Decimal | int):
        if isinstance(amount, decimal.Decimal):
            amount = self.from_decimal(amount)

        transaction = await self.contract.functions.transferFrom(sender, to, amount)
        return self._make_transaction(transaction)

    # alias
    transferFrom = transfer_from
