from django.db import transaction
from django.core.management.base import BaseCommand

from apps.orders.models import Order


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        # Cancel orders
        Order.objects.expired().cancel()
