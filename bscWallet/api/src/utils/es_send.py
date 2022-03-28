import os
import sys
import traceback
import aiohttp
from datetime import datetime
from config import (
    ELASTIC_LOGIN, ELASTIC_PASSWORD,
    ELASTIC_LOG_SERVER, ELASTIC_LOG_INDEX,
    logger, ELASTIC_MSG_INDEX
)


async def send_msg_to_kibana(msg: str):
    return await __send_msg_to_kibana(msg=msg, is_msg=True)


async def send_error_to_kibana(*, msg: str, code: int):
    return await __send_msg_to_kibana(msg=msg, code=code)


async def send_exception_to_kibana(e: Exception, msg: str = None):
    try:
        code = e.args[0]
    except:
        code = '-1'
    exc_type, exc_obj, exc_tb = sys.exc_info()
    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    tb = traceback.format_exc()
    line = exc_tb.tb_lineno
    return await __send_msg_to_kibana(
        msg=str(e) if msg is None else f'{msg} || {str(e)}',
        code=code, file_name=file_name, tb=tb, line=line
    )


async def __send_msg_to_kibana(
    *, msg: str, code=None, tb=None, file_name=None, line=None, is_msg=False
):
    index = ELASTIC_MSG_INDEX if is_msg else ELASTIC_LOG_INDEX
    url = f'{ELASTIC_LOG_SERVER}/{index}/_doc'
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiohttp.ClientSession(
            headers={'Content-Type': 'application/json'},
            auth=aiohttp.BasicAuth(ELASTIC_LOGIN, ELASTIC_PASSWORD)
    ) as session:
        async with session.post(url, json={
            'Time': time,
            'Status': code,
            'Message': msg,
            'File': file_name,
            'Line': line,
            'Trace': tb,
            '@timestamp': datetime.now().isoformat()
        }) as resp:
            in_kibana = resp.ok
    if code is None:
        logger.error(msg)
    else:
        logger.error(
            f'EXCEPTION {time} || '
            f'Status: {code} || '
            f'Trace: {tb} || '
            f'File: {file_name} || '
            f'Line: {line} || '
            f'Sent to kibana: {in_kibana}'
        )
    return in_kibana
