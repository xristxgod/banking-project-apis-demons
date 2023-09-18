import sqlalchemy as fields
from sqlalchemy import Column

from core.common import models


class CryptoCurrency(models.Model):
    __tablename__ = 'exchange_rates__crypto_currency'

    name = Column(fields.String(length=255), nullable=False)
    coin_gecko_id = Column(fields.String(length=255), nullable=True, default='')
    default_price = Column(fields.Numeric(25, 3), default=0.0)

    def __repr__(self):
        return f'Currency: {self.name}'


class FiatCurrency(models.Model):
    __tablename__ = 'exchange_rates__fiat_currency'

    name = Column(fields.String(length=255), nullable=False)
    exchange_rate_id = Column(fields.String(length=255), nullable=True, default='')
    default_price = Column(fields.Numeric(25, 2), default=0.0)

    def __repr__(self):
        return f'Currency: {self.name}'
