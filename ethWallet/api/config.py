import os
from logging import getLogger

ALL_TOKENS = "allToken.txt"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, "files")
if "files" not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)
TOKENS = os.path.join(BASE_DIR, ALL_TOKENS)

# Logger
logger = getLogger(__name__)

