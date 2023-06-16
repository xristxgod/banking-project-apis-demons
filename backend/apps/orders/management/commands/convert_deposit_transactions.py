import decimal

from django.db import transaction
from django.core.management.base import BaseCommand

from apps.telegram.models import User
from apps.orders.models import Order, ConvertTransactionAmount, UserDeposit

SERVICES_COMMISSION_PERCENT = 5         # %


class Command(BaseCommand):

    def telegram_notification(self, user: User, order: Order):
        # TODO Изменить сообщение юзера, на готовю транзакцию
        pass

    def take_usd_exchange_rate(self, symbol: str) -> decimal.Decimal:
        # TODO
        pass

    @classmethod
    def calculate_amount_and_commission(cls, amount: decimal.Decimal,
                                        usd_exchange_rate: decimal.Decimal) -> tuple[decimal.Decimal, decimal.Decimal]:
        usd_amount = amount * usd_exchange_rate
        commission = amount - (amount / decimal.Decimal(100)) * 5

        return usd_amount, commission

    @transaction.atomic()
    def create_convert_amount(self, order: Order):
        usd_exchange_rate = self.take_usd_exchange_rate(order.currency.symbol)

        amount, commission = self.calculate_amount_and_commission(
            amount=order.amount,
            usd_exchange_rate=usd_exchange_rate
        )

        deposit = UserDeposit.objects.create(
            order=order,
            amount=amount,
            commission=commission,
        )
        ConvertTransactionAmount.objects.create(
            usd_exchange_rate=usd_exchange_rate,
            deposit=deposit,
        )

        order.status = Order.Status.DONE
        order.save()

    @transaction.atomic()
    def handle(self, *args, **options):
        for order in Order.objects.filter(status=Order.Status.PROCESSED):
            self.create_convert_amount(order)
