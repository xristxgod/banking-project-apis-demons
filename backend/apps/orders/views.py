from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from apps.orders.models import OrderStatus, OrderType, Order
from apps.orders.services import order_sent


class DepositView(TemplateView):
    template_name = 'deposit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = get_object_or_404(
            Order,
            pk=context['pk'],
            type=OrderType.DEPOSIT,
        )

        context.update({
            'order': order,
        })

        return context

    @property
    def order(self) -> Order:
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        order = order_sent(self.order)
        # TODO

