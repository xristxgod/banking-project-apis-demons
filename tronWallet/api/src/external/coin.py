from dataclasses import dataclass

from .database import Database
from config import Config


@dataclass()
class Token:
    name: str
    symbol: str
    address: str
    decimals: int
    bandwidth: int
    feeLimit: int
    fullEnergy: int
    notEnergy: int


class Coin:
    USDT = Token(
        address="TRvz1r3URQq5otL7ioTbxVUfim9RVSm1hA" if Config.NETWORK.upper() != "MAINNET" \
            else "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        name="Tether USD", symbol="USDT",
        decimals=6, bandwidth=345,
        feeLimit=1000 if Config.NETWORK.upper() != "MAINNET" else 10,
        fullEnergy=14631,
        notEnergy=29631
    )
    USDC = Token(
        address="TK8fX7TpZqedXNYVn6RA24Xcxqox7hbn59" if Config.NETWORK.upper() != "MAINNET" \
            else "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8",
        name="USD Coin", symbol="USDC",
        decimals=6, bandwidth=345,
        feeLimit=1000 if Config.NETWORK.upper() != "MAINNET" else 10,
        fullEnergy=14380 if Config.NETWORK.upper() != "MAINNET" else 14035,
        notEnergy=28827 if Config.NETWORK.upper() != "MAINNET" else 29035
    )


class TokenController:
    @staticmethod
    def get_token(name: str) -> Token:
        result = await Database.get("SELECT * FROM contract WHERE type='tron'")
        token_name = list(filter(lambda x: x["name"].lower() == name.lower(), result))
        if len(token_name) == 0:
            raise Exception("This token is not in the system!!")
        return Coin.__dict__.get(token_name[0]["name"].upper())


__all__ = [
    "TokenController", "Token"
]
