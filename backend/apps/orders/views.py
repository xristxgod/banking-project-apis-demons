from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import settings
from apps.telegram.models import User
from apps.wallets.models import Wallet

ORDER_DIR = settings.APPS_DIR / 'orders'

router = APIRouter()
templates = Jinja2Templates(directory=ORDER_DIR / 'templates')


@router.get(
    '/approve/{typ}/{currency}',
    response_model=HTMLResponse,
)
async def approve_transaction(request: Request, typ, currency):
    # TODO add user to request
    # user: User = request.user
    user = await User.get(pk=1)
    wallet = await Wallet.get(user=user, type=typ)

    return templates.TemplateResponse(
        'approve_transaction.html',
        context={
            'request': request,
            'wallet': wallet,
        },
    )


@router.post(
    '/success/{typ}/{currency}',
    response_model=HTMLResponse,
)
async def success(request: Request):
    pass
