from django.urls import path

from apps.cryptocurrencies.rest import views

app_name = 'cryptocurrencies'

urlpatterns = [
    path('provider/<int:network_id>/', views.ProviderAPIView.as_view(), name='provider'),
]
