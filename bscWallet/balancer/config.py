import logging
from decimal import Decimal, Context
import os
from typing import List

decimal = Context()
decimal.prec = 18


logger = logging.getLogger(__name__)


ADMIN_ADDRESS = os.getenv('ADMIN_ADDRESS')
ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY')
API_URL = os.getenv('API_URL')
DUST_MULTIPLICATOR = decimal.create_decimal(os.getenv('DUST_MULTIPLICATOR', '2.0'))
DB_URL = os.getenv('DataBaseURL')

MIN_TOKEN_COST = decimal.create_decimal(os.getenv('MIN_TOKEN_COST', '2.0'))
INTERNAL_RABBIT_URL = os.getenv('INTERNAL_RABBIT_URL')

NATIVE_LIMIT = decimal.create_decimal(os.getenv('NATIVE_LIMIT', '0.001'))

ELASTIC_LOG_SERVER = os.getenv('ELASTIC_LOG_SERVER')
ELASTIC_LOGIN = os.getenv('ELASTIC_LOGIN')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_LOG_INDEX = f"{os.getenv('ELASTIC_LOG_INDEX')}-bsc-balancer"
ELASTIC_MSG_INDEX = os.getenv('ELASTIC_MSG_INDEX')


class Tokens:
    TOKEN_COST_USDT = decimal.create_decimal(os.getenv('TOKEN_COST_USDT', '2.0'))
    TOKEN_COST_USDC = decimal.create_decimal(os.getenv('TOKEN_COST_USDC', '2.0'))
    TOKEN_COST_BUSD = decimal.create_decimal(os.getenv('TOKEN_COST_BUSD', '2.0'))
    TOKEN_COST_MATIC = decimal.create_decimal(os.getenv('TOKEN_COST_MATIC', '0.9'))
    TOKEN_COST_LINK = decimal.create_decimal(os.getenv('TOKEN_COST_LINK', '0.1'))
    TOKEN_COST_DNC = decimal.create_decimal(os.getenv('TOKEN_COST_DNC', '0.35'))
    TOKEN_COST_RZM = decimal.create_decimal(os.getenv('TOKEN_COST_RZM', '0.53'))
    TOKEN_COST_ICG = decimal.create_decimal(os.getenv('TOKEN_COST_ICG', '0.001'))
    TOKEN_COST_PONT = decimal.create_decimal(os.getenv('TOKEN_COST_PONT', '0.35'))

    async def get_tokens(self) -> List[str]:
        return [attr.replace('TOKEN_COST_', '') for attr in dir(self) if attr.startswith('TOKEN_COST_')]


tokens = Tokens()
