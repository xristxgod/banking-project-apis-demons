import os
import sys
import traceback
import aiohttp
from datetime import datetime
from config import ElasticLogin, ElasticPassword, ElasticLogIndex, ElasticLogServer, logger, ElasticLogIndexEx

async def send_msg_to_kibana(*, msg: str, code=None, tb=None, file_name=None, line=None, url_log=None) -> bool:
    if url_log is None:
        url = f"{ElasticLogServer}/{ElasticLogIndex}/_doc"
    else:
        url = f"{ElasticLogServer}/{url_log}/_doc"
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiohttp.ClientSession(
        headers={'Content-Type': 'application/json'},
        auth=aiohttp.BasicAuth(ElasticLogin, ElasticPassword)
    ) as session:
        async with session.post(url, json={
            "Time": time,
            "Status": code,
            "Message": msg,
            "File": file_name,
            "Line": line,
            "Trace": tb
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

async def send_exception_to_kibana(error: Exception, msg: str = None) -> bool:
    code = error.args[0]
    exc_type, exc_obj, exc_tb = sys.exc_info()
    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    tb = traceback.format_exc()
    line = exc_tb.tb_lineno
    return await send_msg_to_kibana(
        msg=str(error) if msg is None else f"{msg} || {str(error)}",
        code=code, file_name=file_name, tb=tb, line=line, url_log=ElasticLogIndexEx
    )