from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from apps.orders.models import OrderStatus, OrderType, Order
from apps.orders.services import order_update_status
from apps.orders.utils import decode_token


class DepositView(TemplateView):
    template_name = 'deposit.html'
    success_template_name = 'success.html'

    @staticmethod
    def get_pk_from_token(order_token: str):
        return decode_token(order_token)

    def get_order_from_context(self, context: dict) -> Order:
        return get_object_or_404(
            Order,
            pk=self.get_pk_from_token(context['order_token']),
            type=OrderType.DEPOSIT,
            status=OrderStatus.CREATED,
        )

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        context.update({
            'order': self.get_order_from_context(context)
        })

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        context.update({
            'order': order_update_status(
                self.get_order_from_context(context),
                status=OrderStatus.SENT,
            )
        })

        return TemplateResponse(
            request,
            template=self.success_template_name,
            context=context
        )
