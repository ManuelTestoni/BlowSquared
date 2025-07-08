from django.urls import path
from . import views

app_name = 'utenti'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('liste-spesa/', views.liste_spesa_view, name='liste_spesa'),
    path('liste-spesa/crea/', views.crea_lista_view, name='crea_lista'),
    path('liste-spesa/<int:lista_id>/', views.dettaglio_lista_view, name='dettaglio_lista'),
    path('liste-spesa/<int:lista_id>/visualizza/', views.visualizza_lista_popup, name='visualizza_lista_popup'),
    path('liste-spesa/<int:lista_id>/elimina/', views.elimina_lista_view, name='elimina_lista'),
    path('liste-spesa/<int:lista_id>/ordina/', views.ordina_lista_view, name='ordina_lista'),
    path('liste-spesa/<int:lista_id>/aggiungi-al-carrello/', views.aggiungi_lista_al_carrello, name='aggiungi_lista_al_carrello'),
    path('liste-spesa/<int:lista_id>/aggiungi/', views.aggiungi_prodotto_lista, name='aggiungi_prodotto_lista'),
    path('liste-spesa/<int:lista_id>/rimuovi/<int:elemento_id>/', views.rimuovi_prodotto_lista, name='rimuovi_prodotto_lista'),
    path('ajax/cerca-prodotti/', views.cerca_prodotti_ajax, name='cerca_prodotti_ajax'),
    path('api/cerca-prodotti/', views.cerca_prodotti_ajax, name='api_cerca_prodotti'),  # Aggiungi questo
]


