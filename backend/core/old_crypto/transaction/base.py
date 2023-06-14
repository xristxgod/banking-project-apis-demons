import abc
import enum
import decimal
from dataclasses import dataclass


class TransactionType(enum.IntEnum):
    TRANSFER = 0
    APPROVE = 1
    TRANSFER_FROM = 2
    # Only Tron
    FREEZE = 3
    UNFREEZE = 4


@dataclass()
class Commission:
    amount: decimal.Decimal
    extra: dict

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


class TransactionInterface(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def decoded_data(cls, data: str) -> tuple[tuple, TransactionType]: ...

    def __init__(self, client):
        self.client = client

    @abc.abstractmethod
    def commission(self, payload: dict) -> Commission: ...

    @abc.abstractmethod
    def make_response(self, transaction: dict) -> TransactionBody: ...

    @abc.abstractmethod
    def sign(self, payload: dict, private_key: str) -> str: ...

    @abc.abstractmethod
    def send(self, payload: dict) -> TransactionBody: ...
