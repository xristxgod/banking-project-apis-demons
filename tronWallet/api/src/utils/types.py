from typing import Union

# Public address of the Tron wallet (Base58 address) | Example: `TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb`
TronAccountAddress = str
# Tron wallet private key | Example: `61c66z4f57838e1258c7e627873c56eb35ad3zxczx21b1b931dcf165df738b3c`
TronAccountPrivateKey = Union[str, bytes]
# Tron wallet public key | Example:
TronAccountPublicKey = Union[str, bytes]

# Address of the smart contract (tokens) (Base58 address) | Example: `THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF` - ETH Token
ContractAddress = str
# Token Name or Symbol or Address | Example: Name = `Tether USD`, Symbol = `USDT`, Address = `TR7NHqjeKQ...Lj6t`
TokenTRC20 = Union[str, ContractAddress]

# Transaction hash | Example: `7bfe6954fbf43630e47aad1280be10942b29e72fa890cd0b2a35d7659a3ee40a`
TransactionHash = str

# The amount in TRX
Amount = Union[str, int, float]
# The amount in Token TRC20
AmountTRC20 = Union[Amount]

class Coins:
    TRX = "trx"
    token_USDT = 'usdt'
    token_USDC = 'usdc'

    @staticmethod
    def is_native(coin: str):
        return coin.lower() == Coins.TRX

    @staticmethod
    def is_token(coin: str):
        return coin.lower() in [value for key, value in Coins.__dict__.items() if key.startswith('token_')]
