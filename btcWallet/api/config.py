from decimal import Context
from logging import getLogger


logger = getLogger(__name__)

decimal = Context()
decimal.prec = 8
