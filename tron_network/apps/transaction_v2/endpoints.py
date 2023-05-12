from fastapi import APIRouter

from apps.transaction_v2 import schemas
from apps.transaction_v2.storage import TransactionStorage

router = APIRouter()
storage = TransactionStorage()


async def _create_transaction(body: schemas.BaseCreateTransactionSchema):
    obj = await storage.create(body)
    return obj.to_schema


@router.post(
    '/transfer/create',
    response_model=schemas.ResponseCreateTransaction,
)
async def create_transfer(body: schemas.BodyCreateTransfer):
    return await _create_transaction(body)


@router.post(
    '/approve/create',
    response_model=schemas.ResponseCreateTransaction,
)
async def create_approve(body: schemas.BodyCreateApprove):
    return await _create_transaction(body)
