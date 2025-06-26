from django.urls import path
from . import views

app_name = 'negozi'

urlpatterns = [
    path('', views.index, name='index'),
]
