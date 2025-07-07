from django.urls import path
from . import views

app_name = 'volantino'

urlpatterns = [
    path('sfoglia/', views.sfoglia_volantino, name='sfoglia'),
    path('pagina/<int:pagina_num>/', views.pagina_volantino, name='pagina'),
]

