from django.views.generic import TemplateView


class OrderCreatedView(TemplateView):
    template_name = 'order_create.html'
