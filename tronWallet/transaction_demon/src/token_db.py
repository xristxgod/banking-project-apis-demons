import json
from typing import Dict

import psycopg2
import psycopg2.extras
from aiofiles import open as async_open

from src.utils import ContractAddress
from config import DataBaseUrl, fileTokens, network

async def __get_db() -> Dict:
    """Get information from a file"""
    connection = psycopg2.connect(DataBaseUrl)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""SELECT *  FROM contract WHERE type='tron'""")
    data: Dict = cursor.fetchall()
    connection.close()
    return data

async def __get_file() -> Dict:
    async with async_open(fileTokens, "r", encoding="utf-8") as file:
        tokens: dict = json.loads(await file.read())
    return tokens

async def get_asset_trc20(address: ContractAddress) -> Dict:
    if network == "shasta" or network == "nile":
        tokens = await __get_file()
    else:
        tokens = await __get_db()
    for token in tokens:
        if address in [token["name"], token["symbol"], token["address"]]:
            return token

