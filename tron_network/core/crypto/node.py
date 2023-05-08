from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

import settings
from core.crypto.abi import ABI
from core.crypto.contract import Contract


class Node:
    class ContractNotFound(Exception):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            setattr(cls, 'instance', super().__new__(cls))
        return getattr(cls, 'instance')

    def __init__(self):
        self.provider = AsyncHTTPProvider(endpoint_uri=settings.NODE_URL)
        self.client = AsyncTron(
            provider=self.provider
        )

        self.contracts: dict[str, Contract] = {}

    def update_contract(self):
        pass

    def get_contract_by_symbol(self, symbol: str) -> Contract:
        contract = self.contracts.get(symbol)
        if not contract:
            raise self.ContractNotFound()
        return contract

    def has_currency(self, currency: str) -> bool:
        return self.contracts.get(currency) is not None
