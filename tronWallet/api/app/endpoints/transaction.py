from typing import Optional

from fastapi import APIRouter
from tronpy.tron import TAddress

from src.schemas import (
    QueryAccount, QueryNetwork,
    BodyCreateTransaction, BodySendTransaction,
    ResponseOptimalFee, ResponseCreateTransaction, ResponseSendTransaction,
    TransactionData
)
from src.services import (
    AccountController, Account,
    Transaction, TransactionParser
)


router = APIRouter(
    tags=["TRANSACTION"]
)


@router.get(
    "/{network}/transaction/{account}/to/{address}",
    response_model=ResponseOptimalFee
)
async def get_optimal_fee(network: QueryNetwork, account: QueryAccount, address: TAddress):
    return await AccountController(Account(address=account.address)).optimal_fee(address=address, coin=network.network)


@router.get(
    "/transaction/{transaction_id}",
    response_model=TransactionData
)
async def get_transaction(transaction_id: str):
    return await TransactionParser.transaction(
        transaction_id=transaction_id
    )


@router.get(
    "/transactions/{account}",
    response_model=TransactionData
)
async def get_transactions(account: QueryAccount):
    return await TransactionParser.all_transactions(
        address=account.address
    )


@router.post(
    "/{network}/create/transaction",
    response_model=ResponseCreateTransaction
)
async def create_transaction(network: QueryNetwork, body: BodyCreateTransaction):
    return await Transaction.create(
        account=AccountController(Account(address=body.input)),
        body=body,
        coin=network.network
    )


@router.patch(
    "/{network}/send/transaction",
    response_model=ResponseSendTransaction
)
async def send_transaction(body: BodySendTransaction, network: Optional[QueryNetwork] = None):
    return await Transaction.send(
        account=AccountController(Account(privateKey=body.privateKeys[0])),
        body=body
    )
