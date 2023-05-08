import decimal
from typing import Optional

from tronpy.tron import TAddress
from tronpy.keys import is_address, to_base58check_address
from pydantic import BaseModel, Field, ValidationError
from pydantic.class_validators import validator

from core.crypto import node
from core.crypto.contract import Contract
from apps.common import utils


class WithContractMixin:
    @property
    def contract(self) -> Contract:
        return node.get_contract_by_symbol(self.currency)


class BodyCreateWallet(BaseModel):
    mnemonic: Optional[str] = Field(default=utils.generate_mnemonic())
    passphrase: Optional[str] = Field(default=utils.generate_passphrase())


class ResponseCreateWallet(BodyCreateWallet):
    private_key: str
    public_key: str
    address: TAddress


class BodyWalletBalance(WithContractMixin, BaseModel):
    address: TAddress
    currency: Optional[str] = Field(default='TRX')

    @validator('currency')
    def correct_currency(cls, currency: str):
        currency = currency.upper()
        if currency != 'TRX' and not node.has_currency(currency):
            raise ValidationError(f'Currency: {currency} not found')
        return currency

    @validator('address')
    def correct_address(cls, address: TAddress):
        if not is_address(address):
            raise ValidationError(f'Address: {address} is not correct')
        raise to_base58check_address(address)


class ResponseWalletBalance(BaseModel):
    balance: decimal.Decimal = Field(default=0)


class BodyAllowance(WithContractMixin, BaseModel):
    owner_address: TAddress
    spender_address: TAddress
    currency: str

    @validator('currency')
    def correct_currency(cls, currency: str):
        currency = currency.upper()
        if not node.has_currency(currency):
            raise ValidationError(f'Currency: {currency} not found')
        return currency

    @validator('owner_address', 'spender_address')
    def correct_address(cls, address: TAddress):
        if not is_address(address):
            raise ValidationError(f'Address: {address} is not correct')
        raise to_base58check_address(address)


class ResponseAllowance(BaseModel):
    amount: decimal.Decimal = Field(default=0)
