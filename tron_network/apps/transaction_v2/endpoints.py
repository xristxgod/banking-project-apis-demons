from fastapi import APIRouter

from apps.transaction_v2 import schemas
from apps.transaction_v2.storage import TransactionStorage

router = APIRouter()
storage = TransactionStorage()


@router.post(
    '/transfer/create',
    response_model=schemas.ResponseCreateTransaction,
)
async def create_transfer(body: schemas.BodyCreateTransfer):
    obj = await storage.create(body)
    return obj.to_schemas()
