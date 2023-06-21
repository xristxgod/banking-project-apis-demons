from django.urls import path

from apps.telegram import views

app_name = 'telegram'

urlpatterns = [
    path('webhook/', views, name='webhook'),
]
