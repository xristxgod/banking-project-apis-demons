from typing import Union, List, Optional

from pydantic import BaseModel, Field
from api.src.utils.tron_typing import (
    TronAccountPassphrase, TronAccountPrivateKey, TronAccountPublicKey,
    TronAccountAddress, Tokens, AmountToken, Amount, TokenTRC20,
    TokenTRC10, ContractAddress
)

class BodyCreateWallet(BaseModel):
    """Body for create wallet"""
    passphrase: Optional[TronAccountPassphrase] = None

class ResponseCreateWallet(BaseModel):
    """Response for create wallet"""
    passphrase: TronAccountPassphrase
    privateKey: TronAccountPrivateKey
    publicKey: TronAccountPublicKey
    address: TronAccountAddress
    message: Optional[str] = "IMPORTANT!!! This account will become active after adding at least 0.1 TRX to his account!!!"

class ResponseGetBalance(BaseModel):
    """Response for get balance"""
    balance: Union[Amount, AmountToken]
    token: Optional[Tokens] = None

class ResponseGetAllTokens(BaseModel):
    tokensTRC20: List[TokenTRC20]
    tokensTRC10: List[TokenTRC10]

class BodyAddNewTokenTRC20(BaseModel):
    address: ContractAddress

class ResponseAddNewTokenTRC20(BaseModel):
    message: str

class BodyFreezeBalance(BaseModel):
    """Freeze balance to get energy or bandwidth, for 3 days"""
    ownerAddress: TronAccountAddress
    toAddress: Optional[TronAccountAddress] = None
    amount: Amount
    resource: Optional[str] = "ENERGY"    # or "BANDWIDTH"

class BodyUnfreezeBalance(BaseModel):
    """Unfreeze balance to get TRX back."""
    ownerAddress: TronAccountAddress
    toAddress: Optional[TronAccountAddress] = None
    resource: Optional[str] = "ENERGY"  # or "BANDWIDTH"