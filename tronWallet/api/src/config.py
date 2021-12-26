import os
from logging import getLogger
from dotenv import load_dotenv

from tronpy.providers import HTTPProvider

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")
if "files" not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)

# File for TRC10 tokens
fileTRC10tokens = "TRC10tokens.json"
FILE_TRC10_TOKENS = os.path.join(BASE_DIR, fileTRC10tokens)

# File for TRC10 tokens symbols
fileTRC10symbols = "TRC10symbols.json"
FILE_TRC10_SYMBOLS = os.path.join(BASE_DIR, fileTRC10symbols)

# File for TRC20 (Smart Contract) tokens
fileTRC20tokens = "TRC20tokens.txt"
FILE_TRC20_TOKENS = os.path.join(BASE_DIR, fileTRC20tokens)

network = os.getenv("NETWORK")

if network.title() == "Mainnet":
    __full_node, __solidity_node, __event_server = (HTTPProvider(endpoint_uri="https://api.trongrid.io"),) * 3
elif network.title() == "Shasta":
    __full_node, __solidity_node, __event_server = (HTTPProvider(endpoint_uri="https://api.shasta.trongrid.io"), ) * 3
elif network.title() == "Nile":
    __full_node, __solidity_node, __event_server = (HTTPProvider(endpoint_uri="https://nile.trongrid.io"), ) * 3
else:
    raise Exception("Specify the correct network")

if network.title() in ["Shasta", "Nile"]:
    TronGridApiKey = None
else:
    if str(os.getenv("MultiKeys")).lower() == "true":
        TronGridApiKey = HTTPProvider(api_key=os.getenv("listTronGridAPIKEY").split())
    else:
        TronGridApiKey = HTTPProvider(api_key=os.getenv("TronGridAPIKEY"))

tr = os.getenv("TronGridAPIKEY")

config = dict(
    full_node=__full_node,
    solidity_node=__solidity_node,
    event_server=__event_server
)

logger = getLogger(__name__)