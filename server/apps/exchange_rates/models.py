import sqlalchemy as fields
from sqlalchemy import Column

from core.common import models


class CryptoCurrency(models.Model):
    __tablename__ = 'exchange_rates__crypto_currency'

    name = Column(fields.String(length=255), nullable=False)
    coin_gecko_id = Column(fields.String(length=255), nullable=True, default='')

    def __repr__(self):
        return f'Currency: {self.name}'


class FiatCurrency(models.Model):
    __tablename__ = 'exchange_rates__fiat_currency'

    name = Column(fields.String(length=255), nullable=False)

    def __repr__(self):
        return f'Currency: {self.name}'
