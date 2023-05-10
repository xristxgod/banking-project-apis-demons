from fastapi import APIRouter, Query, status
from fastapi.exceptions import HTTPException

from core.crypto.calculator import FEE_METHOD_TYPES
from apps.common import schemas
from apps.common import services

router = APIRouter()


@router.post(
    '/create-wallet',
    response_model=schemas.ResponseCreateWallet
)
async def create_wallet(body: schemas.BodyCreateWallet):
    return await services.create_wallet(body)


@router.post(
    '/balance',
    response_model=schemas.ResponseWalletBalance,
)
async def wallet_balance(body: schemas.BodyWalletBalance):
    return await services.wallet_balance(body)


@router.post(
    '/allowance',
    response_model=schemas.ResponseAllowance,
)
async def allowance(body: schemas.BodyAllowance):
    return await services.allowance(body)


@router.post(
    '/transfer/create',
    response_model=schemas.ResponseCreateTransfer
)
async def create_transfer(body: schemas.BodyCreateTransfer):
    try:
        return await services.CreateTransfer.create_transfer(body)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )


@router.post(
    '/transaction/send',
    response_model=schemas.ResponseSendTransaction,
)
async def send_transaction(body: schemas.BodySendTransaction):
    return await services.send_transaction(body)


@router.post(
    '/fee/{method}/calculate',
    response_model=schemas.ResponseCommission,
)
async def fee_calculator(body: schemas.BodyCommission, method: FEE_METHOD_TYPES = FEE_METHOD_TYPES.TRANSFER):
    return await services.fee_calculator(body, method=method)
