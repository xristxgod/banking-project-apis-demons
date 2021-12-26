from typing import Union

# Public address of the Tron wallet (Base58 address) | Example: `TJmV58h1StTogUuVUoogtPoE5i3YPCS7yb`
TronAccountAddress = str
# Address of the smart contract (token) (Base58 address) | Example: `THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF` - ETH Token
ContractAddress = str
# Token Name or Symbol | Example: Name = `APENFT`, Symbol = `NFT`
TokenTRC20 = str
# Token Name or ID or Symbol | Example: ID = `1003533`, Name = `PlayAndLike`, Symbol = `PAL`
TokenTRC10 = Union[int, str]
# Tron wallet private key | Example: `61c66z4f57838e1258c7e627873c56eb35ad3zxczx21b1b931dcf165df738b3c`
TronAccountPrivateKey = Union[str, bytes]
# Transaction hash | Example: `7bfe6954fbf43630e47aad1280be10942b29e72fa890cd0b2a35d7659a3ee40a`
TransactionHash = str
# The amount in TRX
Amount = Union[int, float]
# The amount in Token TRC20
AmountTRC20 = Union[int, float]

TransactionType = Union["TransferAssetContract", "TransferContract", "TriggerSmartContract"]