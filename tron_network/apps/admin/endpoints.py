from typing import Union

from fastapi import APIRouter

from apps.transaction.schemas import (
    ResponseCreateTransaction, ResponseCreateStake,
    ResponseSendTransfer, ResponseSendTransferFrom,
    ResponseSendFreeze, ResponseSendUnfreeze,
)
from apps.transaction.endpoints import transaction
from apps.admin import schemas

router = APIRouter()


@router.post(
    '/transfer/create',
    response_model=ResponseCreateTransaction,
)
async def admin_create_transfer(body: schemas.BodyCreateTransfer):
    return await transaction.create(body)


@router.post(
    '/transfer-from/create',
    response_model=ResponseCreateTransaction,
)
async def admin_create_transfer_from(body: schemas.BodyAdminCreateTransferFrom):
    return await transaction.create(body)


@router.post(
    '/freeze/create',
    response_model=ResponseCreateStake,
)
async def admin_create_freeze(body: schemas.BodyAdminCreateFreeze):
    return await transaction.create(body)


@router.post(
    '/unfreeze/create',
    response_model=ResponseCreateStake,
)
async def admin_create_unfreeze(body: schemas.BodyAdminCreateUnfreeze):
    return await transaction.create(body)


@router.put(
    '/transaction/send',
    response_model=Union[
        ResponseSendTransfer,
        ResponseSendTransferFrom,
        ResponseSendFreeze,
        ResponseSendUnfreeze,
    ]
)
async def admin_send_transaction(body: schemas.BodySendTransaction):
    return await transaction.send(body)
