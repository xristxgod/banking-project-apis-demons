from typing import Optional, List, Dict

from tronpy.tron import TAddress
from tronpy.keys import is_address
from pydantic import BaseModel, Field, validator
from hdwallet.utils import generate_mnemonic

from .external import CoinController


NETWORKS = [
    ("trx", "tron"),
    *[
        (
            f"{coin.symbol.lower()}",
            f"tron-{coin.symbol.lower()}",
            f"tron-trc20-{coin.symbol.lower()}",
            f"trx-{coin.symbol.lower()}",
            f"trx-trc20-{coin.symbol.lower()}"
        )
        for coin in CoinController.get_all_token()

    ]
]


# <<<----------------------------------->>> Data <<<----------------------------------------------------------------->>>


class ParticipantData(BaseModel):
    address: TAddress = Field(description="Wallet address")
    amount: float = Field(default=0, description="Transaction amount")

    class Config:
        schema_extra = {
            "example": {
                "address": "TEAoUFfm3H5hYXo1X2VHwYFu1KMPDtZR4G",
                "amount": 10
            }
        }


class TransactionData(BaseModel):
    timestamp: int = Field(description="Transaction time")
    transactionId: str = Field(description="Transaction hash")
    inputs: List[ParticipantData] = Field(description="Senders address")
    outputs: List[ParticipantData] = Field(description="Recipients address")
    amount: float = Field(default=0, description="Transaction amount")
    fee: float = Field(default=0, description="Transaction fee")
    token: Optional[str] = Field(default=None, description="Transaction Token")

    def __init__(self, **kwargs):
        super(TransactionData, self).__init__(**kwargs)
        if self.token is None:
            del self.token

    class Config:
        schema_extra = {
            "example": {
                "timestamp": 1660372014,
                "transactionId": "96756db705d81f48d00ca9f1cd75bde3a8357aafa7e9698b776a1336f2b3778f",
                "inputs": [
                    {
                        "address": "TEAoUFfm3H5hYXo1X2VHwYFu1KMPDtZR4G",
                        "amount": 10
                    }
                ],
                "outputs": [
                    {
                        "address": "TWCQvcJ2JkWamoXWs7rAf7PiWTYaiB8WHx",
                        "amount": 10
                    }
                ],
                "amount": 10,
                "fee": 0,
                "token": "USDT"
            }
        }


# <<<----------------------------------->>> Query <<<---------------------------------------------------------------->>>


class QueryAccount(BaseModel):
    address: TAddress = Field(description="Wallet address")

    @validator("address")
    def valid_address(cls, address: TAddress):
        if not is_address(address):
            raise ValueError("Address is bad")
        return address


class QueryNetwork(BaseModel):
    """
    List of networks:
        ** trx, tron - For native currency
        ** usdt, tron-usdt, tron-trc20-usdt, trx-usdt, trx-trc20-usdt - For USDT token
        ** usdc, tron-usdc, tron-trc20-usdc, trx-usdc, trx-trc20-usdc - For USDC token
    """
    network: str = Field(description="Network & token")

    @validator("network")
    def valid_network(cls, network: str):
        if len(list(filter(lambda x: network in x, NETWORKS))) == 0:
            raise ValueError("This network was not found")
        return list(filter(lambda x: x.symbol in network, CoinController.get_all_token()))[0]


# <<<----------------------------------->>> Body <<<----------------------------------------------------------------->>>


class BodyCreateWallet(BaseModel):
    mnemonicWords: str = Field(default=None, description="Secret word for account recovery")

    @validator("mnemonicWords")
    def valid_mnemonic_words(cls, mnemonic_words: Optional[str] = None):
        if isinstance(mnemonic_words, str) and len(mnemonic_words.split()) not in [12, 18, 24]:
            raise ValueError("Mnemonic words must be long: 12, 18, 24")
        if mnemonic_words is None:
            return generate_mnemonic(language="english", strength=128)
        return mnemonic_words

    class Config:
        schema_extra = {
            "example": {
                "mnemonicWords": "snack butter whip wood monkey canoe shine flush clutch year alien frozen swarm cluster patient glide resemble track"
            }
        }


