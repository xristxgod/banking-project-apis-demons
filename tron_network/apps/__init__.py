from fastapi import APIRouter

from .common import router as common_router
from .transaction import router as transaction_router
from .admin import router as admin_router


router = APIRouter()

router.include_router(common_router, tags=['Common'])
router.include_router(transaction_router, prefix='/tx', tags=['Transaction'])
router.include_router(transaction_router, prefix='/admin', tags=['Admin'])
