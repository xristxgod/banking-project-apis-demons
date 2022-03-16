import os
from logging import getLogger
from decimal import Context

from dotenv import load_dotenv

load_dotenv()

decimals = Context()
decimals.prec = 8

# Node network
network = os.getenv("Network").lower()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "src/files")

if network == "mainnet":    __token = "tokensMainNet.json"
elif network == "shasta":   __token = "tokensShastaNet.json"
else:    __token = "tokensNileNet.json"
# File for TRC20 tokens
fileTokens = os.path.join(BASE_DIR, __token)

min_balance = decimals.create_decimal(os.getenv("MinBalanceNative"))

# The node url
node = os.getenv("NodeURL")

AdminWallet = os.getenv("AdminWallet")
AdminFee = os.getenv("AdminFee")
AdminFeeToken = os.getenv("AdminFeeToken", "1.0")
AdminPrivateKey = os.getenv("AdminPrivateKey")

ReportingAddress = os.getenv("ReportingAddress")

db_url = os.getenv("DataBaseURL")

ElasticLogServer = os.getenv("ELASTIC_LOG_SERVER")
ElasticLogin = os.getenv("ELASTIC_LOGIN")
ElasticPassword = os.getenv("ELASTIC_PASSWORD")
ElasticLogIndex = os.getenv('ELASTIC_LOG_INDEX')
ElasticLogIndexEx = f"{os.getenv('ELASTIC_LOG_INDEX_EX')}-api"

NGINX_DOMAIN = os.getenv("NGINX_DOMAIN")

BALANCER_QUEUE = os.getenv("QueueBalancer")
RABBITMQ_URL = os.getenv("RabbitMQURL")
MAX_BALANCER_MESSAGE = int(os.getenv("MaxBalancerMessage"))

API_URL = os.getenv("ApiURL")

logger = getLogger(__name__)