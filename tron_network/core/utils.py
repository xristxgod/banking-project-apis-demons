from tronpy.keys import is_address
from tronpy.tron import TAddress
from tronpy.exceptions import AddressNotFound

from . import core
from core import exceptions


async def correct_currency(currency: str):
    if currency.upper() not in ['TRX', 'TRON'] and not core.contracts.get(currency.upper()):
        raise exceptions.CurrencyNotFound(currency)


async def correct_address(address: TAddress):
    if not is_address(address):
        raise AddressNotFound()
