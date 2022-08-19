from typing import Optional

from fastapi import APIRouter, HTTPException, status
from tronpy.tron import TAddress

from src.external import ElasticController
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
from config import logger


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
    try:
        logger.error(f"Create transaction: {body.input} -> {body.outputs}")
        await ElasticController.send_message(message=f"Create transaction: {body.input} -> {body.outputs}")
        return await Transaction.create(
            account=AccountController(Account(address=body.input)),
            body=body,
            coin=network.network
        )
    except Exception as error:
        logger.error(f"{error}")
        await ElasticController.send_exception(ex=error, message="Bad create transaction!")
        raise HTTPException(detail="Transaction error", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


@router.patch(
    "/{network}/send/transaction",
    response_model=ResponseSendTransaction
)
async def send_transaction(body: BodySendTransaction, network: Optional[QueryNetwork] = None):
    try:
        logger.error(f"Send transaction")
        transaction = await Transaction.send(
            account=AccountController(Account(privateKey=body.privateKeys[0])),
            body=body
        )
        await ElasticController.send_message(
            message=f"Send transaction: {transaction.bodyTransaction.inputs} -> {transaction.bodyTransaction.outputs}"
        )
        return transaction
    except Exception as error:
        logger.error(f"{error}")
        await ElasticController.send_exception(ex=error, message="Bad send transaction!")
        raise HTTPException(detail="Transaction error", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
