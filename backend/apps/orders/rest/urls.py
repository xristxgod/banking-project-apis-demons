from django.urls import path

from apps.orders.rest import views

app_name = 'orders'

urlpatterns = [
    path('payment/<int:pk>/', views.PaymentAPIView.as_view(), name='payment'),
]
