from fastapi import APIRouter
from .endpoints.transactions import transactions_router
from .endpoints.wallet import wallet_router


router_v2 = APIRouter(prefix="")

router_v2.include_router(transactions_router)
router_v2.include_router(wallet_router)
