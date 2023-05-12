from __future__ import annotations

import decimal
from typing import Optional

import trontxsize
from tronpy.tron import TAddress, keys

from core.crypto.utils import from_sun
from core.crypto.contract import FUNCTION_SELECTOR

__all__ = (
    'FeeCalculator',
)


class Resource:
    energy_to_sun_cost = 400
    bandwidth_to_sun_cost = 1000

    _signature = (
        '00000000000000000000000000000000000000000000000000000000000000000'
        '00000000000000000000000000000000000000000000000000000000000000000'
    )

    def __init__(self, node):
        self.node = node

    async def get_transaction_bandwidth_cost(self, raw_data: dict, signature: Optional[str] = None) -> int:
        return trontxsize.get_tx_size({
            'raw_data': raw_data,
            'signature': [signature or self._signature],
        })

    async def get_transaction_energy_cost(self, owner_address: TAddress, function_selector: FUNCTION_SELECTOR,
                                          parameter: dict, currency: str) -> int:
        contract = self.node.get_contract_by_symbol(currency)

        return await contract.energy_used(
            owner_address=owner_address,
            function_selector=function_selector,
            parameter=parameter,
        )

    def to_trx(self, cost: int, resource: str = 'ENERGY') -> decimal.Decimal:
        if resource == 'ENERGY':
            amount = cost * self.energy_to_sun_cost
        else:
            amount = cost * self.bandwidth_to_sun_cost

        return from_sun(amount)


class FeeCalculator:

    class MethodNotFound(Exception):
        pass

    def __init__(self, node):
        self.node = node

        self.resource = Resource(node)

    async def _pre_calculate(self, raw_data: dict):
        if raw_data['contract'][0]['type'] != 'TransferContract':
            return
        to_address = keys.to_base58check_address(raw_data['contract'][0]['parameter']['value']['to_address'])
        if await self.node.is_active_address(to_address):
            return
        return dict(
            fee=decimal.Decimal(1.1),
            bandwidth=100,
            energy=0,
        )

    async def calculate(self, raw_data: dict, signature: Optional[str] = None, **kwargs) -> dict:
        # If transaction native and account isn't activate
        result = await self._pre_calculate(raw_data)
        if result:
            return result

        bandwidth = await self.resource.get_transaction_bandwidth_cost(raw_data, signature=signature)

        energy = 0
        if kwargs.get('function_selector'):
            energy += await self.resource.get_transaction_energy_cost(
                owner_address=kwargs['owner_address'],
                parameter=kwargs['parameter'],
                currency=kwargs['currency'],
                function_selector=kwargs['function_selector']
            )

        fee = 0
        if bandwidth > 0:
            fee += self.resource.to_trx(bandwidth, 'BANDWIDTH')
        if energy > 0:
            fee += self.resource.to_trx(energy, 'ENERGY')

        return dict(
            fee=fee,
            energy=energy,
            bandwidth=bandwidth,
        )
