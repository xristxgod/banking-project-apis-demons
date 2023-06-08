import enum

import decimal
from dataclasses import dataclass


class TransactionType(enum.IntEnum):
    TRANSFER = 0
    FREEZE = 1
    UNFREEZE = 2
    APPROVE = 3
    TRANSFER_FROM = 4


@dataclass()
class Commission:
    amount: decimal.Decimal
    bandwidth: int
    energy: int

    @property
    def fee(self):
        return self.amount


@dataclass()
class Participant:
    address: str
    amount: decimal.Decimal


@dataclass()
class TransactionBody:
    id: str
    timestamp: int
    commission: Commission
    amount: decimal.Decimal
    senders: list[Participant]
    recipients: list[Participant]
    type: TransactionType
    currency: str = 'TRX'

    @property
    def transaction_hash(self) -> str:
        return self.id
