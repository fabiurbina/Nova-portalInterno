from django.urls import path
from .views import home, teste_gateway

urlpatterns = [
    path('', home, name='home'),
    path('teste-gateway/', 
    teste_gateway, name='teste_gateway'),
]