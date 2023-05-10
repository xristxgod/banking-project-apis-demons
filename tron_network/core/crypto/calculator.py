from __future__ import annotations

import decimal
import enum

from tronpy.tron import TAddress

from core.crypto.utils import from_sun


class FeeCalculator:
    class Method(enum.Enum):
        TRANSFER = 'transfer'
        TRANSFER_FROM = 'transfer_from'
        APPROVE = 'approve'

    class MethodNotFound(Exception):
        pass

    def __init__(self, node):
        self.node = node

    async def _bandwidth_fee(self, from_address: TAddress, bandwidth: int) -> decimal.Decimal:
        bandwidth_balance = await self.node.get_bandwidth_balance(from_address)

        amount = 0
        if bandwidth_balance < bandwidth:
            amount += 0.267
        return decimal.Decimal(amount)

    async def _energy_fee(self, from_address: TAddress, energy: int) -> decimal.Decimal:
        energy_balance = await self.node.get_energy_balance(from_address)

        amount = decimal.Decimal(0)
        if energy_balance < energy:
            amount += from_sun(energy * 420)
        return amount

    async def _transfer_native(self, from_address: TAddress, to_address: TAddress) -> dict:
        amount, bandwidth = decimal.Decimal(0), 267
        if await self.node.is_active_address(address=to_address):
            amount += decimal.Decimal(1.1)
            bandwidth += 100

        amount += await self._bandwidth_fee(from_address, bandwidth)

        return dict(
            fee=amount,
            energy=0,
            bandwidth=bandwidth,
        )

    async def _transfer(self, from_address: TAddress, to_address: TAddress,
                        amount: decimal.Decimal, currency: str) -> dict:
        contract = self.node.get_contract_by_symbol(currency)
        parameter = (
            to_address,
            int(amount * contract.decimals),
        )
        energy = await contract.energy_used(
            from_address=from_address,
            function_selector=contract.FunctionSelector.TRANSFER,
            parameter=parameter,
        )
        bandwidth = 345

        bandwidth_fee = await self._bandwidth_fee(from_address, bandwidth)
        energy_fee = await self._energy_fee(from_address, energy)

        return dict(
            fee=bandwidth_fee + energy_fee,
            energy=energy,
            bandwidth=bandwidth,
        )

    async def calculate(self, method: Method, **kwargs) -> dict:
        match method:
            case self.Method.TRANSFER:
                from_address = kwargs['from_address']
                to_address = kwargs['to_address']
                if kwargs.get('currency', 'TRX') == 'TRX':
                    return await self._transfer_native(
                        from_address=from_address,
                        to_address=to_address,
                    )
                return await self._transfer(
                    from_address=from_address,
                    to_address=to_address,
                    amount=kwargs['amount'],
                    currency=kwargs['currency'],
                )
            case self.Method.TRANSFER_FROM:
                # TODO transfer from
                pass
            case self.Method.APPROVE:
                # TODO approve
                pass
            case _:
                raise self.MethodNotFound(f'Method: {method} not found')


FEE_METHOD_TYPES = FeeCalculator.Method
