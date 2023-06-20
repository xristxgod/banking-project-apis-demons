from django.urls import reverse
from django.http.request import HttpRequest
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from old_apps.orders.models import Order
from old_apps.orders.services import update_order


class ApproveCreateView(TemplateView):
    pass


class OrderCreateView(TemplateView):

    @property
    def obj(self) -> Order:
        context = self.get_context_data()
        return context.get('object')

    def get_success_url(self):
        # TODO
        # return reverse('feedback_admin:index')
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, pk=order_id)

        context.update({
            'object': order,
        })

        return context

    def post(self, request, *args, **kwargs):
        update_order(self.obj, Order.Status.SENT)
        return HttpResponseRedirect(self.get_success_url())
