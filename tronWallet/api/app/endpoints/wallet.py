from typing import Optional

from fastapi import APIRouter, HTTPException, status

from src import core
from src.schemas import (
    QueryAccount, QueryNetwork,
    BodyCreateWallet,
    ResponseCreateWallet, ResponseBalance
)
from src.services import Account, AccountController


router = APIRouter()


@router.post(
    "/{network}/create/wallet",
    response_model=ResponseCreateWallet,
    summary="Create wallet",
    response_description="Wallet created",
    response_model_exclude_unset=True
)
async def create_wallet(body: BodyCreateWallet, network: Optional[QueryNetwork] = None):
    return core.create_wallet(body=body)


@router.get(
    "/{network}/balance/{account}",
    response_model=ResponseBalance,
    summary="Get account balance",
    response_model_exclude_unset=True
)
async def get_balance(network: QueryNetwork, account: QueryAccount):
    return AccountController(Account(address=account.address)).balance(network.network)
