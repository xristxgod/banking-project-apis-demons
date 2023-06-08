import decimal

from tronpy.async_tron import AsyncTron, AsyncTransactionBuilder

from core.transaction import Transaction
from core.utils import from_sun, to_sun


class Native:
    def __init__(self, client: AsyncTron):
        self.client = client

    def _make_transaction(self, transaction) -> Transaction:
        return Transaction(transaction, client=self.client)

    def to_decimal(self, amount: int) -> decimal.Decimal:
        return from_sun(amount)

    def from_decimal(self, amount: decimal.Decimal) -> int:
        return to_sun(amount)

    async def balance(self, owner: str, to_decimal: bool = True) -> decimal.Decimal | int:
        amount = await self.client.get_account_balance(owner)
        if not to_decimal:
            amount = self.from_decimal(amount)
        return amount

    def transfer(self, to: str, amount: decimal.Decimal | int):
        if isinstance(amount, decimal.Decimal):
            amount = self.from_decimal(amount)

        inner = {
            'parameter': {
                'value': {
                    'owner_address': None,
                    'to_address': to,
                    'amount': amount,
                },
                'type_url': 'type.googleapis.com/protocol.TransferContract',
                'type': 'TransferContract',
            }
        }

        transaction = AsyncTransactionBuilder(inner, client=self.client)
        return self._make_transaction(transaction)
