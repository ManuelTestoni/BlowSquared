from django.urls import path
from . import views

app_name = 'prodotti'

urlpatterns = [
    path('', views.list, name='list'),
    path('<int:product_id>/', views.detail, name='detail'),
]
