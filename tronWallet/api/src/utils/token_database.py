import json
from typing import List, Dict

import psycopg2
import psycopg2.extras

from src.utils.types import TokenTRC20
from config import db_url, fileTokens, network

class TokenDB:

    @property
    def __get_file(self) -> Dict:
        """Get information from a file"""
        connection = psycopg2.connect(db_url)
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""SELECT *  FROM contract WHERE type='tron'""")
        data = cursor.fetchall()
        connection.close()
        return data

    def __get_res(self, symbol: TokenTRC20):
        with open(fileTokens, "r", encoding="utf-8") as file:
            tokens = json.loads(file.read())
        for token in tokens:
            if token["symbol"] == symbol:
                return token

    def get_all_tokens(self) -> List[TokenTRC20]:
        """Get all files in system"""
        all_tokens = []
        tokens_in_system = self.__get_file
        for token_in_system in tokens_in_system:
            all_tokens.append(token_in_system["symbol"])
        return all_tokens

    def get_token(self, token: TokenTRC20) -> Dict:
        """
        Get a tokens
        :param token: Contact address || Symbol || Name
        """
        tokens_in_system = self.__get_file
        for token_in_system in tokens_in_system:
            if token.upper() in [token_in_system["name"], token_in_system["symbol"].upper(), token_in_system["address"]]:
                info = self.__get_res(token_in_system["symbol"].upper())
                if network == "mainnet" or network == "nile":
                    return {
                        "name": token_in_system["name"],
                        "symbol": token_in_system["symbol"],
                        "address": token_in_system["address"],
                        "decimal": token_in_system["decimals"] if network != "nile" else token_in_system["decimal"],
                        "bandwidth": info["bandwidth"],
                        "feeLimit": info["feeLimit"],
                        "isBalanceNotNullEnergy": info["isBalanceNotNullEnergy"],
                        "isBalanceNullEnergy": info["isBalanceNullEnergy"]
                    }
                else:
                    return info
        else:
            raise Exception("This token is not in the system!!")

token_db = TokenDB()