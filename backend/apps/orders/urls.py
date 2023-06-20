from django.urls import path

from apps.orders import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderSendView.as_view(), name='send'),
]
