class Coins:
    BNB = 'bnb'
    token_USDT = 'usdt'
    token_USDC = 'usdc'
    token_BUSD = 'busd'
    token_MATIC = 'matic'
    token_LINK = 'link'
    token_DNC = 'dnc'
    token_RZM = 'rzm'

    @staticmethod
    def is_native(coin: str):
        return coin.lower() == Coins.BNB

    @staticmethod
    def is_token(coin: str):
        return coin.lower() in [
            value for key, value in Coins.__dict__.items() if key.startswith('token_')
        ]
