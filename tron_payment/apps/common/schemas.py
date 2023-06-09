import decimal
from typing import Optional

from tronpy.keys import is_address, to_base58check_address
from pydantic import BaseModel, Field, validator

from core.node import node
from core.stable_coins import StableCoinInterface


class BodyWithAlias(BaseModel):
    class Config:
        allow_population_by_field_name = True


class BodyCreateWallet(BodyWithAlias):
    mnemonic: Optional[str] = Field(default=None)
    passphrase: Optional[str] = Field(default=None)


class ResponseCreateWallet(BodyCreateWallet):
    address: str
    public_key: str = Field(default=None, alias='publicKey')
    private_key: Optional[str] = Field(default=None, alias='privateKey')


class BodyBalance(BaseModel):
    address: str
    currency: str = Field(default=node.native_symbol)

    @validator('currency')
    def valid_currency(cls, value: str):
        currency = value.upper()
        if not node.has_currency(currency):
            raise ValueError(f'Currency: {currency} not found')
        return currency

    @validator('address')
    def valid_address(self, value: str):
        if not is_address(value):
            raise ValueError(f'Invalid address: {value}')
        return to_base58check_address(value)

    @property
    def is_native(self) -> bool:
        return self.currency == node.native_symbol

    @property
    def is_stable_coin(self) -> bool:
        return not self.is_native

    @property
    def stable_coin(self) -> StableCoinInterface:
        if self.is_stable_coin:
            return node.get_stable_coin(self.currency)


class ResponseBalance(BodyBalance):
    amount: decimal.Decimal = Field(default=0)
