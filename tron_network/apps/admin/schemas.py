from tronpy.tron import TAddress

import settings
from apps.transaction.schemas import (
    BodyCreateTransfer, BodyCreateTransferFrom,
    BodyCreateFreeze, BodyCreateUnfreeze,
    BodySendTransaction,
)

ADMIN_ADDRESS = settings.CENTRAL_WALLET_CONFIG['address']


class BaseAdminPropertyMixin:
    @property
    def owner_address(self) -> TAddress:
        return ADMIN_ADDRESS

    from_address = owner_address

    class Config:
        exclude = (
            'owner_address',
        )


class BodyAdminCreateTransfer(BaseAdminPropertyMixin, BodyCreateTransfer):
    class Config:
        exclude = (
            'from_address',
        )


class BodyAdminCreateTransferFrom(BaseAdminPropertyMixin, BodyCreateTransferFrom):
    pass


class BodyAdminCreateFreeze(BaseAdminPropertyMixin, BodyCreateFreeze):
    pass


class BodyAdminCreateUnfreeze(BaseAdminPropertyMixin, BodyCreateUnfreeze):
    pass


class BodyAdminSendTransaction(BodySendTransaction):
    @property
    def private_key(self) -> str:
        return settings.CENTRAL_WALLET_CONFIG['private_key']

    class Config:
        exclude = (
            'private_key',
        )
