import decimal

from tronpy.tron import TAddress

from src.core import Node
from src.settings import settings
from src.utils import exception_handler
from src.exceptions import CurrencyNotFound


class Wallet:
    central_wallet = settings.CENTRAL_WALLET

    def __init__(self):
        self.core = Node()
        self.node = self.core.node

    @exception_handler(KeyError, CurrencyNotFound)
    async def balance(self, address: TAddress, currency: str = 'TRX') -> decimal.Decimal:
        if currency == 'TRX':
            return await self.node.get_account_balance(address)
        else:
            contract = self.core.contracts[currency]
            return await contract.read.balance_of(address)
