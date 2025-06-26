from django.urls import path
from . import views

app_name = 'utenti'

urlpatterns = [
    path('', views.index, name='index'),
]
