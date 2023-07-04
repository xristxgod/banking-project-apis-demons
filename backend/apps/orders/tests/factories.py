from django.utils import timezone

import faker
import factory.fuzzy
from factory.django import DjangoModelFactory

from apps.orders import models
from apps.users.tests.factories import UserFactory
from apps.cryptocurrencies.tests.factories import CurrencyFactory

fake = faker.Faker()


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = models.Order

    amount = factory.fuzzy.FuzzyDecimal(low=0.005, high=10**3, precision=18)
    currency = factory.SubFactory(CurrencyFactory)
    user = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice(choices=models.OrderStatus)

    class Params:
        is_confirmed = is_created = factory.Trait(
            confirmed=timezone.now(),
        )


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = models.Transaction

    order = factory.SubFactory(OrderFactory, transaction=None)
    transaction_hash = factory.Sequence(lambda n: "transactionHash#%d" % n)
    timestamp = fake.unique.unix_time()
    sender_address = factory.Sequence(lambda n: "senderAddress#%d" % n)
    recipient_address = factory.Sequence(lambda n: "recipientAddress#%d" % n)
    fee = factory.fuzzy.FuzzyDecimal(low=0.005, high=10**3, precision=18)


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = models.Payment

    order = factory.SubFactory(OrderFactory, payment=None)
    usdt_amount = factory.fuzzy.FuzzyDecimal(low=10, high=10**3, precision=2)
    usdt_exchange_rate = factory.fuzzy.FuzzyDecimal(low=40, high=99, precision=2)
    usdt_commission = factory.fuzzy.FuzzyDecimal(low=1, high=15, precision=2)
    type = factory.fuzzy.FuzzyChoice(choices=models.Payment.Type.choices)

    class Params:
        is_created = factory.Trait(
            order__status=models.OrderStatus.CREATED,
        )
        is_cancel = factory.Trait(
            order__status=models.OrderStatus.CANCEL,
            order__confirmed=timezone.now(),
        )
        is_done = factory.Trait(
            order__status=models.OrderStatus.DONE,
            order__transaction=factory.SubFactory(TransactionFactory),
            order__confirmed=timezone.now(),
        )


class TempWalletFactory(DjangoModelFactory):
    class Meta:
        model = models.TempWallet

    payment = factory.SubFactory(PaymentFactory, type=models.Payment.Type.DEPOSIT)

    address = factory.Sequence(lambda n: "address#%d" % n)
    private_key = factory.Sequence(lambda n: "private_key#%d" % n)
