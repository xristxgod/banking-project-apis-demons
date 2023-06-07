import decimal

from tronpy.async_tron import AsyncTron, AsyncTransactionBuilder

from core.transaction import Transaction


class Native:
    def __init__(self, client: AsyncTron):
        self.client = client

    def _make_transaction(self, transaction) -> Transaction:
        return Transaction(transaction, client=self.client)

    def to_decimal(self, amount: int) -> decimal.Decimal:
        if amount == 0:
            return decimal.Decimal(0)

        with decimal.localcontext() as ctx:
            ctx.prec = 999
            amount = decimal.Decimal(value=amount, context=ctx) / decimal.Decimal(1000000)

        return amount

    def from_decimal(self, amount: decimal.Decimal) -> int:
        if amount == 0:
            return 0

        unit_value = decimal.Decimal(1000000)

        if amount < 1 and '.' in str(amount):
            s_amount = str(amount)
            with decimal.localcontext() as ctx:
                multiplier = len(s_amount) - s_amount.index('.') - 1
                ctx.prec = multiplier
                amount = decimal.Decimal(value=amount, context=ctx) * 10 ** multiplier
            unit_value /= 10 ** multiplier

        with decimal.localcontext() as ctx:
            ctx.prec = 999
            amount = decimal.Decimal(value=amount, context=ctx) * unit_value

        return int(amount)

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
