from tronpy.tron import TAddress
from tronpy.exceptions import AddressNotFound
from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

import settings
from core.crypto.abi import ABI
from core.crypto.contract import Contract
from core.crypto.calculator import FeeCalculator


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

        self.fee_calculator = FeeCalculator(self)

        self.update_contract()

    @property
    def calculator(self) -> FeeCalculator:
        return self.fee_calculator

    def update_contract(self):
        pass

    def get_contract_by_symbol(self, symbol: str) -> Contract:
        contract = self.contracts.get(symbol)
        if not contract:
            raise self.ContractNotFound()
        return contract

    def has_currency(self, currency: str) -> bool:
        return self.contracts.get(currency) is not None

    async def is_active_address(self, address: TAddress) -> bool:
        try:
            await self.client.get_account_balance(address)
        except AddressNotFound:
            return False
        else:
            return True

    async def get_bandwidth_balance(self, address: TAddress) -> int:
        resource = await self.client.get_account_resource(address)
        return (
                resource["freeNetLimit"] - resource.get("freeNetUsed", 0) +
                resource.get("NetLimit", 0) - resource.get("NetUsed", 0)
        )

    async def get_energy_balance(self, address: TAddress) -> int:
        resource = await self.client.get_account_resource(address)
        return resource.get('EnergyLimit', 0) - resource.get('EnergyUsed', 0)
