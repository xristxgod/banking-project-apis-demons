import decimal
from typing import Optional

from tronpy.tron import TAddress
from pydantic import BaseModel, Field, conint
from pydantic import ValidationError, validator

from src.core import controller
from src.settings import settings


class CurrencyMixin:
    currency: Optional[str] = Field(default='TRX')

    @validator('currency')
    def valid_currency(cls, currency: str):
        if currency.upper() != 'TRX' and controller.has_currency(currency):
            raise ValidationError(f'Currency {currency} not found')
        return currency.upper()


class BodyAdminCreateWallet(BaseModel):
    index: Optional[conint(gt=1)] = Field(default=None)


class BodyAdminBalance(CurrencyMixin, BaseModel):
    address: Optional[TAddress] = Field(default=settings.CENTRAL_WALLET['address'])


class BodyAdminTransfer(CurrencyMixin, BaseModel):
    to_address: TAddress = Field(alias='toAddress')
    amount: decimal.Decimal
    fee_limit: int = Field(alias='feeLimit', default=None)

    @property
    def from_address(self) -> TAddress:
        return settings.CENTRAL_WALLET['address']


class ResponseAdminCreateWallet(BodyAdminCreateWallet):
    address: TAddress
    hex_private_key = Field(alias='hexPrivateKey')


class ResponseAdminBalance(BaseModel):
    amount: decimal.Decimal = Field(default=0)


class ResponseTransaction(BaseModel):
    pass


class ResponseCommission(BaseModel):
    fee: decimal.Decimal = Field(default=0)
    energy: int = Field(default=0)
    bandwidth: int = Field(default=0)
    fee_limit: int = Field(alias='feeLimit', default=settings.GLOBAL_FEE_LIMIT)


class ResponseAdminTransfer(BaseModel):
    raw_data: str = Field(alias='raw_data')
    body_transaction: ResponseTransaction
    extra: ResponseCommission
