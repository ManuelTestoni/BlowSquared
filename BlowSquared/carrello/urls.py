from django.urls import path
from . import views

app_name = 'carrello'

urlpatterns = [
    path('', views.riepilogo, name='riepilogo'),
]
