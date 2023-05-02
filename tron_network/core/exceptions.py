
class CurrencyNotFound(Exception):
    def __init__(self, currency: str, *args, **kwargs):
        self.message = f'Currency: {currency} not found'
