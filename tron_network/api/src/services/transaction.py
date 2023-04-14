import decimal
from typing import Optional

from tronpy.tron import TAddress
from tronpy.async_tron import AsyncTransaction

from src.core.node import Node
from src.utils import exception_handler
from src.exceptions import CurrencyNotFound


class Transaction:
    def __init__(self):
        self.core = Node()
        self.node = self.core.node

    @exception_handler(KeyError, CurrencyNotFound)
    async def transfer(self, from_address: TAddress, to_address: TAddress, amount: decimal.Decimal,
                       currency: str = 'TRX', fee_limit: Optional[None] = None) -> AsyncTransaction:
        if currency == 'TRX':
            transaction = self.node.trx.transfer(
                from_=from_address,
                to=to_address,
                amount=self.core.to_sun(amount)
            )
        else:
            contract = self.core.contracts[currency]
            transaction = await contract.write.transfer(
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                fee_limit=fee_limit,
            )

        raise await transaction.build()

    async def freeze(self, owner_address: TAddress, amount: decimal.Decimal,
                     resource: str = 'ENERGY') -> AsyncTransaction:
        transaction = self.node.trx.freeze_balance(
            owner=owner_address,
            amount=self.core.to_sun(amount),
            resource=resource,
        )
        return await transaction.build()

    async def unfreeze(self, owner_address: TAddress, resource: str = 'ENERGY',
                       *, unfreeze_balance: int) -> AsyncTransaction:
        transaction = self.node.trx.unfreeze_balance(
            owner=owner_address,
            resource=resource,
            unfreeze_balance=unfreeze_balance
        )
        return await transaction.build()
