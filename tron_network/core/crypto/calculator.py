from __future__ import annotations

import decimal
import enum

from tronpy.tron import TAddress

from core.crypto.utils import from_sun


class FeeCalculator:
    energy_sun_cost = 420
    default_native_bandwidth_cost = 267
    default_token_bandwidth_cost = 345

    not_bandwidth_balance_extra_fee_native_cost = decimal.Decimal(0.267)
    not_bandwidth_balance_extra_fee_token_cost = decimal.Decimal(0.345)
    activate_account_trx_cost = decimal.Decimal(1.1)
    activate_account_bandwidth_cost = 100

    class Method(enum.Enum):
        TRANSFER = 'transfer'
        TRANSFER_FROM = 'transfer_from'
        APPROVE = 'approve'

    class MethodNotFound(Exception):
        pass

    def __init__(self, node):
        self.node = node

    async def _bandwidth_fee(self, from_address: TAddress, bandwidth: int, currency: str) -> decimal.Decimal:
        bandwidth_balance = await self.node.get_bandwidth_balance(from_address)

        amount = decimal.Decimal(0)
        if bandwidth_balance < bandwidth:
            if currency == 'TRX':
                amount += self.not_bandwidth_balance_extra_fee_native_cost
            else:
                amount += self.not_bandwidth_balance_extra_fee_token_cost
        return amount

    async def _energy_fee(self, from_address: TAddress, energy: int) -> decimal.Decimal:
        energy_balance = await self.node.get_energy_balance(from_address)

        amount = decimal.Decimal(0)
        if energy_balance < energy:
            amount += from_sun(energy * self.energy_sun_cost)
        return amount

    async def _transfer_native(self, from_address: TAddress, to_address: TAddress) -> dict:
        amount, bandwidth = decimal.Decimal(0), self.default_native_bandwidth_cost
        if not await self.node.is_active_address(address=to_address):
            amount += self.activate_account_trx_cost
            bandwidth += self.activate_account_bandwidth_cost

        amount += await self._bandwidth_fee(from_address, bandwidth, 'TRX')

        return dict(
            fee=amount,
            energy=0,
            bandwidth=bandwidth,
        )

    async def _transfer(self, from_address: TAddress, to_address: TAddress,
                        amount: decimal.Decimal, currency: str) -> dict:
        contract = self.node.get_contract_by_symbol(currency)
        parameter = [
            to_address,
            int(amount * contract.decimals),
        ]
        energy = await contract.energy_used(
            owner_address=from_address,
            function_selector=contract.FunctionSelector.TRANSFER,
            parameter=parameter,
        )
        bandwidth = self.default_token_bandwidth_cost

        bandwidth_fee = await self._bandwidth_fee(from_address, bandwidth, currency)
        energy_fee = await self._energy_fee(from_address, energy)

        return dict(
            fee=bandwidth_fee + energy_fee,
            energy=energy,
            bandwidth=bandwidth,
        )

    async def _approve(self, owner_address: TAddress, spender_address: TAddress,
                       amount: decimal.Decimal, currency: str) -> dict:
        contract = self.node.get_contract_by_symbol(currency)
        parameter = [spender_address, int(amount * contract.decimals)]
        energy = await contract.energy_used(
            owner_address=owner_address,
            function_selector=contract.FunctionSelector.APPROVE,
            parameter=parameter,
        )
        bandwidth = self.default_token_bandwidth_cost

        bandwidth_fee = await self._bandwidth_fee(owner_address, bandwidth, currency)
        energy_fee = await self._energy_fee(owner_address, energy)

        return dict(
            fee=bandwidth_fee + energy_fee,
            energy=energy,
            bandwidth=bandwidth,
        )

    async def _transfer_from(self, owner_address: TAddress, from_address: TAddress, to_address: TAddress,
                             amount: decimal.Decimal, currency: str) -> dict:
        contract = self.node.get_contract_by_symbol(currency)
        parameter = [from_address, to_address, int(amount * contract.decimals)]
        energy = await contract.energy_used(
            owner_address=owner_address,
            function_selector=contract.FunctionSelector.TRANSFER_FROM,
            parameter=parameter,
        )
        bandwidth = self.default_token_bandwidth_cost

        bandwidth_fee = await self._bandwidth_fee(owner_address, bandwidth, currency)
        energy_fee = await self._energy_fee(owner_address, energy)

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
            case self.Method.APPROVE:
                return await self._approve(
                    owner_address=kwargs['owner_address'],
                    spender_address=kwargs['spender_address'],
                    amount=kwargs['amount'],
                    currency=kwargs['currency'],
                )
            case self.Method.TRANSFER_FROM:
                return await self._transfer_from(

                )
            case _:
                raise self.MethodNotFound(f'Method: {method} not found')


FEE_METHOD_TYPES = FeeCalculator.Method