class BodyCreateTransaction(BaseModel):
    input: Optional[TAddress] = Field(default=None, description="Senders address")
    outputs: List[Dict] = Field(description="Recipients address")
    adminAddress: Optional[TAddress] = Field(default=None, description="Reporting addresses.")
    adminFee: Optional[float] = Field(default=None, description="Admin fee")

    @validator("input")
    async def valid_input(cls, address: TAddress):
        if not is_address(address):
            raise ValueError("Address is bad")
        return address

    @validator("output")
    async def valid_output(cls, output: List[Dict]):
        if not isinstance(output, list):
            raise ValueError("Output must be list")
        if len(output) == 0:
            raise ValueError("Output must contain 1 or more values.")
        for data in output:
            data = list(data.items())[0]
            if not is_address(data[0]):
                raise ValueError("Address is bad")
            _ = float(data[1])
        return output

    @validator("adminAddress")
    async def valid_admin_address(cls, address: Optional[TAddress] = None):
        if address is not None:
            if not is_address(address):
                raise ValueError("Address is bad")
        return address

    @validator("adminFee")
    async def valid_admin_fee(cls, value: Optional[float] = None):
        if cls.adminAddress is not None and value is None:
            return 10.00
        if isinstance(value, str) and not value.isdigit():
            raise ValueError("Admin fee must be a number")
        if value < 0:
            raise ValueError("Admin fee must be greater than 0")
        return value

    class Config:
        schema_extra = {
            "example": {
                "input": "TP2Xz1zytoYtzwdVUXVPmcX2UZrdxXNVhK",
                "output": [
                    {
                        "TWCQvcJ2JkWamoXWs7rAf7PiWTYaiB8WHx": 100.23
                    }
                ],
                "adminAddress": "TEiVn3A6npbb4EJGb6N3BHifKzkhJG1ksx",
                "adminFee": 13.441
            }
        }


class BodySendTransaction(BaseModel):
    createTxHex: str = Field(description="The hex of the unsigned transaction")
    privateKeys: Optional[List[str]] = Field(default=None, description="The private key of the sender")
    maxFeeRate: Optional[float] = Field(default=None, description="Maximum transaction fee")

    class Config:
        schema_extra = {
            "example": {
                "createTxHex": "7b22636f6e7472616374223a205b7b22706172616d65746572223a207b2276616c7565223a207b226f776e65725f61646472657373223a2022343132653131646131346633353935326566366664363234333263373933656665313734363262636339222c2022636f6e74726163745f61646472657373223a2022343161663136353731303831643332366436303830376265663131366230633035366139343733363833222c202264617461223a202261393035396362623030303030303030303030303030303030303030303030306464653165303530636439643038366635656238626539376535336539636330343336616164633930303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030393839363830222c202263616c6c5f746f6b656e5f76616c7565223a20302c202263616c6c5f76616c7565223a20302c2022746f6b656e5f6964223a20307d2c2022747970655f75726c223a2022747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e54726967676572536d617274436f6e7472616374227d2c202274797065223a202254726967676572536d617274436f6e7472616374227d5d2c202274696d657374616d70223a20313636303839303135303434342c202265787069726174696f6e223a20313636303839303231303434342c20227265665f626c6f636b5f6279746573223a202231643938222c20227265665f626c6f636b5f68617368223a202266366330626561316664633032613236222c20226665655f6c696d6974223a2031303030303030307d",
                "privateKeys": [
                    "3ce030d9b23bc5d6ed9c79228a3ee92c65395ada12c472f2574673280cf3a017"
                ],
                "maxFeeRate": 10.344,
            }
        }


# <<<----------------------------------->>> Response <<<------------------------------------------------------------->>>


class ResponseCreateWallet(BaseModel):
    mnemonicWords: str = Field(description="Secret word for account recovery")
    privateKey: str = Field(description="Private key for account")
    publicKey: str = Field(description="Public key for account")
    address: TAddress = Field(description="Wallet address")

    class Config:
        schema_extra = {
            "example": {
                "mnemonicWords": "snack butter whip wood monkey canoe shine flush clutch year alien frozen swarm cluster patient glide resemble track",
                "privateKey": "3ce030d9b23bc5d6ed9c79228a3ee92c65395ada12c472f2574673280cf3a017",
                "publicKey": "03e4eeb3fd1875fe17d5455d889b3b677c36ffecd25b865ad0fc920a1554f10422",
                "address": "TP2Xz1zytoYtzwdVUXVPmcX2UZrdxXNVhK"
            }
        }


