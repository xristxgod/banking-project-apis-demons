from __future__ import annotations

import decimal

from tronpy.tron import TAddress
from tronpy.abi import trx_abi
from tronpy.async_tron import AsyncTron, AsyncContract, AsyncTransactionBuilder


class ReadContractMixin:
    async def balance_of(self, address: TAddress) -> decimal.Decimal:
        amount = self.contract.functions.balanceOf(address)
        if amount > 0:
            amount = amount / self.decimals
        return decimal.Decimal(amount, context=self.context)

    async def allowance(self, owner_address: TAddress, spender_address: TAddress) -> decimal.Decimal:
        amount = self.contract.functions.allowance(owner_address, spender_address)
        if amount > 0:
            amount = amount / self.decimals
        return decimal.Decimal(amount, context=self.context)


class WriteContractMixin:
    async def transfer(self, from_address: TAddress, to_address: str,
                       amount: decimal.Decimal) -> AsyncTransactionBuilder:
        amount = int(amount * self.decimals)
        return self.contract.functions.transfer(
            to_address, amount,
        ).with_owner(
            from_address
        )


class ContractMethodMixin(ReadContractMixin, WriteContractMixin):
    pass


class Contract(ContractMethodMixin):

    class FunctionSelector:
        # name      function selector, parameter
        TRANSFER = 'transfer(address,uint256)', '(address,uint256)'

    def __init__(self, contract: AsyncContract, client: AsyncTron, **kwargs):
        self.contract = contract
        self.client = client

        self._address = self.contract.address
        self._name = self.contract.name or kwargs.pop('name')
        self._symbol = kwargs.pop('symbol')
        self._decimal_place = kwargs.pop('decimal_place')

        self.context = decimal.Context(prec=self._decimal_place)

    def __str__(self):
        return f'Contract: {self._symbol}'

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def address(self) -> TAddress:
        return self._address

    @property
    def decimals(self) -> int:
        return 10 ** self._decimal_place

    async def energy_used(self, from_address: TAddress, function_selector: FunctionSelector, parameter: tuple) -> int:
        function_selector_view, parameter_view = function_selector

        def get_parameter_hex():
            return trx_abi.encode(parameter_view, parameter).hex()

        response = await self.client.provider.make_request(
            "wallet/triggerconstantcontract",
            {
                "owner_address": from_address,
                "contract_address": self.address,
                "function_selector": function_selector_view,
                "parameter": get_parameter_hex(),
                "visible": True,
            }
        )

        return response['energy_used']
