import os
from logging import getLogger
from decimal import Context, Decimal


decimal = Context()
decimal.prec = 18

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")

if "files" not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")
if "files" not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)

# Logger
logger = getLogger(__name__)


ADMIN_ADDRESS = os.getenv('ADMIN_ADDRESS', '0xbB10Db443c7eE8c871b073326be9c156d0E1C963').lower()
ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY', '0x8056ff9c55ce2cd624b9b531173c5c1583b3e78c777f2049c08ff61e49b2f3be')
ADMIN_FEE = decimal.create_decimal(os.getenv('ADMIN_FEE', '0.05'))

MIN_MAIN_BALANCE = decimal.create_decimal(os.getenv('MIN_MAIN_BALANCE', '0.1'))

ELASTIC_LOG_SERVER = os.getenv('ELASTIC_LOG_SERVER', "https://elasticsearch.staging.mango:9200")
ELASTIC_LOGIN = os.getenv('ELASTIC_LOGIN', "elastic")
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', "ru.s0iex3shae%23chiapae8chiiP5ie")
ELASTIC_LOG_INDEX = f"{os.getenv('ELASTIC_LOG_INDEX', 'banking-crypto')}-bsc-api"
ELASTIC_MSG_INDEX = os.getenv('ELASTIC_MSG_INDEX', 'nodes-bsc-messages')

NODE_URL = os.environ.get("NodeURL", 'https://data-seed-prebsc-2-s3.binance.org:8545/')

NGINX_DOMAIN = os.environ.get("NGINX_DOMAIN", 'http://api.bsc.staging.mangobanking.com')

INTERNAL_RABBIT_URL = os.getenv('INTERNAL_RABBIT_URL', "amqp://root:password@127.0.0.1:5672/")
