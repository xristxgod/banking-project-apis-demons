from typing import Union

from fastapi import APIRouter

from apps.transaction.endpoints import transaction
from apps.transaction.schemas import (
    ResponseCreateTransaction, ResponseCreateStake,
    ResponseSendTransfer, ResponseSendTransferFrom,
    ResponseSendFreeze, ResponseSendUnfreeze,
)
from apps.admin import schemas
from apps.admin.services import Admin

router = APIRouter()
admin = Admin(transaction)


@router.post(
    '/create-sub-wallet',
    response_model=schemas.ResponseAdminCreateWallet,
)
async def admin_create_sub_wallet(body: schemas.BodyAdminCreateWallet):
    return await admin.create_sub_wallet(body)


@router.post(
    '/transfer/create',
    response_model=ResponseCreateTransaction,
)
async def admin_create_transfer(body: schemas.BodyCreateTransfer):
    return await admin.transaction.create(body)


@router.post(
    '/transfer-from/create',
    response_model=ResponseCreateTransaction,
)
async def admin_create_transfer_from(body: schemas.BodyAdminCreateTransferFrom):
    return await admin.transaction.create(body)


@router.post(
    '/freeze/create',
    response_model=ResponseCreateStake,
)
async def admin_create_freeze(body: schemas.BodyAdminCreateFreeze):
    return await admin.transaction.create(body)


@router.post(
    '/unfreeze/create',
    response_model=ResponseCreateStake,
)
async def admin_create_unfreeze(body: schemas.BodyAdminCreateUnfreeze):
    return await admin.transaction.create(body)


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
    return await admin.transaction.send(body)
