import json
from typing import List, Dict

from asyncpg import Connection, connect, Record
from aiofiles import open as async_open

from src.utils.types import TokenTRC20
from src.utils.es_send import send_exception_to_kibana
from config import db_url, fileTokens, network


class TokenDB:

    @property
    async def __get_from_database(self) -> List:
        """Get information from a database"""
        __connection = None
        try:
            __connection: Connection = await connect(db_url)
            result: List[Record] = await __connection.fetch("""SELECT *  FROM contract WHERE type='tron'""")
            return [x for x in result]
        except Exception as error:
            await send_exception_to_kibana(error, "GET FROM DB ERROR")
            return []
        finally:
            if __connection is not None:
                await __connection.close()

    @staticmethod
    async def __get_from_json_file(symbol: TokenTRC20):
        """Get information from a file"""
        try:
            async with async_open(fileTokens, "r", encoding="utf-8") as file:
                tokens = json.loads(await file.read())
            for token in tokens:
                if token["symbol"] == symbol:
                    return token
        except Exception as error:
            await send_exception_to_kibana(error, "GET FROM FILE ERROR")

    async def get_token(self, token: TokenTRC20) -> Dict:
        """
        Get a tokens
        :param token: Contact address || Symbol || Name
        """
        tokens_in_system = await self.__get_from_database
        for token_in_system in tokens_in_system:
            if token.upper() in [
                token_in_system["name"].upper(),
                token_in_system["symbol"].upper(),
                token_in_system["address"].upper()
            ]:
                info = await TokenDB.__get_from_json_file(symbol=token_in_system["symbol"].upper())
                return {
                    "name": token_in_system["name"],
                    "symbol": token_in_system["symbol"],
                    "address": token_in_system["address"] if network == "mainnet" else info["address"],
                    "decimal": token_in_system["decimals"] if network == "mainnet" else info["decimals"],
                    "bandwidth": info["bandwidth"],
                    "feeLimit": info["feeLimit"],
                    "isBalanceNotNullEnergy": info["isBalanceNotNullEnergy"],
                    "isBalanceNullEnergy": info["isBalanceNullEnergy"]
                }
        else:
            raise Exception("This token is not in the system!!")

    async def get_test_token(self, token: TokenTRC20) -> Dict:
        async with async_open(fileTokens, "r", encoding="utf-8") as file:
            tokens_in_system = json.loads(await file.read())
        for token_in_system in tokens_in_system:
            if token.upper() in [
                token_in_system["name"].upper(),
                token_in_system["symbol"].upper(),
                token_in_system["address"].upper()
            ]:
                info = await TokenDB.__get_from_json_file(symbol=token_in_system["symbol"].upper())
                return {
                    "name": token_in_system["name"],
                    "symbol": token_in_system["symbol"],
                    "address": token_in_system["address"] if network == "mainnet" else info["address"],
                    "decimal": token_in_system["decimals"] if network == "mainnet" else info["decimals"],
                    "bandwidth": info["bandwidth"],
                    "feeLimit": info["feeLimit"],
                    "isBalanceNotNullEnergy": info["isBalanceNotNullEnergy"],
                    "isBalanceNullEnergy": info["isBalanceNullEnergy"]
                }
        else:
            raise Exception("This token is not in the system!!")

token_db = TokenDB()
