from typing import Optional, List, Dict

from tronpy.tron import TAddress
from tronpy.keys import is_address
from pydantic import BaseModel, Field, validator
from hdwallet.utils import generate_mnemonic


# <<<----------------------------------->>> Query <<<------------------------------------------------------------->>>


class QueryAccount(BaseModel):
    address: TAddress = Field(description="Wallet address")

    @validator("address")
    def valid_address(cls, address: TAddress):
        if not is_address(address):
            raise ValueError("Address is bad")
        return address


# <<<----------------------------------->>> Body <<<------------------------------------------------------------->>>


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
    input: Optional[TAddress] = Field(default=None, description="Sender's address")
    output: List[Dict] = Field(description="Sender's address")
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
    async def valid_admin_fee(self, value: float):
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
    balance: float

    class Config:
        schema_extra = {
            "example": {
                "balance": 100.41244
            }
        }
