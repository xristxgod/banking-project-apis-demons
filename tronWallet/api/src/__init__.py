from fastapi import APIRouter

from .services.wallet import router as router_wallet
from .services.transaction import router as router_transaction

router = APIRouter()
router.include_router(router_wallet.router)
router.include_router(router_transaction.router)