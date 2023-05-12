import decimal
import enum

from pydantic import BaseModel, Field, validator
from tronpy.tron import PrivateKey, TAddress

import settings
from core.crypto import node
from core.crypto.contract import Contract


class TransactionType(int, enum.Enum):
    TRANSFER_NATIVE = 0
    FREEZE = 1
    UNFREEZE = 2
    TRANSFER = 3
    APPROVE = 4
    TRANSFER_FROM = 5


class SchemaWithCurrency(BaseModel):
    currency: str = Field(default='TRX')

    @property
    def is_native(self) -> bool:
        return self.currency == 'TRX'

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
        if not cls.use_native() and currency == 'TRX':
            raise ValueError("Don't use native!")
        elif currency != 'TRX' and not node.has_currency(currency):
            raise ValueError(f'Currency: {currency} not found')
        return currency


class ResponseCommission(BaseModel):
    fee: decimal.Decimal
    bandwidth: int
    energy: int


class BaseCreateTransactionSchema(SchemaWithCurrency):
    amount: decimal.Decimal
    fee_limit: int = Field(default=settings.DEFAULT_FEE_LIMIT)

    @property
    def transaction_type(self) -> TransactionType:
        raise NotImplementedError()


class BodyCreateTransfer(BaseCreateTransactionSchema):
    from_address: TAddress
    to_address: TAddress

    @property
    def transaction_type(self) -> TransactionType:
        if self.is_native:
            return TransactionType.TRANSFER_NATIVE
        return TransactionType.TRANSFER


class ResponseCreateTransaction(SchemaWithCurrency):
    id: str
    commission: ResponseCommission


class BodySendTransaction(BaseModel):
    id: str
    private_key: str

    @property
    def private_key_obj(self) -> PrivateKey:
        return PrivateKey(bytes.fromhex(self.private_key))


class BaseResponseSendTransactionSchema(SchemaWithCurrency):
    id: str
    commission: ResponseCommission
    amount: decimal.Decimal
    type: TransactionType
