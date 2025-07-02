from django.urls import path
from . import views

app_name = 'negozi'

urlpatterns = [
    path('', views.lista_negozi, name='lista'),
    path('seleziona/', views.seleziona_negozio, name='seleziona_negozio'),
    path('<int:negozio_id>/', views.dettaglio_negozio, name='dettaglio'),
    path('<int:negozio_id>/completo/', views.dettaglio_completo_negozio, name='dettaglio_completo'),
    path('<int:negozio_id>/seleziona/', views.seleziona_negozio_preferito, name='seleziona_preferito'),
    path('api/cerca-vicini/', views.cerca_negozi_vicini, name='cerca_vicini'),
]
