from . import orders
from . import start

ALL_HANDLERS = (
    start.HANDLERS +
    orders.HANDLERS
)
