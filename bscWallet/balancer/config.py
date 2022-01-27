import logging
from decimal import Decimal, Context
import os
from typing import List

decimal = Context()
decimal.prec = 18


logger = logging.getLogger(__name__)


ADMIN_ADDRESS = os.getenv('ADMIN_ADDRESS', '0x6fAE511E40F582C50cD487a4999dc857a7bc3527')
ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY', '41f588612616cf8fd7150c13e6564650f57dad5b98f67ce839e1299cffc0a69f')
API_URL = os.getenv('API_URL', 'http://127.0.0.1:8000')
DUST_MULTIPLICATOR = decimal.create_decimal(os.getenv('DUST_MULTIPLICATOR', '2.0'))
DB_URL = os.getenv('DataBaseURL', 'postgresql://mango:mango@172.31.3.130:35432/mango_crypto_master')

MIN_TOKEN_COST = decimal.create_decimal(os.getenv('MIN_TOKEN_COST', '2.0'))
INTERNAL_RABBIT_URL = os.getenv('INTERNAL_RABBIT_URL', "amqp://root:password@127.0.0.1:5672/")

NATIVE_LIMIT = decimal.create_decimal(os.getenv('NATIVE_LIMIT', '0.0012'))


class Tokens:
    TOKEN_COST_USDT = decimal.create_decimal(os.getenv('TOKEN_COST_USDT', '2.0'))
    TOKEN_COST_USDC = decimal.create_decimal(os.getenv('TOKEN_COST_USDC', '2.0'))
    TOKEN_COST_BUSD = decimal.create_decimal(os.getenv('TOKEN_COST_BUSD', '2.0'))
    TOKEN_COST_MATIC = decimal.create_decimal(os.getenv('TOKEN_COST_MATIC', '0.9'))
    TOKEN_COST_LINK = decimal.create_decimal(os.getenv('TOKEN_COST_LINK', '0.1'))
    TOKEN_COST_DNC = decimal.create_decimal(os.getenv('TOKEN_COST_DNC', '0.35'))
    TOKEN_COST_RZM = decimal.create_decimal(os.getenv('TOKEN_COST_RZM', '0.53'))

    async def get_tokens(self) -> List[str]:
        return [attr.replace('TOKEN_COST_', '') for attr in dir(self) if attr.startswith('TOKEN_COST_')]


tokens = Tokens()
