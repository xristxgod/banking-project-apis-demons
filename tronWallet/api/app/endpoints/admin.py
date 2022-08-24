from typing import Optional

from fastapi import APIRouter, HTTPException, status
from tronpy.tron import TAddress

from src.external.elastic import ElasticController
from src.services.services import admin
from src.schemas import (
    QueryNetwork,
    BodyCreateTransaction, BodySendTransaction,
    ResponseBalance, ResponseOptimalFee, ResponseCreateTransaction, ResponseSendTransaction
)
from src.services import Transaction
from config import logger


router = APIRouter(
    prefix="/admin",
    tags=[
        "ADMIN"
    ],
    dependencies=[]
)


@router.get(
    "/{network}/balance/",
    response_model=ResponseBalance,
    tags=["WALLET"]
)
async def get_balance():
    return await admin.balance()


@router.get(
    "/{network}/transaction/to/{address}",
    response_model=ResponseOptimalFee,
    tags=["TRANSACTION"]
)
async def get_optimal_fee(network: QueryNetwork, address: TAddress):
    return await admin.optimal_fee(address=address, coin=network.network)


@router.post(
    "/{network}/create/transaction",
    response_model=ResponseCreateTransaction,
    tags=["TRANSACTION"]
)
async def create_transaction(network: QueryNetwork, body: BodyCreateTransaction):
    try:
        logger.error(f"Create admin transaction: {body.outputs}")
        transaction = await Transaction.create(
            account=admin,
            body=body,
            coin=network.network
        )
        await ElasticController.send_message(
            message=f"TX: {transaction.bodyTransaction.transactionId} | Create admin transaction: {body.outputs}"
        )
        return transaction
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
        logger.error(f"Send admin transaction")
        transaction = await Transaction.send(
            account=admin,
            body=body
        )
        await ElasticController.send_message(
            message=(
                f"TX: {transaction.bodyTransaction.transactionId} | "
                f"Send admin transaction: {transaction.bodyTransaction.outputs}"
            )
        )
        return transaction
    except Exception as error:
        logger.error(f"{error}")
        await ElasticController.send_exception(ex=error, message="Bad send transaction!")
        raise HTTPException(detail="Transaction error", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
