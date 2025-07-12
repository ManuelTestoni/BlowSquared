from django.urls import path
from . import views

app_name = 'dirigenti'

urlpatterns = [
    path('login/', views.login_dirigente, name='login'),
    path('', views.dashboard_dirigente, name='dashboard'),
    path('negozi/', views.gestione_negozi, name='gestione_negozi'),
    path('dipendenti/', views.gestione_dipendenti, name='gestione_dipendenti'),
    path('statistiche/', views.statistiche, name='statistiche'),
    path('prodotti/', views.gestione_prodotti, name='gestione_prodotti'),
]
