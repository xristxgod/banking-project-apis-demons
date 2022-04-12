import os
from dotenv import load_dotenv
from logging import getLogger
from decimal import Decimal, Context


decimal = Context()
decimal.prec = 18

load_dotenv()


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")

if "files" not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)


NOT_SEND = os.path.join(BASE_DIR, 'not_send')

if 'not_send' not in os.listdir(BASE_DIR):
    os.mkdir(NOT_SEND)

# Errors Recording
ERROR = os.path.join(BASE_DIR, "error.txt")

LAST_BLOCK = os.path.join(BASE_DIR, "last_block.txt")

if "last_block.txt" not in os.listdir(BASE_DIR):
    with open(LAST_BLOCK, "w") as file:
        file.write("")

logger = getLogger(__name__)
NODE_URL = os.environ.get("NodeURL")


ADMIN_ADDRESS = os.getenv('ADMIN_ADDRESS')
SEND_TO_MAIN_WALLET_LIMIT = decimal.create_decimal(os.getenv('SEND_TO_MAIN_WALLET_LIMIT', '0.0001'))
DB_URL = os.getenv('DataBaseURL')
WALLET_FEE_DEFAULT = os.getenv('WALLET_FEE_DEFAULT')

ELASTIC_LOG_SERVER = os.getenv('ELASTIC_LOG_SERVER')
ELASTIC_LOGIN = os.getenv('ELASTIC_LOGIN')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_LOG_INDEX = f"{os.getenv('ELASTIC_LOG_INDEX')}-bsc-demon"
ELASTIC_MSG_INDEX = os.getenv('ELASTIC_MSG_INDEX')
