import enum

import settings


class WalletType(enum.StrEnum):
    METAMASK = 'metamask'


class MainnetMetamaskChainId(enum.IntEnum):
    ETH = 1
    BSC = 56


class TestnetMetamaskChainId(enum.IntEnum):
    ETH = 11155111      # Spela
    BSC = 97


MetamaskChainId = TestnetMetamaskChainId if settings.TESTNET else MainnetMetamaskChainId
