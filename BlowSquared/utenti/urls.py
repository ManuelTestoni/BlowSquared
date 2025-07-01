from django.urls import path
from . import views

app_name = 'utenti'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Liste della spesa
    path('liste-spesa/crea/', views.crea_lista_view, name='crea_lista'),
    path('liste-spesa/<int:lista_id>/elimina/', views.elimina_lista_view, name='elimina_lista'),
    path('liste-spesa/<int:lista_id>/visualizza/', views.visualizza_lista_popup, name='visualizza_lista_popup'),
    path('liste-spesa/<int:lista_id>/ordina/', views.ordina_lista_view, name='ordina_lista'),
    
    # AJAX
    path('api/cerca-prodotti/', views.cerca_prodotti_ajax, name='cerca_prodotti_ajax'),
]


