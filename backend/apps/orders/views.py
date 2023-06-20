from django.views.generic import TemplateView


class OrderSendView(TemplateView):
    template_name = 'order_send.html'
