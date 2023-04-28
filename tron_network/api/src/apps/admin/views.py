from fastapi import APIRouter

from src.apps.admin import schemas
from src.apps.admin import services

router = APIRouter()


@router.post(
    '/wallet/create',
    response_model=schemas.ResponseAdminCreateWallet,
    tags=['Admin Wallet'],
)
async def create_wallet(body: schemas.BodyAdminCreateWallet):
    return await services.create_wallet(body)


@router.post(
    '/wallet/balance',
    response_model=schemas.ResponseAdminBalance,
    tags=['Admin Wallet'],
)
async def balance(body: schemas.BodyAdminBalance):
    return await services.wallet_balance(body)


@router.post(
    '/transfer/create',
    response_model=schemas.ResponseAdminTransfer,
    tags=['Admin transaction'],
)
async def transfer(body: schemas.ResponseAdminTransfer):
    pass
