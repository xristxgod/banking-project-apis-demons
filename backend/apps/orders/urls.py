from django.urls import path

from apps.orders import views

app_name = 'orders'

urlpatterns = [
    path('deposit/<str:order_token>/', views.DepositView.as_view(), name='deposit'),
]
