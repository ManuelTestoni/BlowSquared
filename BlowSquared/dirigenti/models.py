from django.db import models
from django.contrib.auth.models import User

class Dirigente(models.Model):
    LIVELLI_ACCESSO = [
        ('direttore_generale', 'Direttore Generale'),
        ('vice_direttore', 'Vice Direttore'),
        ('direttore_negozio', 'Direttore di Negozio'),
        ('manager_area', 'Manager di Area'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dirigente')
    nome = models.CharField(max_length=50)
    cognome = models.CharField(max_length=50)
    eta = models.PositiveIntegerField()
    telefono = models.CharField(max_length=20, blank=True)
    indirizzo = models.CharField(max_length=255, blank=True)
    data_nascita = models.DateField(null=True, blank=True)
    
    # Livello di accesso del dirigente
    livello_accesso = models.CharField(
        max_length=20,
        choices=LIVELLI_ACCESSO,
        default='direttore_negozio'
    )
    
    # CORREZIONE: related_name univoci per evitare conflitti
    negozio_principale = models.ForeignKey(
        'negozi.Negozio',
        on_delete=models.CASCADE,
        related_name='dirigente_responsabile',
        help_text="Negozio principale che dirige"
    )
    
    negozi_supervisionati = models.ManyToManyField(
        'negozi.Negozio',
        related_name='dirigenti_area',
        blank=True,
        help_text="Negozi aggiuntivi sotto supervisione"
    )
    
    # Dati professionali
    data_assunzione = models.DateField(null=True, blank=True)
    stipendio_base = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    note_direzione = models.TextField(blank=True, help_text="Note dalla direzione generale")
    
    # Timestamp
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dirigente"
        verbose_name_plural = "Dirigenti"
        ordering = ['livello_accesso', 'cognome', 'nome']

    def __str__(self):
        return f"{self.nome} {self.cognome} ({self.get_livello_accesso_display()}) - {self.negozio_principale.nome}"
    
    @property
    def nome_completo(self):
        return f"{self.nome} {self.cognome}"
    
    def ha_accesso_negozio(self, negozio):
        """Verifica se il dirigente ha accesso a un negozio specifico"""
        if self.livello_accesso in ['direttore_generale', 'vice_direttore']:
            return True  # Accesso a tutti i negozi
        
        if self.negozio_principale == negozio:
            return True  # Accesso al negozio principale
            
        return self.negozi_supervisionati.filter(id=negozio.id).exists()
    
    def get_negozi_accessibili(self):
        """Restituisce tutti i negozi a cui ha accesso"""
        if self.livello_accesso in ['direttore_generale', 'vice_direttore']:
            from negozi.models import Negozio
            return Negozio.objects.all()
        
        # Per manager di area e direttori di negozio
        from negozi.models import Negozio
        negozi_ids = [self.negozio_principale.id]
        negozi_ids.extend(self.negozi_supervisionati.values_list('id', flat=True))
        
        return Negozio.objects.filter(id__in=negozi_ids)
    
    @property
    def numero_negozi_gestiti(self):
        """Restituisce il numero di negozi gestiti"""
        return self.get_negozi_accessibili().count()
    
    def can_manage_dipendenti(self):
        """Verifica se può gestire i dipendenti"""
        return self.livello_accesso in ['direttore_generale', 'vice_direttore', 'manager_area']
    
    def can_view_financials(self):
        """Verifica se può vedere i dati finanziari"""
        return self.livello_accesso in ['direttore_generale', 'vice_direttore']
        return self.livello_accesso in ['direttore_generale', 'vice_direttore']
