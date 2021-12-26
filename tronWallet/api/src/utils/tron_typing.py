from typing import Union

# Secret word for quick access to your account
TronAccountPassphrase = str
# Public address of the Tron wallet (Base58 address) | Example: `TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb`
TronAccountAddress = str
# Address of the smart contract (token) (Base58 address) | Example: `THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF` - ETH Token
ContractAddress = str
# Token Name or Symbol | Example: Name = `APENFT`, Symbol = `NFT`
TokenTRC20 = Union[str, ContractAddress]
# Token Name or ID or Symbol | Example: ID = `1003533`, Name = `PlayAndLike`, Symbol = `PAL`
TokenTRC10 = Union[int, str]
# Tokens
Tokens = Union[TokenTRC10, TokenTRC20]
# Tron wallet private key | Example: `61c66z4f57838e1258c7e627873c56eb35ad3zxczx21b1b931dcf165df738b3c`
TronAccountPrivateKey = Union[str, bytes]
# Tron wallet public key | Example:
TronAccountPublicKey = Union[str, bytes]
# Transaction hash | Example: `7bfe6954fbf43630e47aad1280be10942b29e72fa890cd0b2a35d7659a3ee40a`
TransactionHash = str
# The amount in TRX
Amount = Union[str, int, float]
# The amount in Token TRC20
AmountTRC20 = Union[Amount]
# The amount in Token TRC10
AmountTRC10 = Union[Amount]
# The amount in tokens
AmountToken = Union[AmountTRC10, AmountTRC20]
