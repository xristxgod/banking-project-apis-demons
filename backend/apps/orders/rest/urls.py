from django.urls import path

from apps.orders.rest import views

app_name = 'orders'

urlpatterns = [
    path('deposit/<int:pk>/', views.DepositAPIView.as_view(), name='deposit'),
]
