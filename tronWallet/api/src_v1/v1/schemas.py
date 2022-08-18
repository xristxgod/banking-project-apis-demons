import json
import secrets
import string
from typing import List, Optional, Dict

from pydantic import BaseModel, Field

from src_v1.utils.types import TronAccountPrivateKey, TronAccountPublicKey, TronAccountAddress, Amount, TokenTRC20
from config import AdminFee, decimals, ReportingAddress


# <<<----------------------------------->>> Body <<<----------------------------------------------------------------->>>


class BodyCreateWallet(BaseModel):
    """Body for create wallet"""
    words: Optional[str] = Field(default=None, description="Secret word for account recovery")

    def __init__(self, **kwargs):
        super(BodyCreateWallet, self).__init__(**kwargs)
        if self.words is None or self.words == "string":
            self.words = "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))


class BodyCreateTransaction(BaseModel):
    """Create a transaction TRX or Tokens TRC20"""
    fromAddress: TronAccountAddress = Field(default=None, description="Sender's address")
    outputs: Optional[List[Dict]] = Field(description="Sender's address")
    adminAddress: Optional[TronAccountAddress] = Field(default=None, description="Reporting addresses.")
    adminFee: Optional[Amount] = Field(default=None, description="Admin fee")
    
    def __init__(self, **kwargs):
        super(BodyCreateTransaction, self).__init__(**kwargs)
        if self.adminFee is None or self.adminFee == "string":
            self.adminFee = "%.8f" % decimals.create_decimal(AdminFee)
        if self.adminAddress is None or self.adminAddress == "string":
            self.adminAddress = ReportingAddress
        if isinstance(self.outputs, str):
            self.outputs = json.loads(self.outputs)


class BodySignAndSendTransaction(BaseModel):
    """Sign and send transaction"""
    createTxHex: str = Field(description="The hex of the unsigned transaction")
    privateKeys: List[TronAccountPrivateKey] = Field(default=None, description="The private key of the sender")
    maxFeeRate: Optional[Amount] = Field(default=None, description="Maximum transaction fee")

    def __init__(self, **kwargs):
        super(BodySignAndSendTransaction, self).__init__(**kwargs)
        if isinstance(self.privateKeys, str):
            self.privateKeys = json.loads(self.privateKeys)


# <<<----------------------------------->>> Response <<<------------------------------------------------------------->>>


class ResponseCreateWallet(BaseModel):
    """Response for create wallet"""
    words: str = Field(description="Secret word for account recovery")
    privateKey: TronAccountPrivateKey = Field(description="Private key for account")
    publicKey: TronAccountPublicKey = Field(description="Public key for account")
    address: TronAccountAddress = Field(description="Wallet address")


class ResponseGetBalance(BaseModel):
    """Response for get balance"""
    balance: Amount
    token: Optional[TokenTRC20] = None

    def __init__(self, **kwargs):
        super(ResponseGetBalance, self).__init__(**kwargs)
        if self.token is None:
            del self.token


class ResponseCreateTransaction(BaseModel):
    """Response to create transaction"""
    createTxHex: str = Field(description="The hex of the unsigned transaction")
    bodyTransaction: dict = Field(description="Transaction body in json")
    fee: Amount = Field(description="Transaction fee")
    energy: int = Field(description="Transaction energy")
    bandwidth: int = Field(description="Transaction bandwidth")
    maxFeeRate: Amount = Field(description="Maximum transaction fee")
