from django.urls import path

from old_apps.telegram import views

urlpatterns = [
    path('telegram/update', views.APIView.as_view(), name='update'),
]
