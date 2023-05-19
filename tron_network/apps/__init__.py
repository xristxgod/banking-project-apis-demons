from fastapi import APIRouter, Depends

from .common import router as common_router
from .transaction import router as transaction_router
from .admin import router as admin_router

from core.auth import auth


router = APIRouter()

router.include_router(common_router, tags=['Common'])
router.include_router(transaction_router, prefix='/tx', tags=['Transaction'])
router.include_router(transaction_router, prefix='/admin', tags=['Admin'], dependencies=[
    Depends(auth.get_token_header),
    Depends(auth.valid_admin_ips),
])
