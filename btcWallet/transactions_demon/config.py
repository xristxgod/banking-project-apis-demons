import os
from dotenv import load_dotenv
from logging import getLogger
from decimal import Decimal, Context

decimal = Context()
decimal.prec = 8


load_dotenv()

DB_URL = os.getenv("DataBaseURL")
WALLET_FEE_DEFAULT = os.getenv('WALLET_FEE_DEFAULT', '0xbB10Db443c7eE8c871b073326be9c156d0E1C963')
ADMIN_ADDRESS = os.getenv('ADMIN_WALLET', '188c31hPxLcZekAG9JXZX97mDtshaqYC3z')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, 'files')

if 'files' not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)


NOT_SEND = os.path.join(BASE_DIR, 'not_send')

if 'not_send' not in os.listdir(BASE_DIR):
    os.mkdir(NOT_SEND)


# Errors Recording
ERROR = os.path.join(BASE_DIR, 'error.txt')

if 'error.txt' not in os.listdir(BASE_DIR):
    with open(ERROR, 'w') as file:
        file.write('')


LAST_BLOCK = os.path.join(BASE_DIR, 'last_block.txt')


if 'last_block.txt' not in os.listdir(BASE_DIR):
    with open(LAST_BLOCK, 'w') as file:
        file.write('')


logger = getLogger(__name__)


ELASTIC_LOG_SERVER = os.getenv('ELASTIC_LOG_SERVER', "https://elasticsearch.staging.mango:9200")
ELASTIC_LOGIN = os.getenv('ELASTIC_LOGIN', "elastic")
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', "ru.s0iex3shae%23chiapae8chiiP5ie")
ELASTIC_LOG_INDEX = f"{os.getenv('ELASTIC_LOG_INDEX', 'banking-crypto')}-btc-demon"
ELASTIC_MSG_INDEX = os.getenv('ELASTIC_MSG_INDEX', 'nodes-btc-messages')
