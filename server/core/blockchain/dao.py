from core.common.dao import BaseDAO
from core.blockchain import models


class NetworkDAO(BaseDAO):
    model = models.Network


class StableCoinDAO(BaseDAO):
    model = models.StableCoin


class OrderProvider(BaseDAO):
    model = models.OrderProvider
