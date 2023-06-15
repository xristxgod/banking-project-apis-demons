from tortoise import models, fields, transactions

from apps.wallets.schemas import WalletType, MetamaskChainId
from apps.telegram.models import User


class Wallet(models.Model):
    address = fields.CharField(max_length=255)
    chain_id = fields.IntField(default=None, null=True)
    type = fields.CharEnumField(enum_type=WalletType, default=WalletType.METAMASK)
    user = fields.ForeignKeyField('models.User', related_name='wallets', on_delete=fields.CASCADE)

    class Meta:
        table = 'wallets_wallet'

    @property
    def enum_chain_id(self) -> MetamaskChainId:
        return MetamaskChainId(self.chain_id)

    @classmethod
    @transactions.atomic()
    async def create_wallet(cls, user: User, address: str, typ: WalletType, **kwargs):
        obj = cls(
            user=user,
            address=address,
            typ=typ,
            **kwargs,
        )
        await obj.save()
        return obj


class TempWallet(models.Model):
    address = fields.CharField(max_length=255, pk=True)
    private_key = fields.CharField(max_length=255)
    currency = fields.ForeignKeyField('models.Network', related_name='temp_wallets', on_delete=fields.RESTRICT)
    user = fields.ForeignKeyField('models.User', related_name='temp_wallets', on_delete=fields.RESTRICT)

    created = fields.DatetimeField(auto_now=True)
    deleted = fields.DatetimeField(default=None, null=True)

    life_time = 60 * 5

    class Meta:
        table = 'wallets_temp_wallet'

