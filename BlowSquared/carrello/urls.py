from django.urls import path
from . import views

app_name = 'carrello'

urlpatterns = [
    path('', views.visualizza_carrello, name='visualizza'),
    path('checkout/', views.checkout, name='checkout'),
    path('ordine-completato/<str:codice_ordine>/', views.ordine_completato, name='ordine_completato'),
    path('aggiungi/<int:prodotto_id>/', views.aggiungi_al_carrello, name='aggiungi'),
    path('rimuovi/<int:elemento_id>/', views.rimuovi_dal_carrello, name='rimuovi'),
    path('aggiorna/<int:elemento_id>/', views.aggiorna_quantita_carrello, name='aggiorna_quantita'),
    path('svuota/', views.svuota_carrello, name='svuota'),
    path('api/count/', views.api_cart_count, name='api_count'),
]
