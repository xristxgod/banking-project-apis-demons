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

    amount = fake.unique.pydecimal(left_digits=25, right_digits=25, positive=True)
    currency = factory.SubFactory(CurrencyFactory)
    user = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice(choices=models.OrderStatus.choices)

    deposit = factory.RelatedFactory('apps.orders.tests.DepositFactory')
    transaction = factory.RelatedFactory('apps.orders.tests.TransactionFactory')

    class Params:
        is_created = factory.Trait(
            status=models.OrderStatus.CREATED,
            deposit=factory.RelatedFactory('apps.orders.tests.DepositFactory'),
            transaction=None,
        )
        is_cancel = factory.Trait(
            status=models.OrderStatus.CANCEL,
            deposit=factory.RelatedFactory('apps.orders.tests.DepositFactory'),
            transaction=None,
        )
        is_sent = factory.Trait(
            status=models.OrderStatus.SENT,
            deposit=factory.RelatedFactory('apps.orders.tests.DepositFactory'),
            transaction=None,
        )
        is_done = factory.Trait(
            status=models.OrderStatus.DONE,
            deposit=factory.RelatedFactory('apps.orders.tests.DepositFactory'),
            transaction=factory.RelatedFactory('apps.orders.tests.TransactionFactory'),
        )
        is_error = factory.Trait(
            status=models.OrderStatus.ERROR,
            deposit=factory.RelatedFactory('apps.orders.tests.DepositFactory'),
            transaction=None,
        )


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = models.Transaction

    order = factory.SubFactory(OrderFactory)
    transaction_hash = factory.Sequence(lambda n: "transactionHash#%d" % n)
    timestamp = fake.unique.unix_time()
    sender_address = factory.SubFactory(lambda n: "senderAddress#%d" % n)
    recipient_address = factory.SubFactory(lambda n: "recipientAddress#%d" % n)
    fee = fake.unique.pydecimal(left_digits=2, right_digits=25, positive=True, max_value=10)


class DepositFactory(DjangoModelFactory):
    class Meta:
        model = models.Deposit

    order = factory.SubFactory(OrderFactory)
    amount = fake.unique.pydecimal(left_digits=25, right_digits=2, positive=True)
    usd_exchange_rate = fake.unique.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=60, max_value=99)
    commission = fake.unique.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=1, max_value=15)
