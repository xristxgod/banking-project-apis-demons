from fastapi import APIRouter, status, Form
from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import settings
from apps.wallets.schemas import WalletType, MetamaskChainId

WALLET_DIR = settings.APPS_DIR / 'wallets'

router = APIRouter()
templates = Jinja2Templates(directory=WALLET_DIR / 'templates')


@router.get(
    '/selector/{typ}',
    response_class=HTMLResponse,
)
async def wallet_selector(request: Request, typ: WalletType):
    context = {
        'request': request,
        'typ': WalletType,
    }
    match typ:
        case WalletType.METAMASK:
            template = 'metamask.html'
            context.update({
                'title': 'Metamask',
                'chainIds': [
                    MetamaskChainId.ETH.value,
                    MetamaskChainId.BSC.value,
                ]
            })
        case _:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='This wallet is not supported!'
            )

    return templates.TemplateResponse(
        template,
        context=context,
    )


@router.post(
    '/connect/{typ}',
    response_class=HTMLResponse,
)
async def connect(
        request: Request, typ: WalletType,
        chain_id: int = Form(...),
        address: str = Form(...),
):
    return templates.TemplateResponse(
        'success.html',
        context={
            'request': request,
        },
    )
