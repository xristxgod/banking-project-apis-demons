from typing import NoReturn

from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from src.settings import settings
from src.core.contract import Contract


class Node:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            setattr(cls, 'instance', super(cls).__new__(*args, **kwargs))
        return getattr(cls, 'instance')

    def __init__(self):
        self._node = AsyncTron(provider=AsyncHTTPProvider(settings.NODE_URL))

        self.contracts: dict[str: Contract] = {}

    @property
    def node(self) -> AsyncTron:
        return self._node

    async def update_contracts(self) -> NoReturn:
        contracts = dict()

        for contract_info in contracts:
            self.contracts.update({
                contract_info['symbol']: Contract(
                    client=await self._node.get_contract(contract_info['address']),
                    address=contract_info['address'],
                    symbol=contract_info['symbol'],
                    decimal_places=contract_info['decimal_places']
                )
            })
