from fastapi import APIRouter
from fastapi.responses import JSONResponse

from tronpy.tron import Tron, HTTPProvider

from src_v1.utils.node_status import native_balance_status, balancer_status, demon_status, node_status
from src_v1.utils.es_send import send_exception_to_kibana
from config import network


router = APIRouter()

# <<<------------------------------------>>> API Status <<<---------------------------------------------------------->>>


@router.get(
    "/", description="Find out the status of the API",
    response_class=JSONResponse, tags=["Project status"]
)
async def is_api_connected():
    """Find out the status of the API"""
    return JSONResponse(content={"message": True})


# <<<------------------------------------>>> Node Status <<<--------------------------------------------------------->>>


@router.get(
    "/is-node-alive", description="Find out the status of the Tron Node",
    response_class=JSONResponse, tags=["Project status"]
)
async def is_node_connected():
    """Find out the status of the Tron node"""
    try:
        if network == "mainnet":
            status = node_status()
            p = Tron().get_latest_block_number()
            o = Tron(HTTPProvider(endpoint_uri="http://tron-mainnet.mangobank.elcorp.io:8090")).get_latest_block_number()
            if not status:
                raise Exception
            return JSONResponse(content={
                "message": status,
                "our_block": o,
                "public_block": p,
                "gap": p - o
            })
        return JSONResponse(content={"message": True})
    except Exception as error:
        await send_exception_to_kibana(error, "ERROR: THE TRON NODE IS NOT ALIVE")
        try:
            p = Tron().get_latest_block_number()
            o = Tron(HTTPProvider(endpoint_uri="http://tron-mainnet.mangobank.elcorp.io:8090")).get_latest_block_number()
            return JSONResponse(content={
                "message": False,
                "our_block": o,
                "public_block": p,
                "gap": p - o
            })
        except Exception:
            return JSONResponse(content={"message": False})


# <<<------------------------------------>>> Admin Balance Status <<<------------------------------------------------>>>


@router.get(
    "/is-native-currency", description="Find out if there is enough native currency on the balance sheet",
    response_class=JSONResponse, tags=["Project status"]
)
async def is_there_native_currency_on_central_wallet():
    """Find out if there is enough native currency on the balance sheet"""
    try:
        return JSONResponse(content={"message": await native_balance_status()})
    except Exception as error:
        await send_exception_to_kibana(error, "ERROR: THERE IS NO NATIONAL CURRENCY ON THE BALANCE OF THE CENTRAL WALLET")
        return JSONResponse(content={"message": False})


# <<<------------------------------------>>> Demon Status <<<-------------------------------------------------------->>>


@router.get(
    "/is-demon-alive", description="Find out the status of the Tron Demon",
    response_class=JSONResponse, tags=["Project status"]
)
async def is_demon_alive():
    try:
        status = demon_status()
        p = Tron().get_latest_block_number()
        o = Tron(HTTPProvider(endpoint_uri="http://tron-mainnet.mangobank.elcorp.io:8090")).get_latest_block_number()
        if not status:
            raise Exception
        return JSONResponse(content={
            "message": status,
            "our_block": o,
            "public_block": p,
            "gap": p - o
        })
    except Exception as error:
        await send_exception_to_kibana(error, "ERROR: THE TRON DEMON IS NOT ALIVE")
        try:
            p = Tron().get_latest_block_number()
            o = Tron(HTTPProvider(endpoint_uri="http://tron-mainnet.mangobank.elcorp.io:8090")).get_latest_block_number()
            return JSONResponse(content={
                "message": False,
                "our_block": o,
                "public_block": p,
                "gap": p - o
            })
        except Exception:
            return JSONResponse(content={"message": False})


# <<<------------------------------------>>> Balancer Status <<<----------------------------------------------------->>>


@router.get(
    "/is-balancer-alive", description="Find out the status of the Tron Balancer",
    response_class=JSONResponse, tags=["Project status"]
)
async def is_balancer_alive():
    try:
        return JSONResponse(content={"message": balancer_status()})
    except Exception as error:
        await send_exception_to_kibana(error, "ERROR: THE TRON BALANCER IS NOT ALIVE")
        return JSONResponse(content={"message": False})
