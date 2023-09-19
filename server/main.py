import fastapi
from sqladmin import Admin

from config.database import engine, extra_engines
from config.auth import get_authentication_backend

from core.blockchain import admin as blockchain_admin

app = fastapi.FastAPI(
    title='Merchant',
)

admin = Admin(
    app=app,
    engine=engine,
    title='Merchant Admin',
    templates_dir='./templates',
    authentication_backend=get_authentication_backend(backend_name='admin'),
)

admin_exchange_rate = Admin(
    app=app,
    engine=extra_engines['exchange-rate'],
    title='Exchange Rate',
    templates_dir='./templates',
    authentication_backend=get_authentication_backend(backend_name='admin-exchange-rate'),
    base_url='/admin-exchange-rate'
)

admin.add_view(blockchain_admin.NetworkAdmin)
admin.add_view(blockchain_admin.StableCoinAdmin)
admin.add_view(blockchain_admin.OrderProviderAdmin)
