import decimal

from tronpy.tron import TAddress

from core.celery.app import app


@app.task(acks_late=True)
def send_to_central_wallet(address: TAddress, currency: str, **kwargs):
    pass


@app.task(acks_late=True)
def approve_to_central_wallet(address: TAddress, currency: str, **kwargs):
    pass


@app.task(acks_late=True)
def freeze_central_balance(amount: decimal.Decimal, resource: str = 'ENERGY'):
    pass


@app.task(acks_late=True)
def unfreeze_central_balance(amount: decimal.Decimal, resource: str = 'ENERGY'):
    pass
