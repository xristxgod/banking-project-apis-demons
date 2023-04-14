from typing import Tuple

from fastapi import APIRouter

from src.services.status import get_status
from src.schemas import ResponseStatus, ResponseBlock, ResponseBalance, ResponseMessageCount


router = APIRouter(
    tags=["STATUS"]
)


@router.get(
    "/",
    description="Find out the status of the API",
    response_model=ResponseStatus
)
async def api_status():
    return ResponseStatus(
        successfully=True
    )


@router.get(
    "/status/node",
    description="Find out the status of the Tron Node",
    response_model=Tuple[ResponseStatus, ResponseBlock]
)
async def node_status():
    return await get_status()


@router.get(
    "/status/balance",
    description="Find out if there is enough native currency on the balance sheet",
    response_model=Tuple[ResponseStatus, ResponseBalance]
)
async def balance_status():
    return await get_status("balance")


@router.get(
    "/status/demon",
    description="Find out the status of the Tron Demon",
    response_model=Tuple[ResponseStatus, ResponseBlock]
)
async def demon_status():
    return await get_status("demon")


@router.get(
    "/status/balancer",
    description="Find out the status of the Tron Balancer",
    response_model=Tuple[ResponseStatus, ResponseMessageCount]
)
async def balancer_status():
    return await get_status("balancer")
