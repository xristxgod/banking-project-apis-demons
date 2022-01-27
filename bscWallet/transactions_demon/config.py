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
NODE_URL = os.environ.get("NodeURL", 'https://data-seed-prebsc-2-s3.binance.org:8545/')


ADMIN_ADDRESS = os.getenv('ADMIN_ADDRESS', '0xbB10Db443c7eE8c871b073326be9c156d0E1C963')
SEND_TO_MAIN_WALLET_LIMIT = decimal.create_decimal(os.getenv('SEND_TO_MAIN_WALLET_LIMIT', '0.0001'))
