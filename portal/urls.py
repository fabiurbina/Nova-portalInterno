from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/guia-condenacao/', views.guia_condenacao, name='guia_condenacao'),
    path('teste-gateway/', views.teste_gateway, name='teste_gateway'),
]