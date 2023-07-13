from . import handlers

HANDLERS = (
    handlers.OrderHandler,
    handlers.ViewDepositHandler,
    handlers.ViewWithdrawHandler,
    handlers.CreateDepositHandler,
    handlers.CreateDepositByTextHandler,
    handlers.RepeatDepositHandler,
    handlers.CancelPaymentHandler,
)
