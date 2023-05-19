from fastapi import Header, Request, HTTPException, status

import settings


async def get_token_header(x_token: str = Header(...)):
    if x_token != settings.ADMIN_HEADER_X_TOKEN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='X-Token header invalid')


async def valid_admin_ips(request: Request):
    if settings.ADMIN_HOST_IPS and request.client.host not in settings.ADMIN_HOST_IPS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Host IP invalid')
