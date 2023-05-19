import decimal
from typing import Optional

from tronpy.tron import TAddress
from pydantic import BaseModel, Field, validator

from core.crypto import node
from core.crypto.utils import is_native
from core.crypto.contract import Contract
from apps.common import utils


class WithCurrencySchema(BaseModel):
    currency: str = Field(default='TRX')

    @property
    def is_native(self) -> bool:
        return is_native(self.currency)

    @property
    def contract(self) -> Contract:
        if not self.is_native:
            return node.get_contract_by_symbol(self.currency)

    @classmethod
    def use_native(cls) -> bool:
        return True

    @validator('currency')
    def valid_currency(cls, currency: str):
        currency = currency.upper()
        if not cls.use_native() and is_native(currency):
            raise ValueError("Don't use native!")
        elif currency != 'TRX' and not node.has_currency(currency):
            raise ValueError(f'Currency: {currency} not found')
        return currency


class BodyCreateWallet(BaseModel):
    mnemonic: Optional[str] = Field(default=utils.generate_mnemonic())
    passphrase: Optional[str] = Field(default=utils.generate_passphrase())


class ResponseCreateWallet(BodyCreateWallet):
    private_key: str
    public_key: str
    address: TAddress


class BodyWalletBalance(WithCurrencySchema, BaseModel):
    address: TAddress
    currency: Optional[str] = Field(default='TRX')

    @validator('currency')
    def correct_currency(cls, currency: str):
        currency = currency.upper()
        if is_native(currency) and not node.has_currency(currency):
            raise ValueError(f'Currency: {currency} not found')
        return currency

    @validator('address')
    def correct_address(cls, address: TAddress):
        return utils.correct_address(address)


class ResponseWalletBalance(BaseModel):
    balance: decimal.Decimal = Field(default=0)


class BodyAllowance(WithCurrencySchema, BaseModel):
    owner_address: TAddress
    sender_address: TAddress
    currency: str

    @validator('currency')
    def correct_currency(cls, currency: str):
        currency = currency.upper()
        if not node.has_currency(currency):
            raise ValueError(f'Currency: {currency} not found')
        return currency

    @validator('owner_address', 'sender_address')
    def correct_address(cls, address: TAddress):
        return utils.correct_address(address)


class ResponseAllowance(BaseModel):
    amount: decimal.Decimal = Field(default=0)
