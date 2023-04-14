import asyncio
from typing import Coroutine

from tronpy.tron import TAddress

from src import UserMiddleware
from .app import app
from .services import transaction_worker


def run(coroutine: Coroutine):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coroutine)


@app.task(acks_late=True)
def send_transaction(user: UserMiddleware, token: str):
    run(transaction_worker(user=user, token=token))
