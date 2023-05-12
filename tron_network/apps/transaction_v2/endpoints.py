from fastapi import APIRouter, HTTPException, status

from apps.transaction_v2 import schemas
from apps.transaction_v2.storage import TransactionStorage

router = APIRouter()
storage = TransactionStorage()


async def _create_transaction(body: schemas.BaseCreateTransactionSchema,
                              save: bool = True) -> schemas.ResponseCreateTransaction:
    obj = await storage.create(body, save=save)
    return obj.to_schema


async def _send_transaction(body: schemas.BodySendTransaction,
                            delete: bool = True) -> schemas.BaseResponseSendTransactionSchema:
    try:
        obj = await storage.get(body.id, delete=delete)
        await obj.sign(private_key=body.private_key_obj)
        return await obj.send()
    except storage.TransactionNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )


@router.on_event('')
async def clear_buffer_event():
    await storage.clear_buffer()


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


@router.post(
    '/transfer-from/create',
    response_model=schemas.ResponseCreateTransaction,
)
async def create_transfer_from(body: schemas.BodyCreateTransferFrom):
    return await _create_transaction(body)


@router.put(
    '/transaction/send',
    response_model=[
        schemas.ResponseSendTransfer,
        schemas.ResponseSendApprove,
        schemas.ResponseSendTransferFrom,
    ]
)
async def send_transaction(body: schemas.BodySendTransaction):
    return await _send_transaction(body)