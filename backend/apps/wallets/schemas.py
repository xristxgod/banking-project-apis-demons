import enum


class WalletType(enum.StrEnum):
    METAMASK = 'metamask'
    TRON_LINK = 'tron_link'


# class MainnetMetamaskChainId(enum.IntEnum):
#     ETH = 1
#     BSC = 56
#
#     @property
#     def to_list(self):
#         return [
#             self.ETH.value,
#             self.BSC.value,
#         ]
#
#
# class TestnetMetamaskChainId(MainnetMetamaskChainId):
#     ETH = 11155111      # Spela
#     BSC = 97
