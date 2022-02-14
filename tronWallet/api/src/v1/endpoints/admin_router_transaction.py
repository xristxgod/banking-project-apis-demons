from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.v1.services.admin_transaction import admin_transaction
from src.v1.schemas import ResponseCreateTransaction, BodyCreateTransaction, BodySignAndSendTransaction
from src.utils.types import Coins
from config import logger

router = APIRouter()

# <<<----------------------------------->>> Create transaction <<<--------------------------------------------------->>>
@router.post(
    "/tron/create-transaction", description="Create transaction for sending ONLY from AdminWallet",
    response_model=ResponseCreateTransaction, tags=["Admin Transaction TRX"]
)
async def create_transactions(body: BodyCreateTransaction):
    try:
        logger.error(f"Calling '/tron/create-transaction'")
        logger.error(f"<= SET addressFrom = ADMIN_ADDRESS: {body.json()}")
        result = await admin_transaction.create_admin_transaction(body=body)
        logger.error(f"<= SET addressFrom = ADMIN_ADDRESS Result: {result}")
        return result
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.post(
    "/tron_trc20_{coin}/create-transaction", description="Create transaction for sending ONLY from AdminWallet",
    response_model=ResponseCreateTransaction, tags=["Admin Transaction Tokens"]
)
async def create_trc20_transactions(body: BodyCreateTransaction, coin: str):
    try:
        logger.error(f"Calling '/tron-trc20-{coin}/create-transaction'")
        logger.error(f"<= SET addressFrom = ADMIN_ADDRESS: {body.json()}")
        if Coins.is_native(coin=coin):
            result = await admin_transaction.create_admin_transaction(body=body)
            logger.error(f"<= SET addressFrom = ADMIN_ADDRESS Result: {result}")
            return result
        elif Coins.is_token(coin=coin):
            result = await admin_transaction.create_trc20_admin_transactions(body=body, token=coin)
            logger.error(f"<= SET addressFrom = ADMIN_ADDRESS Result: {result}")
            return result
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Sing and Send transactions <<<------------------------------------------->>>

@router.post(
    "/{network}/sign-send-transaction", description="Sign and Send a transaction",
    response_class=JSONResponse, tags=["Admin Transaction TRX", "Admin Transaction Tokens"]
)
async def sign_and_send_transaction(body: BodySignAndSendTransaction, network: str):
    try:
        logger.error(f"Calling '/{network}/sign-send-transaction'")
        logger.error(f"<= SET privateKeys = [AdminPrivateKey]: {body.json()}")
        result = await admin_transaction.sign_send_admin_transaction(body=body)
        logger.error(f"<= SET privateKeys = [AdminPrivateKey] Result: {result}")
        return JSONResponse(content=result)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})