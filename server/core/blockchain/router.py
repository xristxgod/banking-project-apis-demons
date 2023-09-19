from fastapi import APIRouter

from core.blockchain import schemas
from core.blockchain.dao import NetworkDAO

router = APIRouter(
    tags=['Blockchain'],
    prefix='/blockchain',
)


@router.get(
    '/networks',
    response_model=list[schemas.BodyNetwork],
    description='All active networks',
)
async def get_networks():
    return [
        schemas.BodyNetwork(
            name=network.name,
            short_name=network.short_name,
            native_symbol=network.native_symbol,
            native_decimal_place=network.native_decimal_place,
            node_url=network.node_url,
            family=network.family,
        )
        for network in await NetworkDAO.get_current_networks()
    ]