class ResponseBalance(BaseModel):
    balance: float = Field(default=0, description="Account balance")

    class Config:
        schema_extra = {
            "example": {
                "balance": 100.41244
            }
        }


class ResponseCreateTransaction(BaseModel):
    createTxHex: str = Field(description="The hex of the unsigned transaction")
    bodyTransaction: TransactionData = Field(description="Transaction body")

    class Config:
        schema_extra = {
            "example": {
                "createTxHex": "7b22636f6e7472616374223a205b7b22706172616d65746572223a207b2276616c7565223a207b226f776e65725f61646472657373223a2022343132653131646131346633353935326566366664363234333263373933656665313734363262636339222c2022636f6e74726163745f61646472657373223a2022343161663136353731303831643332366436303830376265663131366230633035366139343733363833222c202264617461223a202261393035396362623030303030303030303030303030303030303030303030306464653165303530636439643038366635656238626539376535336539636330343336616164633930303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030393839363830222c202263616c6c5f746f6b656e5f76616c7565223a20302c202263616c6c5f76616c7565223a20302c2022746f6b656e5f6964223a20307d2c2022747970655f75726c223a2022747970652e676f6f676c65617069732e636f6d2f70726f746f636f6c2e54726967676572536d617274436f6e7472616374227d2c202274797065223a202254726967676572536d617274436f6e7472616374227d5d2c202274696d657374616d70223a20313636303839303135303434342c202265787069726174696f6e223a20313636303839303231303434342c20227265665f626c6f636b5f6279746573223a202231643938222c20227265665f626c6f636b5f68617368223a202266366330626561316664633032613236222c20226665655f6c696d6974223a2031303030303030307d",
                "bodyTransaction": {
                    "timestamp": 1660372014,
                    "transactionId": "96756db705d81f48d00ca9f1cd75bde3a8357aafa7e9698b776a1336f2b3778f",
                    "inputs": [
                        {
                            "address": "TEAoUFfm3H5hYXo1X2VHwYFu1KMPDtZR4G",
                            "amount": 10
                        }
                    ],
                    "outputs": [
                        {
                            "address": "TWCQvcJ2JkWamoXWs7rAf7PiWTYaiB8WHx",
                            "amount": 10
                        }
                    ],
                    "amount": 10,
                    "fee": 0,
                    "token": "USDT"
                }
            }
        }


class ResponseSendTransaction(BaseModel):
    timestamp: int = Field(description="Transaction time")
    transactionId: str = Field(description="Transaction hash")
    bodyTransaction: TransactionData = Field(description="Transaction body")
    successfully: Optional[bool] = Field(default=True, description="Transaction status")

    class Config:
        schema_extra = {
            "example": {
                "timestamp": 1660372014,
                "transactionId": "96756db705d81f48d00ca9f1cd75bde3a8357aafa7e9698b776a1336f2b3778f",
                "successfully": True
            }
        }


class ResponseStatus(BaseModel):
    message: Optional[str] = Field(default=None, description="Error message")
    successfully: bool = Field(default=True, description="Status system. Work or not!")

    def __init__(self, **kwargs):
        super(ResponseStatus, self).__init__(**kwargs)
        if self.message is None:
            del self.message

    class Config:
        schema_extra = {
            "example": {
                "message": "Problems with the node. There are no active connections",
                "successfully": False
            }
        }


class ResponseBlock(BaseModel):
    ourBlock: int = Field(description="Our node block")
    publicBlock: int = Field(description="Public node block")

    class Config:
        schema_extra = {
            "example": {
                "ourBlock": 26725523,
                "publicBlock": 26725523
            }
        }


class ResponseMessageCount(BaseModel):
    messageCount: int = Field(default=0, description="Number of messages in the balancer")

    class Config:
        schema_extra = {
            "example": {
                "messageCount": 0
            }
        }
