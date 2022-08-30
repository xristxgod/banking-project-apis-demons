import asyncio

from tronpy.tron import TAddress

from src import UserMiddleware
from .app import app
from .services import transaction_worker


def run_sync(f):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(f)


@app.task(acks_late=True)
def send_transaction(user: UserMiddleware, token: str):
    run_sync(transaction_worker(user=user, token=token))