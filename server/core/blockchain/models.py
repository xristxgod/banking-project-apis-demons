import dataclasses
import enum

import sqlalchemy as fields
from sqlalchemy import Column
from sqlalchemy.orm import relationship

import settings
from core.common import models


class NetworkFamily(enum.Enum):
    evm = 'evm'
    tron = 'tron'


class ABIType(enum.Enum):
    ERC20 = 'erc20'
    BEP20 = 'bep20'
    TRC20 = 'trc20'

    EVM_ORDER_PROVIDER = 'evm_order_provider'
    TRON_ORDER_PROVIDER = 'tron_order_provider'


class Network(models.Model):
    __tablename__ = 'blockchain__network'

    @dataclasses.dataclass()
    class CentralWallet:
        address: str
        private_key: str
        mnemonic: str

    name = Column(fields.String(length=255), nullable=False)
    short_name = Column(fields.String(length=255), nullable=False)

    native_symbol = Column(fields.String(length=255), nullable=False)
    native_decimal_place = Column(fields.Integer, nullable=False, default=18)

    node_url = Column(fields.String(length=255), nullable=False)
    is_active = Column(fields.Boolean, default=True, nullable=False)
    family = Column(fields.Enum(NetworkFamily), nullable=False)

    @property
    def central_address(self) -> CentralWallet:
        return self.CentralWallet(
            **settings.BLOCKCHAIN_CENTRAL_WALLETS[self.short_name.lower()],
        )

    def __repr__(self):
        return f'{self.name} ({self.family.value})'


class StableCoin(models.Model):
    __tablename__ = 'blockchain__stable_coin'

    address = Column(fields.String(length=42), index=True, nullable=False)
    name = Column(fields.String(length=255), nullable=True, default='')
    symbol = Column(fields.String(length=255), nullable=True, default='')
    decimal_place = Column(fields.Integer, nullable=True, default=18)
    abi_type = Column(fields.Enum(ABIType), nullable=True)
    extra = Column(fields.JSON, nullable=True, default=None)

    network_id = Column(fields.Integer, fields.ForeignKey('blockchain__network.id', ondelete='CASCADE'))
    network = relationship(Network, backref='stable_coins', lazy='selectin')

    def __repr__(self):
        return f'{self.symbol}:{self.abi_type}'


class OrderProvider(models.Model):
    __tablename__ = 'blockchain__order_provider'

    address = Column(fields.String(length=42), nullable=False)
    abi_type = Column(fields.Enum(ABIType), nullable=True)
    network_id = Column(fields.Integer, fields.ForeignKey('blockchain__network.id', ondelete='CASCADE'))
    network = relationship(Network, backref='order_providers', lazy='selectin')

    def __repr__(self):
        return f'OrderProvider: {self.network.name}'
