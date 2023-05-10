from tortoise import models, fields


class Contract(models.Model):
    address = fields.CharField(max_length=50, unique=True)
    symbol = fields.CharField(max_length=10, unique=True)
    name = fields.CharField(max_length=25)
    decimal_place = fields.IntField(default=8)

    class Meta:
        table = "common_contract"
