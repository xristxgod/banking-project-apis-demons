from typing import Union, Optional

from pydantic import BaseModel
from api.src.utils.tron_typing import (
    TronAccountAddress, Amount, AmountToken, Tokens, TronAccountPrivateKey, TransactionHash
)

class BodyCreateTransaction(BaseModel):
    """Create a transaction TRX or Tokens TRC10, TRC20"""
    fromAddress: TronAccountAddress
    toAddress: TronAccountAddress
    amount: Union[Amount, AmountToken]
    token: Optional[Tokens] = None

class BodySignAndSendTransaction(BaseModel):
    """Sign and send transaction"""
    createTxHex: str
    privateKey: TronAccountPrivateKey

class ResponseCreateTransaction(BaseModel):
    """Response to create transaction"""
    createTxHex: str
    bodyTransaction: dict
    message: Optional[str] = "You have about 2-5 minutes to sign and send the order. Otherwise, it will be deleted!!!"

class ResponseTransactions(BaseModel):
    blockNumber: int
    timestamp: int
    datetime: str
    transactionHash: TransactionHash
    transactionType: str
    amount: Union[Amount, AmountToken]
    fee: Union[int, Amount]
    senders: TronAccountAddress
    recipients: Optional[TronAccountAddress] = None
    token: Optional[Tokens] = "TRX"

class ResponseGetFeeLimit(BaseModel):
    """Receive a commission for sending a token"""
    feeTRX: Amount


