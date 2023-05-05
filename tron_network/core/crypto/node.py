import json

from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

import settings
from settings import settings
from core.crypto.contract import Contract


class Node:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            setattr(cls, 'instance', super().__new__(cls, *args, **kwargs))
        return getattr(cls, 'instance')

    def __init__(self):
        self.node = AsyncTron(provider=AsyncHTTPProvider(settings.NODE_URL))

        self._contracts: dict[str, Contract] = {}

        self.update_contracts()

    def update_contracts(self):
        with open(settings.CONTRACTS_FILE, 'r', encoding='utf-8') as file:
            contracts = json.loads(file.read())
        for contract in contracts:
            self._contracts.update({
                contract['symbol'].upper(): Contract(
                    address=contract['address'],
                    symbol=contract['symbol'],
                    name=contract.get('name'),
                    decimal_place=contract['decimal_place'],
                    node=self.node
                )
            })

    @property
    def contracts(self) -> dict:
        return self._contracts
