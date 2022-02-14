from typing import Optional, Dict, List, Union
from pydantic import BaseModel

from config import ADMIN_FEE, logger, decimal, ADMIN_ADDRESS


class ResponseAddressWithAmount(BaseModel):
    address: str
    amount: str


class BodyCreateTransaction(BaseModel):
    """Create a transaction TRX or Tokens TRC10, TRC20"""
    fromAddress: str
    outputs: List[Dict[str, str]]
    fee: Optional[int] = 21000
    adminFee: Optional[str] = None
    adminAddress: Optional[str] = None

    def __init__(self, **kwargs):
        super(BodyCreateTransaction, self).__init__(**kwargs)
        self.fromAddress = self.fromAddress.lower()
        if self.adminFee is None:
            self.adminFee = "%.18f" % ADMIN_FEE


class BodyAdminSignAndSendTransaction(BaseModel):
    """Sign and send transaction"""
    createTxHex: str
    privateKey: List[str]
    maxFeeRate: float


class ResponseCreateTransaction(BaseModel):
    """Response to create transaction"""
    createTxHex: str
    fee: str
    maxFeeRate: str
    time: Optional[int] = None
    amount: str
    senders: List[ResponseAddressWithAmount]
    recipients: List[ResponseAddressWithAmount]

    def __init__(self, **kwargs):
        super(ResponseCreateTransaction, self).__init__(**kwargs)
        for index, item in enumerate(self.senders):
            self.senders[index].address = item.address.lower()
        for index, item in enumerate(self.recipients):
            self.recipients[index].address = item.address.lower()


class ResponseCreateTokenTransaction(ResponseCreateTransaction):
    token: str

    def __init__(self, **kwargs):
        super(ResponseCreateTokenTransaction, self).__init__(**kwargs)
        for index, item in enumerate(self.senders):
            self.senders[index].address = item.address.lower()
        for index, item in enumerate(self.recipients):
            self.recipients[index].address = item.address.lower()
        logger.error(f'RESPONSE CREATE TX: {self.json()}')


class BodySendTransaction(BaseModel):
    createTxHex: str
    privateKeys: List[str]


class BodyGetTx(BaseModel):
    trxHash: str


class BodyAddressOnly(BaseModel):
    address: str

    def __init__(self, **kwargs):
        super(BodyAddressOnly, self).__init__(**kwargs)
        self.address = self.address.lower()


class BodyGetOptimalGas(BaseModel):
    fromAddress: str
    toAddress: str
    amount: str

    def __init__(self, **kwargs):
        super(BodyGetOptimalGas, self).__init__(**kwargs)
        self.fromAddress = self.fromAddress.lower()
        self.toAddress = self.toAddress.lower()


class ResponseSendTransaction(BaseModel):
    """Response to create transaction"""
    time: Optional[int] = None
    transactionHash: str
    amount: str
    fee: str
    senders: List[ResponseAddressWithAmount]
    recipients: List[ResponseAddressWithAmount]

    def __init__(self, **kwargs):
        super(ResponseSendTransaction, self).__init__(**kwargs)
        for index, item in enumerate(self.senders):
            self.senders[index].address = item.address.lower()
        for index, item in enumerate(self.recipients):
            self.recipients[index].address = item.address.lower()


class ResponseCreateWallet(BaseModel):
    mnemonicWords: str
    privateKey: str
    publicKey: str
    address: str

    def __init__(self, **kwargs):
        super(ResponseCreateWallet, self).__init__(**kwargs)
        self.address = self.address.lower()


class GetBalance(BaseModel):
    balance: str


class BodyCreateWallet(BaseModel):
    words: Optional[str] = None
