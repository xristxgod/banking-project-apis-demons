from fastapi import APIRouter
from .endpoints import admin, status, transaction, wallet


router = APIRouter()


router.include_router(admin.router)         # Router for admin
router.include_router(wallet.router)        # Router for work wallet
router.include_router(transaction.router)   # Router for work transaction
router.include_router(status.router)        # Router for check status
