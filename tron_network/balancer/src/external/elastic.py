import os
import sys
import traceback
from datetime import datetime
from dataclasses import dataclass, field

import aiohttp

from config import Config, logger


@dataclass()
class SendData:
    message: str
    code: int = field(default=None)
    trace: str = field(default=None)
    fileName: str = field(default=None)
    line: int = field(default=None)
    isMessage: bool = field(default=False)


class ElasticCore:
    HEADERS = {
        "Content-Type": "application/json"
    }
    AUTH = aiohttp.BasicAuth(Config.ELASTIC_LOGIN, Config.ELASTIC_PASSWORD)

    @staticmethod
    async def send(data: SendData) -> bool:
        index = Config.ELASTIC_LOG_INDEX_EX if data.isMessage else Config.ELASTIC_LOG_INDEX
        url = f'{Config.ELASTIC_LOG_SERVER}/{index}/_doc'
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiohttp.ClientSession(
            headers=ElasticCore.HEADERS,
            auth=ElasticCore.AUTH
        ) as session:
            async with session.post(url, json={
                'Time': time,
                'Status': data.code,
                'Message': data.message,
                'File': data.fileName,
                'Line': data.line,
                'Trace': data.trace,
                '@timestamp': datetime.now().isoformat()
            }) as response:
                status = response.ok
        if data.code is None:
            logger.error(data.message)
        else:
            logger.error(
                f'EXCEPTION {time} || '
                f'Status: {data.code} || '
                f'Trace: {data.trace} || '
                f'File: {data.fileName} || '
                f'Line: {data.line} || '
                f'Sent to kibana: {status}'
            )
        return status


class ElasticController:
    CORE = ElasticCore

    @staticmethod
    async def send_message(message: str) -> bool:
        return await ElasticController.CORE.send(data=SendData(
            message=message, isMessage=True
        ))

    @staticmethod
    async def send_error(message: str, code: int) -> bool:
        return await ElasticController.CORE.send(data=SendData(
            message=message, code=code
        ))

    @staticmethod
    async def send_exception(ex: Exception, message: str = None) -> bool:
        try:
            code = ex.args[0]
        except:
            code = "-1"
        ex_type, ex_obj, ex_trace = sys.exc_info()
        file_name = os.path.split(ex_trace.tb_frame.f_code.co_filename)[1]
        trace = traceback.format_exc()
        line = ex_trace.tb_lineno
        return await ElasticController.CORE.send(data=SendData(
            message=str(ex) if message is None else f'{message} || {ex}',
            code=code, fileName=file_name, trace=trace, line=line
        ))


__all__ = [
    "ElasticController", "SendData"
]