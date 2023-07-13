from django.urls import path

from apps.cryptocurrencies.rest import views

app_name = 'cryptocurrencies'

urlpatterns = [
    path('currency/<int:pk>/', views.currency_view, name='currency'),
    path('network/<int:pk>/', views.network_view, name='network'),
    path('provider/<int:pk>/', views.provider_view, name='provider'),
]

