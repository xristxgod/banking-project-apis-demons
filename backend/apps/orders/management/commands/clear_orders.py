import decimal

from django.db import transaction
from django.core.management.base import BaseCommand

from apps.orders.models import Order, ConvertTransactionAmount, UserDeposit
from apps.cryptocurrencies.models import Network, InternalWallet


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        Order.expired_qs().delete()
