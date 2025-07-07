from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_home, name='home'),
    path('api/negozi/', views.api_negozi, name='api_negozi'),
    path('api/prodotti/', views.api_prodotti, name='api_prodotti'),
    path('api/messaggi-recenti/', views.api_messaggi_recenti, name='api_messaggi_recenti'),
    path('api/invia-messaggio/', views.api_invia_messaggio, name='api_invia_messaggio'),
]
