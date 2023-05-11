from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from core.crypto.calculator import FEE_METHOD_TYPES
from apps.transaction import schemas
from apps.transaction import services

router = APIRouter()


@router.post(
    '/transfer/create',
    response_model=schemas.ResponseCreateTransaction
)
async def create_transfer(body: schemas.BodyCreateTransfer):
    try:
        return await services.CreateTransfer.create(body)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )


@router.post(
    '/approve/create',
    response_model=schemas.ResponseCreateTransaction,
)
async def create_approve(body: schemas.BodyCreateApprove):
    return await services.CreateApprove.create(body)


@router.post(
    '/transfer-from/create',
    response_model=schemas.ResponseCreateTransaction
)
async def create_transfer_from(body: schemas.BodyCreateTransferFrom):
    pass


@router.post(
    '/transaction/send',
    response_model=schemas.ResponseSendTransaction,
)
async def send_transaction(body: schemas.BodySendTransaction):
    return await services.SendTransaction.send_transaction(body)


@router.post(
    '/fee/{method}/calculate',
    response_model=schemas.ResponseCommission,
)
async def fee_calculator(body: schemas.BodyCommission, method: FEE_METHOD_TYPES = FEE_METHOD_TYPES.TRANSFER):
    return await services.fee_calculator(body, method=method)
