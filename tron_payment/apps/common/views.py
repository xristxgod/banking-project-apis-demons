from fastapi import APIRouter

from apps.common import schemas
from apps.common import services


router = APIRouter()


@router.post(
    '/wallet/create',
    response_model=schemas.ResponseCreateWallet,
)
async def create_wallet(body: schemas.BodyCreateWallet):
    return await services.create_wallet(body)


@router.post(
    '/wallet/balance',
    response_model=schemas.ResponseBalance,
)
async def wallet_balance(body: schemas.BodyBalance):
    return await services.get_balance(body)
