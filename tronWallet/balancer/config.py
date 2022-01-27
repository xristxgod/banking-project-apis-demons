import os
import logging
from decimal import Context
from dotenv import load_dotenv

load_dotenv()

decimals = Context()
decimals.prec = 18

AdminAddress = os.getenv("ADMIN_WALLET")
AdminPrivateKey = os.getenv("ADMIN_PRIVATE_KEY")

API_URL = os.getenv("API_URL")
DB_URL = os.getenv('DB_URL')

rabbit_url = os.getenv("RABBITMQ_URL")
queue = os.getenv("QUEUE")

minTokenCost = decimals.create_decimal(os.getenv("MIN_TOKEN_COST"))
tokenCostUSDT = decimals.create_decimal(os.getenv('TOKEN_COST_USDT'))
tokenCostUSDC = decimals.create_decimal(os.getenv('TOKEN_COST_USDC'))
tokens = {"usdc": tokenCostUSDC, "usdt": tokenCostUSDT}

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")
if "files" not in os.listdir(ROOT_DIR): os.mkdir(BASE_DIR)
NOT_SEND = os.path.join(BASE_DIR, 'not_send')
if 'not_send' not in os.listdir(BASE_DIR):  os.mkdir(NOT_SEND)

get_network = lambda token: {"usdt": "tron_trc20_usdt", "usdc": "tron_trc20_usdc"}[token]

logger = logging.getLogger(__name__)
