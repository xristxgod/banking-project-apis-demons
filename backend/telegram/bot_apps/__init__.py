from . import start
from . import orders

ALL_HANDLERS = (
        start.HANDLERS +
        orders.HANDLERS
)
