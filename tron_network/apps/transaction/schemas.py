import enum
import decimal
from typing import Optional

from pydantic import BaseModel, Field
from tronpy.tron import PrivateKey, TAddress

import settings
from core.crypto.utils import to_sun
from apps.common.schemas import WithCurrencySchema


class TransactionType(int, enum.Enum):
    TRANSFER_NATIVE = 0
    FREEZE = 1
    UNFREEZE = 2
    TRANSFER = 3
    APPROVE = 4
    TRANSFER_FROM = 5
    DELEGATE = 6
    UN_DELEGATE = 7


class ResourceType(str, enum.Enum):
    ENERGY = 'ENERGY'
    BANDWIDTH = 'BANDWIDTH'


class ResponseCommission(BaseModel):
    fee: decimal.Decimal
    bandwidth: int
    energy: int


class BaseCreateTransactionSchema(WithCurrencySchema):
    amount: decimal.Decimal
    fee_limit: int = Field(default=settings.DEFAULT_FEE_LIMIT)

    @property
    def amount_sun(self) -> int:
        return to_sun(self.amount)

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


class BodyCreateApprove(BaseCreateTransactionSchema):
    owner_address: TAddress
    sender_address: TAddress

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.APPROVE


class BodyCreateTransferFrom(BodyCreateApprove):
    recipient_address: TAddress

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.TRANSFER_FROM


class BodyCreateFreeze(BaseCreateTransactionSchema):
    owner_address: TAddress
    recipient_address: Optional[TAddress] = Field(default=None)
    resource: ResourceType

    use_free_frozen_balance: bool = Field(default=False, description='Use a free frozen balance')

    @property
    def transaction_type(self) -> TransactionType:
        return TransactionType.FREEZE

    @property
    def sub_transaction_type(self) -> TransactionType:
        return TransactionType.DELEGATE

    @property
    def with_delegate(self) -> bool:
        return self.recipient_address is not None

    class Config:
        exclude = (
            'currency',
        )


class ResponseCreateTransaction(BaseModel):
    id: str
    commission: ResponseCommission


class ResponseCreateFreeze(BaseModel):
    general_commission: ResponseCommission


class BodySendTransaction(BaseModel):
    id: str
    private_key: str

    @property
    def private_key_obj(self) -> PrivateKey:
        return PrivateKey(bytes.fromhex(self.private_key))


class BaseResponseSendTransactionSchema(WithCurrencySchema):
    id: str
    timestamp: int
    commission: ResponseCommission
    amount: decimal.Decimal
    type: TransactionType


class ResponseSendTransfer(WithCurrencySchema):
    from_address: TAddress
    to_address: TAddress


class ResponseSendApprove(WithCurrencySchema):
    owner_address: TAddress
    sender_address: TAddress


class ResponseSendTransferFrom(ResponseSendApprove):
    recipient_address: TAddress


class FieldFreeze(ResponseSendTransfer):
    class Config:
        exclude = (
            'currency',
        )


class ResponseSendFreeze(BaseModel):
    freeze: FieldFreeze
    delegate: Optional[FieldFreeze] = None

    general_commission: ResponseCommission

    class Config:
        exclude = (
            'currency',
        )
