import decimal
from tronpy.tron import TransactionBuilder

import settings
from .base import NativeInterface, StableCoinInterface


class Native(NativeInterface):
    @classmethod
    def build_transaction(cls, owner: str, raw_transaction: TransactionBuilder) -> dict:
        transaction = raw_transaction.with_owner(
            owner,
        ).fee_limit(
            settings.STANDART_FEE_LIMIT,
        ).build()

        return transaction.to_json()

    def to_decimal(self, amount: int) -> decimal.Decimal:
        if amount == 0:
            return decimal.Decimal(0)

        return decimal.Decimal(value=amount, context=self.context) / decimal.Decimal(self.decimals)

    def from_decimal(self, amount: decimal.Decimal) -> int:
        if isinstance(amount, int) or isinstance(amount, str):
            d_num = decimal.Decimal(value=amount)
        elif isinstance(amount, float):
            d_num = decimal.Decimal(value=str(amount))
        elif isinstance(amount, decimal.Decimal):
            d_num = amount
        else:
            raise TypeError("Unsupported type. Must be one of integer, float, or string")

        s_num = str(amount)
        unit_value = decimal.Decimal(self.decimals)

        if d_num == 0:
            return 0

        if d_num < 1 and "." in s_num:
            with decimal.localcontext() as ctx:
                multiplier = len(s_num) - s_num.index(".") - 1
                ctx.prec = multiplier
                d_num = decimal.Decimal(value=amount, context=ctx) * 10 ** multiplier
            unit_value /= 10 ** multiplier

        with decimal.localcontext() as ctx:
            ctx.prec = 999
            result = decimal.Decimal(value=d_num, context=ctx) * unit_value

        return int(result)

    def balance(self, owner: str, to_decimal: bool = True) -> decimal.Decimal | int:
        amount = self.client.get_account_balance(owner)
        if not to_decimal:
            amount = self.from_decimal(amount)
        return amount

    def transfer(self, owner: str, to: str, amount: decimal.Decimal | int):
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

        transaction = TransactionBuilder(inner, client=self.client)
        return self.build_transaction(owner, transaction)


class StableCoin(Native, StableCoinInterface):
    pass
