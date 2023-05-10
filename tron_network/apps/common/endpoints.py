from fastapi import APIRouter

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
    response_model=schemas.ResponseCreateWallet,
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
    pass
