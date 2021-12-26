import os
from dotenv import load_dotenv
from logging import getLogger


load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(ROOT_DIR, 'files')

if 'files' not in os.listdir(ROOT_DIR):
    os.mkdir(BASE_DIR)


NOT_SEND = os.path.join(BASE_DIR, 'not_send')

if 'not_send' not in os.listdir(BASE_DIR):
    os.mkdir(NOT_SEND)


# Errors Recording
ERROR = os.path.join(BASE_DIR, 'error.txt')

if 'error.txt' not in os.listdir(BASE_DIR):
    with open(ERROR, 'w') as file:
        file.write('')


LAST_BLOCK = os.path.join(BASE_DIR, 'last_block.txt')


if 'last_block.txt' not in os.listdir(BASE_DIR):
    with open(LAST_BLOCK, 'w') as file:
        file.write('')


logger = getLogger(__name__)
