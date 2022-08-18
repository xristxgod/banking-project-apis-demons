from typing import Optional

from tronpy.tron import TAddress
from pydantic import BaseModel, Field, validator
from hdwallet.utils import generate_mnemonic


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