from django.urls import path
from .views import upload_csv, list_fraudulent_clients

urlpatterns = [
    path('upload/', upload_csv, name='upload_csv'),
    path('fraudulent_clients/', list_fraudulent_clients, name='fraudulent_clients'),
]