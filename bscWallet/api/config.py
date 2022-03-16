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


ADMIN_ADDRESS = os.getenv('ADMIN_ADDRESS', '').lower()
ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY', '')
ADMIN_FEE = decimal.create_decimal(os.getenv('ADMIN_FEE', '0.05'))
