import decimal
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from tronpy.tron import TAddress


@dataclass()
class ProcessingTransaction:
    transaction: Dict                                   # Transaction Data
    addresses: List[TAddress]                           # Wallet addresses in Database
    timestamp: int                                      # Time to send transaction
    transactionsHash: List[str]                         # Transactions in Database


@dataclass()
class SmartContractData:
    amount: decimal.Decimal                             # Transaction amount
    symbol: str                                         # Token name


@dataclass()
class Participant:
    address: TAddress                                   # Participant wallet address
    amount: decimal.Decimal                             # Transaction amount


@dataclass()
class Transaction:
    timestamp: int                                      # Time to send transaction
    transactionHash: str                                # Transaction hash/id
    amount: decimal.Decimal                             # Transaction amount
    fee: decimal.Decimal                                # Transaction fee
    inputs: List[Participant] = field(default=list)     # Sender transaction
    outputs: List[Participant] = field(default=list)    # Recipient transaction
    token: Optional[str] = field(default=None)          # Token symbol


@dataclass()
class BodyTransaction:
    address: TAddress                                   # Participant transaction in has to db
    transactions: List[Transaction]                     # Transaction list


@dataclass()
class SendTransactionData:
    transactionPackage: BodyTransaction                 # Transactions for send
    addresses: List[TAddress]                           # Wallet addresses in Database
    transactionsHash: List[str]                         # Transactions in Database
    blockNumber: int                                    # Block in Blockchain


@dataclass()
class Header:
    block: int                                          # Block in Blockchain
    network: str                                        # Example: tron, tron_trc20_usdt, tron_trc20_usdc, etc.


@dataclass()
class RangeSearch:
    startBlock: int                                     # Start of the search
    endBlock: int                                       # End of the search
    addresses: List[TAddress] = field(default=None)     # Wallet addresses in Database or user write


@dataclass()
class ListSearch:
    listBlock: List[int]                                # List of the block
    addresses: List[TAddress] = field(default=None)     # Wallet addresses in Database or user write


@dataclass()
class Start:
    startBlock: Optional[int] = field(default=None)     # Start of the search
    endBlock: Optional[int] = field(default=None)       # End of the search
    listBlock: List[int] = field(default=None)          # List of the block
    addresses: List[TAddress] = field(default=None)     # Wallet addresses in Database or user write


@dataclass()
class BalancerMessage:
    address: TAddress                                   # Wallet address
    network: str                                        # Network: TRX, USDT, USDC, etc.


__all__ = [
    "ProcessingTransaction", "SmartContractData", "Participant",
    "Transaction", "BodyTransaction", "SendTransactionData", "Header",
    "RangeSearch", "ListSearch", "Start", "BalancerMessage"
]