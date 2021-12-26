from pydantic import BaseModel
from typing import Optional
from solana.rpc.commitment import Commitment


class QueryBalance(BaseModel):
    pubkey: str
    commitment: Optional[Commitment] = None


class BodySendTransaction(BaseModel):
    from_pubkey: str
    to_pubkey: str
    lamports: int


class BodyCreateWallet(BaseModel):
    secret_word: str


class CreateWalletResponse(BaseModel):
    MnemonicPhrase: str
    PublicKey: str
    SecretWord: str
