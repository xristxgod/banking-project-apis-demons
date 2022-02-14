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

# The node url
node = os.getenv("NodeURL")

AdminWallet = os.getenv("AdminWallet")
AdminFee = os.getenv("AdminFee")
AdminPrivateKey = os.getenv("AdminPrivateKey")

ReportingAddress = os.getenv("ReportingAddress")

db_url = os.getenv("DataBaseURL")

logger = getLogger(__name__)