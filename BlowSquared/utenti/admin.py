from django.contrib import admin
from .models import ListaSpesa, ElementoLista, ListaCondivisa

class ElementoListaInline(admin.TabularInline):
    model = ElementoLista
    extra = 0
    fields = ['prodotto', 'quantita', 'acquisito', 'priorita', 'note']
    readonly_fields = ['data_aggiunta']

@admin.register(ListaSpesa)
class ListaSpesaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'utente', 'numero_prodotti', 'prezzo_stimato', 'completata', 'data_creazione']
    list_filter = ['completata', 'condivisa', 'data_creazione', 'utente']
    search_fields = ['nome', 'utente__username', 'descrizione']
    readonly_fields = ['data_creazione', 'data_modifica', 'numero_prodotti', 'prezzo_stimato']
    inlines = [ElementoListaInline]
    
    fieldsets = (
        ('Informazioni Principali', {
            'fields': ('nome', 'utente', 'descrizione')
        }),
        ('Stato', {
            'fields': ('completata', 'condivisa')
        }),
        ('Statistiche', {
            'fields': ('numero_prodotti', 'prezzo_stimato'),
            'classes': ('collapse',)
        }),
        ('Date', {
            'fields': ('data_creazione', 'data_modifica'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ElementoLista)
class ElementoListaAdmin(admin.ModelAdmin):
    list_display = ['prodotto', 'lista', 'quantita', 'acquisito', 'priorita', 'prezzo_totale']
    list_filter = ['acquisito', 'priorita', 'data_aggiunta', 'lista__utente']
    search_fields = ['prodotto__nome', 'lista__nome', 'note']
    readonly_fields = ['data_aggiunta', 'prezzo_totale']
    
    fieldsets = (
        ('Prodotto', {
            'fields': ('lista', 'prodotto', 'quantita')
        }),
        ('Stato e Priorità', {
            'fields': ('acquisito', 'priorita')
        }),
        ('Note e Info', {
            'fields': ('note', 'data_aggiunta', 'prezzo_totale')
        }),
    )

@admin.register(ListaCondivisa)
class ListaCondivisaAdmin(admin.ModelAdmin):
    list_display = ['lista', 'utente_condiviso', 'permessi', 'data_condivisione']
    list_filter = ['permessi', 'data_condivisione']
    search_fields = ['lista__nome', 'utente_condiviso__username']
