from django.db import transaction
from django.core.management.base import BaseCommand

from old_apps.orders.models import Order


class Command(BaseCommand):
    @transaction.atomic()
    def handle(self, *args, **options):
        Order.expired_qs().delete()
