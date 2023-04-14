import os
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent.parent

NODE_URL = os.getenv('NODE_URL')
