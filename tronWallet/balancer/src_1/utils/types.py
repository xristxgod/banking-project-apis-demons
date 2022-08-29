from typing import Union


# Public address of the Tron wallet (Base58 address) | Example: `TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb`
TronAccountAddress = str
# Tron wallet private key | Example: `61c66z4f57838e1258c7e627873c56eb35ad3zxczx21b1b931dcf165df738b3c`
TronAccountPrivateKey = Union[str, bytes]
# Address of the smart contract (tokens) (Base58 address) | Example: `THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF` - ETH Token
ContractAddress = str
# Token Name or Symbol | Example: Name = `APENFT`, Symbol = `NFT`
TokenTRC20 = Union[str, ContractAddress]