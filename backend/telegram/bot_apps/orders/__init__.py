from . import handlers

HANDLERS = (
    handlers.OrdersHandler,
    handlers.DepositHandler,
    handlers.PreMakeDepositHandler,
    handlers.MakeDepositHandler,
    handlers.CancelDepositHandler,
)
