from django.contrib import admin
from .models import Negozio, DisponibilitaProdotto

class DisponibilitaProdottoInline(admin.TabularInline):
    model = DisponibilitaProdotto
    extra = 0
    fields = ['prodotto', 'quantita_disponibile', 'quantita_minima', 'prezzo_locale', 'sconto_locale']
    readonly_fields = ['data_creazione', 'data_modifica']

@admin.register(Negozio)
class NegozioAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'citta', 'provincia', 'attivo', 'servizio_consegna_domicilio', 
        'data_apertura', 'numero_casse'
    ]
    list_filter = [
        'attivo', 'provincia', 'regione', 'servizio_consegna_domicilio',
        'servizio_farmacia', 'servizio_panetteria', 'servizio_macelleria', 'servizio_pescheria'
    ]
    search_fields = ['nome', 'citta', 'indirizzo', 'codice_negozio']
    readonly_fields = ['data_creazione', 'data_modifica']
    inlines = [DisponibilitaProdottoInline]
    
    fieldsets = (
        ('Informazioni di Base', {
            'fields': ('nome', 'codice_negozio', 'attivo')
        }),
        ('Indirizzo', {
            'fields': ('indirizzo', 'cap', 'citta', 'provincia', 'regione', 'nazione')
        }),
        ('Coordinate GPS', {
            'fields': ('latitudine', 'longitudine'),
            'classes': ('collapse',)
        }),
        ('Contatti', {
            'fields': ('telefono', 'email'),
            'classes': ('collapse',)
        }),
        ('Caratteristiche Negozio', {
            'fields': (
                'superficie_mq', 'numero_casse', 'parcheggio_disponibile', 
                'posti_parcheggio'
            ),
            'classes': ('collapse',)
        }),
        ('Servizi', {
            'fields': (
                'servizio_farmacia', 'servizio_panetteria', 'servizio_macelleria',
                'servizio_pescheria', 'servizio_consegna_domicilio', 'ritiro_click_collect'
            )
        }),
        ('Gestione', {
            'fields': ('direttore', 'data_apertura', 'orari_apertura'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('data_creazione', 'data_modifica'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DisponibilitaProdotto)
class DisponibilitaProdottoAdmin(admin.ModelAdmin):
    list_display = [
        'prodotto', 'negozio', 'quantita_disponibile', 'quantita_minima',
        'disponibile', 'scorta_bassa', 'prezzo_finale'
    ]
    list_filter = [
        'negozio', 'prodotto__categoria', 'in_promozione_locale', 
        'settore', 'ultimo_rifornimento'
    ]
    search_fields = [
        'prodotto__nome', 'prodotto__marca', 'negozio__nome', 
        'negozio__citta', 'settore'
    ]
    readonly_fields = ['data_creazione', 'data_modifica', 'prezzo_finale', 'posizione_completa']
    
    fieldsets = (
        ('Prodotto e Negozio', {
            'fields': ('negozio', 'prodotto')
        }),
        ('Gestione Scorte', {
            'fields': (
                'quantita_disponibile', 'quantita_minima', 'quantita_massima',
                'vendite_giornaliere_media'
            )
        }),
        ('Posizione nel Negozio', {
            'fields': ('settore', 'corridoio', 'scaffale', 'posizione_completa'),
            'classes': ('collapse',)
        }),
        ('Prezzi e Promozioni', {
            'fields': ('prezzo_locale', 'in_promozione_locale', 'sconto_locale', 'prezzo_finale')
        }),
        ('Rifornimenti', {
            'fields': ('ultimo_rifornimento', 'prossimo_rifornimento'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('data_creazione', 'data_modifica'),
            'classes': ('collapse',)
        }),
    )
    
    def disponibile(self, obj):
        return "✅" if obj.disponibile else "❌"
    disponibile.short_description = "Disponibile"
    
    def scorta_bassa(self, obj):
        return "⚠️" if obj.scorta_bassa else "✅"
    scorta_bassa.short_description = "Scorta"
