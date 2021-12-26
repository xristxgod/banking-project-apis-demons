import json
from typing import List

from api.src.utils.tron_typing import TokenTRC10
from api.src.config import FILE_TRC10_TOKENS, FILE_TRC10_SYMBOLS

class TRC10DB:

    def get_all_tokens(self) -> List:
        """
        Get all token in system
        :return: [{"name": "Token name", "id": "Token ID", "symbol": "Token symbol"}, ...]
        """
        with open(FILE_TRC10_TOKENS, "r", encoding="utf-8") as file:
            tokens = json.loads(file.read())
        return tokens

    def get_all_tokens_only_symbol(self) -> List:
        """
        Get only files symbols
        :return: ["Token symbol", ...]
        """
        with open(FILE_TRC10_SYMBOLS, "r", encoding="utf-8") as file:
            tokens = json.loads(file.read())
        return tokens

    def get_token(self, token: TokenTRC10) -> int:
        """
        Get id token by name or symbol
        :param token: Token symbol or name
        :return: ID token
        """
        with open(FILE_TRC10_TOKENS, 'r', encoding="utf-8") as file:
            tokens = json.loads(file.read())

        for token_ in tokens:
            if token in [token_["id"], token_["name"], token_["symbol"]]:
                return int(token_["id"])
        else:
            return 0