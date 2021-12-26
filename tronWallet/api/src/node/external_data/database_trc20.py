from typing import List, Union

from api.src.utils.tron_typing import ContractAddress, TokenTRC20
from api.src.config import FILE_TRC20_TOKENS

class TRC20DB:
    """Database for the TRC20 token"""
    def __get_info_from_file(self) -> List[TokenTRC20]:
        """Get information from a file"""
        with open(FILE_TRC20_TOKENS, "r", encoding="utf-8") as file:
            tokens = file.read().split()
        return tokens

    def get_all_tokens_only_symbol(self) -> List[TokenTRC20]:
        """
        Get all files in system

        :return: ["Token symbol", ...]
        """
        all_token = []
        tokens = self.__get_info_from_file()
        for tokens in tokens:
            all_token.append(tokens.split("==")[0])
        return all_token

    def add_new_token(self, address: ContractAddress, symbol: TokenTRC20) -> bool:
        """
        Add new token in system
        :param address: Smart Contract (token) address
        :param symbol: Token name

        :return: If the token was added `True` otherwise `False`
        """
        try:
            with open(FILE_TRC20_TOKENS, "a", encoding="utf-8") as file:
                file.write(f"{symbol.upper()}=={address}\n")
            return True
        except Exception:
            raise RuntimeError("Token cannot be added")

    def get_token(self, symbol: TokenTRC20) -> Union[ContractAddress, bool]:
        """
        Get a token
        :param symbol: Token name

        :return: Smart Contract (token) address or False
        """
        tokens = self.__get_info_from_file()
        for token in tokens:
            _token = token.split("==")
            if _token[0] == symbol.upper():
                return _token[1]
        else:
            return False

    def is_token(self, address: ContractAddress) -> Union[TokenTRC20, bool]:
        """
        Checks if there is a token in the system
        :param address: Smart Contract (token) address

        :return: Token name or False
        """
        tokens = self.__get_info_from_file()
        for token in tokens:
            _token = token.split("==")
            if _token[1] == address:
                return _token[0]
        else:
            return False