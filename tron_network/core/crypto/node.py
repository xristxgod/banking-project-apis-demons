from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

import settings
from core.crypto.abi import ABI
from core.crypto.contract import Contract


class Node:
    class ContractNotFound(Exception):
        pass

    def __init__(self):
        self.provider = AsyncHTTPProvider(endpoint_uri=settings.NODE_URL)
        self.client = AsyncTron(
            provider=self.provider
        )

        self.contract: dict[str, Contract] = {}

    def update_contract(self):
        pass

    async def get_contract_by_symbol(self, symbol: str) -> Contract:
        contract = self.contract.get(symbol)
        if not contract:
            raise self.ContractNotFound()
        return contract
