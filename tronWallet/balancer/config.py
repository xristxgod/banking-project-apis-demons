import os
import logging
from decimal import Context
from dotenv import load_dotenv

load_dotenv()

decimals = Context()
decimals.prec = 18

AdminAddress = os.getenv("AdminWallet")
ReportingAddress = os.getenv("ReportingAddress")
AdminPrivateKey = os.getenv("AdminPrivateKey")

API_URL = os.getenv("ApiURL")
DB_URL = os.getenv('DataBaseURL')

rabbit_url = os.getenv("RabbitMQURL")
queue = os.getenv("QueueBalancer")

minTokenCost = decimals.create_decimal(os.getenv("MinTokenCost"))
tokenCostUSDT = decimals.create_decimal(os.getenv('TokenCostUSDT'))
tokenCostUSDC = decimals.create_decimal(os.getenv('TokenCostUSDC'))
tokens = {"usdc": tokenCostUSDC, "usdt": tokenCostUSDT}

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")
if "files" not in os.listdir(ROOT_DIR): os.mkdir(BASE_DIR)
NOT_SEND = os.path.join(BASE_DIR, 'not_send')
if 'not_send' not in os.listdir(BASE_DIR):  os.mkdir(NOT_SEND)

get_network = lambda token: {"usdt": "tron_trc20_usdt", "usdc": "tron_trc20_usdc"}[token]

ElasticLogServer = os.getenv("ELASTIC_LOG_SERVER")
ElasticLogin = os.getenv("ELASTIC_LOGIN")
ElasticPassword = os.getenv("ELASTIC_PASSWORD") if os.getenv("Network") == "mainnet" else 'no_pass'
ElasticLogIndex = os.getenv('ELASTIC_LOG_INDEX')
ElasticLogIndexEx = f"{os.getenv('ELASTIC_LOG_INDEX_EX')}-balancer"

logger = logging.getLogger(__name__)