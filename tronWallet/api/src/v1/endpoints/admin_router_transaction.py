from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.v1.services.create_transaction import create_transaction as crt
from src.v1.services.sign_send_transaction import sign_send_transaction
from src.v1.schemas import ResponseCreateTransaction, BodyCreateTransaction, BodySignAndSendTransaction
from src.utils.types import TronAccountAddress, Coins
from config import logger, AdminWallet, AdminPrivateKey

router = APIRouter()

# <<<----------------------------------->>> Create transaction <<<--------------------------------------------------->>>
@router.post(
    "/tron/create-transaction", description="Create transaction for sending ONLY from AdminWallet",
    response_model=ResponseCreateTransaction, tags=["Admin Transaction TRX"]
)
async def create_transactions(body: BodyCreateTransaction):
    try:
        logger.error(f"Calling '/tron/create-transaction'")
        body.fromAddress = AdminWallet
        logger.error(f"<= SET addressFrom = ADMIN_ADDRESS: {body.json()}")
        return crt.create_transaction(body=body)
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.post(
    "/tron_trc20_{coin}/create-transaction", description="Create transaction for sending ONLY from AdminWallet",
    response_model=ResponseCreateTransaction, tags=["Admin Transaction Tokens"]
)
async def create_trc20_transactions(body: BodyCreateTransaction, coin: str):
    try:
        logger.error(f"Calling '/tron-trc20-{coin}/create-transaction'")
        body.fromAddress = AdminWallet
        logger.error(f"<= SET addressFrom = ADMIN_ADDRESS: {body.json()}")
        if Coins.is_native(coin=coin):
            return crt.create_transaction(body=body)
        elif Coins.is_token(coin=coin):
            return crt.create_trc20_transactions(body=body, token=coin)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Coin "{coin}" was not found')
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

# <<<----------------------------------->>> Sing and Send transactions <<<------------------------------------------->>>

@router.post(
    "/tron/sign-send-transaction", description="Sign and Send a transaction",
    response_class=JSONResponse, tags=["Admin Transaction TRX"]
)
def sign_and_send_transaction(body: BodySignAndSendTransaction):
    try:
        logger.error(f"Calling '/tron/sign-send-transaction-for-internal-services'")
        body.privateKeys = [AdminPrivateKey]
        logger.error(f"<= SET privateKeys = [AdminPrivateKey]: {body.json()}")
        return JSONResponse(content=sign_send_transaction.sign_and_send_transaction(body=body))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})

@router.post(
    "/tron_trc20_{coin}/sign-send-transaction", description="Sign and Send a transaction",
    response_class=JSONResponse, tags=["Admin Transaction Tokens"]
)
def sign_and_send_transaction(body: BodySignAndSendTransaction, coin: str):
    try:
        logger.error(f"Calling '/tron-trc20-{coin}/sign-send-transaction-for-internal-services'")
        body.privateKeys = [AdminPrivateKey]
        logger.error(f"<= SET privateKeys = [AdminPrivateKey]: {body.json()}")
        return JSONResponse(content=sign_send_transaction.sign_and_send_transaction(body=body))
    except Exception as error:
        return JSONResponse(content={"error": str(error)})