from fastapi import APIRouter

from src.v1.endpoints import router_wallet, router_transaction, admin_router_transaction

router = APIRouter()

# Include router Wallet
router.include_router(router_wallet.router)
# Include router Transaction
router.include_router(router_transaction.router)
# Include router Admin Transaction
router.include_router(admin_router_transaction.router)