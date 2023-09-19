import fastapi
from sqladmin import Admin

from config.database import engine, extra_engines

app = fastapi.FastAPI(
    title='Merchant',
)

admin = Admin(
    app=app,
    engine=engine,
    title='Merchant Admin',
    templates_dir='./templates',
    authentication_backend=None,    # TODO
)

admin_exchange_rate = Admin(
    app=app,
    engine=extra_engines['exchange-rate'],
    title='Exchange Rate',
    templates_dir='./templates',
    authentication_backend=None,    # TODO
)
