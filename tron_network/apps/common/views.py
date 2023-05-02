from fastapi import APIRouter, Depends

from tronpy.tron import TAddress

from core.utils import correct_currency, correct_address
from apps.common import schemas
from apps.common.services import CommonService

router = APIRouter()

common_service = CommonService()


@router.post(
    '/create-wallet',
    response_model=schemas.ResponseCreateWallet
)
async def create_wallet(body: schemas.BodyCreateWallet, encode: bool = True):
    return await common_service.create_wallet(body, is_encode=encode)


@router.post(
    '/balance/{currency}/{address}'
)
async def get_balance(address: TAddress = Depends(correct_address), currency: str = Depends(correct_currency)):
    return await common_service.get_balance(address, currency)
