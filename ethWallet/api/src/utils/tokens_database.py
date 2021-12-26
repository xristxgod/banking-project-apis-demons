from config import TOKENS


class TokenDB:
    """An impromptu database for adding and receiving files"""

    def add_new_token(self, address: str, symbol: str) -> bool:
        """
        Add a new token to the "ALL_TOKENS" file
        :param address: Token smart contract address
        :param symbol: Token name

        :return: If the token was added `True` otherwise `False`
        """
        try:
            with open(TOKENS, "a", encoding="utf-8") as file:
                file.write(f"{symbol}=={address}\n")
            return True
        except RuntimeError:
            return False

    def get_all_tokens(self) -> list:
        """
        Get all files

        :return: Returns all `files` that are in the system
        """
        all_token = []
        with open(TOKENS, "r", encoding="utf-8") as file:
            tokens = file.read().split()
        for token in tokens:
            all_token.append(token.split("==")[0])
        return all_token

    def get_token(self, symbol: str) -> str:
        """
        Get a token
        :param symbol: Token name

        :return:
        """
        with open(TOKENS, "r", encoding="utf-8") as file:
            tokens = file.read().split()
        for token_ in tokens:
            token: list[str, str] = token_.split("==")
            if token[0] == symbol:
                return token[1]

    def is_token(self, address: str) -> bool or str:
        """
        Checks if there is a token in the system
        :param address: Token smart contract address
        """
        with open(TOKENS, "r", encoding="utf-8") as file:
            tokens = file.read().split()
        for token_ in tokens:
            token: list[str, str] = token_.split("==")
            if token[1] == address:
                return token[0]
        else:
            return False
