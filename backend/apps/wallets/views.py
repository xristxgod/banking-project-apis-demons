from fastapi import APIRouter, status, Form
from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import settings
from apps.wallets.schemas import WalletType

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
    }
    match typ:
        case WalletType.METAMASK:
            template = 'metamask.html'
            context.update({
                'title': 'Metamask',
            })
        case WalletType.TRON_LINK:
            template = 'tronlink.html'
            context.update({
                'title': 'TronLink',
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
    '/connect/{type}',
    response_class=HTMLResponse,
)
async def connect_wallet(request: Request, typ: WalletType):
    pass
