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
