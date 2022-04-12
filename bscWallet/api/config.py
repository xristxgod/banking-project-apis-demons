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


ADMIN_ADDRESS = os.getenv('ADMIN_ADDRESS').lower()
ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY')
ADMIN_FEE = decimal.create_decimal(os.getenv('ADMIN_FEE', '0.05'))

MIN_MAIN_BALANCE = decimal.create_decimal(os.getenv('MIN_MAIN_BALANCE', '0.1'))

ELASTIC_LOG_SERVER = os.getenv('ELASTIC_LOG_SERVER')
ELASTIC_LOGIN = os.getenv('ELASTIC_LOGIN')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_LOG_INDEX = f"{os.getenv('ELASTIC_LOG_INDEX')}-bsc-api"
ELASTIC_MSG_INDEX = os.getenv('ELASTIC_MSG_INDEX')

NODE_URL = os.environ.get("NodeURL")

NGINX_DOMAIN = os.environ.get("NGINX_DOMAIN")

INTERNAL_RABBIT_URL = os.getenv('INTERNAL_RABBIT_URL')
API_URL = os.getenv('API_URL')
