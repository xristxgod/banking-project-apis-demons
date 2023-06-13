from fastapi import APIRouter

from . import common
from . import transactions

router = APIRouter()

router.include_router(common.router)
router.include_router(transactions.router)