from django.urls import path

from apps.orders import views

app_name = 'orders'

urlpatterns = [
    path('deposit/<int:pk>/', views.DepositView.as_view(), name='deposit'),
]
