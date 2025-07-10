from django.urls import path
from . import views

app_name = 'dipendenti'

urlpatterns = [
    path('login/', views.login_dipendente, name='login'),
    path('', views.dashboard_dipendente, name='dashboard'),
    path('aggiungi/', views.aggiungi_prodotto, name='aggiungi_prodotto'),
    path('aggiorna/<int:prodotto_id>/', views.aggiorna_quantita, name='aggiorna_quantita'),
]
