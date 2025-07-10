from django.urls import path, include
from . import views

app_name = 'dipendenti'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profilo/', views.profilo_view, name='profilo'),
    path('ordini/', views.ordini_view, name='ordini'),
    path('lista-spesa/', views.lista_spesa_view, name='lista_spesa'),
    path('negozi/', views.negozi_view, name='negozi'),
    path('impostazioni/', views.impostazioni_view, name='impostazioni'),
    path('dipendenti/', include('dipendenti.urls', namespace='dipendenti')),
]