import decimal
from typing import Optional

from tronpy.tron import TAddress
from pydantic import BaseModel, Field, validator

from core.crypto import node
from core.crypto.contract import Contract
from apps.common import utils


class CurrencyMixin:
    currency: str

    @property
    def is_native(self) -> bool:
        return self.currency == 'TRX'

    @property
    def contract(self) -> Contract:
        if not self.is_native:
            return node.get_contract_by_symbol(self.currency)


class BodyCreateWallet(BaseModel):
    mnemonic: Optional[str] = Field(default=utils.generate_mnemonic())
    passphrase: Optional[str] = Field(default=utils.generate_passphrase())


class ResponseCreateWallet(BodyCreateWallet):
    private_key: str
    public_key: str
    address: TAddress


class BodyWalletBalance(CurrencyMixin, BaseModel):
    address: TAddress
    currency: Optional[str] = Field(default='TRX')

    @validator('currency')
    def correct_currency(cls, currency: str):
        currency = currency.upper()
        if currency != 'TRX' and not node.has_currency(currency):
            raise ValueError(f'Currency: {currency} not found')
        return currency

    @validator('address')
    def correct_address(cls, address: TAddress):
        return utils.correct_address(address)


class ResponseWalletBalance(BaseModel):
    balance: decimal.Decimal = Field(default=0)


class BodyAllowance(CurrencyMixin, BaseModel):
    owner_address: TAddress
    spender_address: TAddress
    currency: str

    @validator('currency')
    def correct_currency(cls, currency: str):
        currency = currency.upper()
        if not node.has_currency(currency):
            raise ValueError(f'Currency: {currency} not found')
        return currency

    @validator('owner_address', 'spender_address')
    def correct_address(cls, address: TAddress):
        return utils.correct_address(address)


class ResponseAllowance(BaseModel):
    amount: decimal.Decimal = Field(default=0)
