import json
import decimal
from typing import Optional

from tronpy.tron import TAddress, PrivateKey
from tronpy.async_tron import AsyncTransaction
from pydantic import BaseModel, Field, validator

import settings
from core.crypto import node
from core.crypto.utils import to_sun
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


class BodyCreateTransfer(CurrencyMixin, BaseModel):
    from_address: TAddress
    to_address: TAddress
    amount: decimal.Decimal

    currency: str = Field(default='TRX')

    fee_limit: int = Field(default=settings.DEFAULT_FEE_LIMIT)

    @property
    def sun_amount(self) -> int:
        # Amount to Sun amount
        return to_sun(self.amount)

    @validator('from_address', 'to_address')
    def correct_address(cls, address: TAddress):
        return utils.correct_address(address)


class ResponseCommission(BaseModel):
    fee: decimal.Decimal = Field(default=0)
    energy: int = Field(default=0)
    bandwidth: int = Field(default=0)


class ResponseCreateTransfer(BaseModel):
    payload: str
    commission: ResponseCommission

    @property
    def payload_dict(self) -> dict:
        return json.loads(self.payload)


class BodySendTransaction(BaseModel):
    payload: str
    private_key: str

    @property
    def payload_dict(self) -> dict:
        return json.loads(self.payload)

    async def create_transaction_obj(self) -> AsyncTransaction:
        data = self.payload_dict.get('data')
        return await AsyncTransaction.from_json(data, client=node.client)

    @property
    def private_key_obj(self):
        return PrivateKey(private_key_bytes=bytes.fromhex(self.private_key))

    @property
    def extra(self) -> dict:
        return self.payload_dict.get('extra_fields')


class ResponseSendTransaction(BaseModel):
    transaction_id: str
    timestamp: int
    amount: decimal.Decimal
    fee: decimal.Decimal
    from_address: TAddress
    to_address: TAddress
    currency: str = Field(default='TRX')


class BodyCommission(BaseModel):
    parameter: dict
