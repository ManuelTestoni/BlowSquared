from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ProfiloUtente

# Rimuovi la registrazione di User esistente e crea una personalizzata
admin.site.unregister(User)

# Inline per il profilo
class ProfiloInline(admin.StackedInline):
    model = ProfiloUtente
    can_delete = False
    verbose_name_plural = 'Profilo'
    fields = ('citta', 'provincia', 'negozio_preferito')

# User admin personalizzato
class UserAdmin(BaseUserAdmin):
    inlines = [ProfiloInline]
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Registra il nuovo UserAdmin
admin.site.register(User, UserAdmin)

# Admin per il Profilo
@admin.register(ProfiloUtente)
class ProfiloUtenteAdmin(admin.ModelAdmin):
    list_display = ['user', 'citta', 'provincia', 'negozio_preferito']
    list_filter = ['citta', 'provincia', 'negozio_preferito']
    search_fields = ['user__username', 'user__email', 'citta']
    ordering = ['user__username']

# Registra i modelli delle liste solo se esistono
try:
    from .models import ListaSpesa, ElementoLista, ListaCondivisa
    
    @admin.register(ListaSpesa)
    class ListaSpesaAdmin(admin.ModelAdmin):
        list_display = ['nome', 'utente', 'numero_prodotti', 'prezzo_stimato', 'completata', 'data_creazione']
        list_filter = ['completata', 'data_creazione', 'data_modifica']
        search_fields = ['nome', 'utente__username', 'descrizione']
        ordering = ['-data_modifica']
        readonly_fields = ['data_creazione', 'data_modifica']
        
        fieldsets = (
            ('Informazioni Base', {
                'fields': ('nome', 'utente', 'descrizione')
            }),
            ('Stato', {
                'fields': ('completata',)
            }),
            ('Date', {
                'fields': ('data_creazione', 'data_modifica'),
                'classes': ('collapse',)
            }),
        )
    
    @admin.register(ElementoLista)
    class ElementoListaAdmin(admin.ModelAdmin):
        list_display = ['prodotto', 'lista', 'quantita', 'priorita', 'data_aggiunta']
        list_filter = ['priorita', 'data_aggiunta', 'lista__completata']
        search_fields = ['prodotto__nome', 'lista__nome', 'note']
        ordering = ['-data_aggiunta']
        
        fieldsets = (
            ('Prodotto', {
                'fields': ('lista', 'prodotto', 'quantita')
            }),
            ('Dettagli', {
                'fields': ('priorita', 'note')
            }),
            ('Informazioni', {
                'fields': ('data_aggiunta',),
                'classes': ('collapse',)
            }),
        )
        
        readonly_fields = ['data_aggiunta']
        
        def get_queryset(self, request):
            return super().get_queryset(request).select_related('prodotto', 'lista', 'lista__utente')

    @admin.register(ListaCondivisa)
    class ListaCondivisaAdmin(admin.ModelAdmin):
        list_display = ['lista', 'utente_condiviso', 'permessi', 'data_condivisione']
        list_filter = ['permessi', 'data_condivisione']
        search_fields = ['lista__nome', 'utente_condiviso__username']
        ordering = ['-data_condivisione']

except ImportError:
    # I modelli non esistono ancora, ignora
    pass
