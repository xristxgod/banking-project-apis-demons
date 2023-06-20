from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from apps.orders.models import OrderStatus, OrderType, Order


class DepositView(TemplateView):
    template_name = 'deposit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = get_object_or_404(
            Order,
            pk=context['pk'],
            status=OrderStatus.CREATED,
            type=OrderType.DEPOSIT,
        )

        return context
