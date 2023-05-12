import decimal
import enum

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


class ResponseCreateTransaction(BaseModel):
    id: str
    commission: ResponseCommission


class BodySendTransaction(BaseModel):
    id: str
    private_key: str

    @property
    def private_key_obj(self) -> PrivateKey:
        return PrivateKey(bytes.fromhex(self.private_key))


class BaseResponseSendTransactionSchema(BaseModel):
    id: str
    timestamp: int
    commission: ResponseCommission
    amount: decimal.Decimal
    type: TransactionType


class ResponseSendTransfer(BaseResponseSendTransactionSchema, WithCurrencySchema):
    from_address: TAddress
    to_address: TAddress


class ResponseSendApprove(BaseResponseSendTransactionSchema, WithCurrencySchema):
    owner_address: TAddress
    sender_address: TAddress


class ResponseSendTransferFrom(ResponseSendApprove):
    recipient_address: TAddress
