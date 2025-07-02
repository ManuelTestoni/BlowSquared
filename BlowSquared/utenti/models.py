from django.db import models
from django.contrib.auth.models import User
from prodotti.models import Prodotto
from decimal import Decimal
import math

# Estendo il profilo utente per includere posizione
class ProfiloUtente(models.Model):
    """Profilo esteso per l'utente con informazioni di posizione"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profilo'
    )
    
    # Posizione utente (solo manuale, no coordinate)
    citta = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Città dell'utente"
    )
    provincia = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="Provincia dell'utente (sigla)"
    )
    
    # Preferenze
    negozio_preferito = models.ForeignKey(
        'negozi.Negozio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utenti_preferiti',
        help_text="Negozio preferito dell'utente"
    )
    raggio_ricerca_km = models.PositiveIntegerField(
        default=50,
        help_text="Raggio di ricerca in km per negozi vicini"
    )
    
    # Privacy
    condividi_posizione = models.BooleanField(
        default=True,
        help_text="Consenso a condividere la posizione per suggerimenti"
    )
    
    # Timestamp
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profilo Utente"
        verbose_name_plural = "Profili Utenti"
    
    def __str__(self):
        return f"Profilo di {self.user.username}"
    
    def trova_negozi_in_provincia(self):
        """Trova negozi nella stessa provincia dell'utente"""
        if not self.provincia:
            return None
        
        from negozi.models import Negozio
        return Negozio.objects.filter(
            attivo=True,
            provincia=self.provincia
        ).order_by('citta', 'nome')
    
    def trova_negozi_in_citta(self):
        """Trova negozi nella stessa città dell'utente"""
        if not self.citta:
            return None
        
        from negozi.models import Negozio
        return Negozio.objects.filter(
            attivo=True,
            citta__icontains=self.citta
        ).order_by('nome')

class ListaSpesa(models.Model):
    """Modello per le liste della spesa degli utenti"""
    
    nome = models.CharField(
        max_length=100, 
        help_text="Nome della lista (es: 'Spesa settimanale', 'Cena romantica')"
    )
    utente = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='liste_spesa',
        help_text="Utente proprietario della lista"
    )
    descrizione = models.TextField(
        blank=True, 
        null=True,
        help_text="Descrizione opzionale della lista"
    )
    data_creazione = models.DateTimeField(
        auto_now_add=True,
        help_text="Data di creazione della lista"
    )
    data_modifica = models.DateTimeField(
        auto_now=True,
        help_text="Data dell'ultima modifica"
    )
    completata = models.BooleanField(
        default=False,
        help_text="Indica se la lista è stata completata/acquistata"
    )
    condivisa = models.BooleanField(
        default=False,
        help_text="Indica se la lista può essere condivisa con altri utenti"
    )
    
    class Meta:
        verbose_name = "Lista della Spesa"
        verbose_name_plural = "Liste della Spesa"
        ordering = ['-data_modifica', '-data_creazione']
        
    def __str__(self):
        return f"{self.nome} - {self.utente.username}"
    
    @property
    def numero_prodotti(self):
        """Restituisce il numero totale di prodotti nella lista"""
        return self.elementi.count()
    
    @property
    def quantita_totale(self):
        """Restituisce la quantità totale di tutti i prodotti"""
        return sum(elemento.quantita for elemento in self.elementi.all())
    
    @property
    def prezzo_stimato(self):
        """Calcola il prezzo stimato totale della lista"""
        totale = 0
        for elemento in self.elementi.all():
            prezzo_prodotto = elemento.prodotto.prezzo
            if elemento.prodotto.sconto > 0:
                prezzo_prodotto = prezzo_prodotto * (100 - elemento.prodotto.sconto) / 100
            totale += prezzo_prodotto * elemento.quantita
        return totale
    
    def duplica_lista(self, nuovo_nome=None):
        """Crea una copia della lista corrente"""
        if not nuovo_nome:
            nuovo_nome = f"Copia di {self.nome}"
        
        nuova_lista = ListaSpesa.objects.create(
            nome=nuovo_nome,
            utente=self.utente,
            descrizione=self.descrizione
        )
        
        # Copia tutti gli elementi
        for elemento in self.elementi.all():
            ElementoLista.objects.create(
                lista=nuova_lista,
                prodotto=elemento.prodotto,
                quantita=elemento.quantita,
                note=elemento.note
            )
        
        return nuova_lista


class ElementoLista(models.Model):
    """Modello per i singoli prodotti all'interno di una lista della spesa"""
    
    lista = models.ForeignKey(
        ListaSpesa, 
        on_delete=models.CASCADE, 
        related_name='elementi',
        help_text="Lista di appartenenza"
    )
    prodotto = models.ForeignKey(
        Prodotto, 
        on_delete=models.CASCADE,
        help_text="Prodotto da acquistare"
    )
    quantita = models.PositiveIntegerField(
        default=1,
        help_text="Quantità del prodotto da acquistare"
    )
    acquisito = models.BooleanField(
        default=False,
        help_text="Indica se il prodotto è già stato acquistato"
    )
    note = models.TextField(
        blank=True, 
        null=True,
        help_text="Note aggiuntive per il prodotto (es: 'marca specifica', 'se in offerta')"
    )
    data_aggiunta = models.DateTimeField(
        auto_now_add=True,
        help_text="Data di aggiunta del prodotto alla lista"
    )
    priorita = models.IntegerField(
        default=0,
        choices=[
            (0, 'Normale'),
            (1, 'Alta'),
            (2, 'Urgente')
        ],
        help_text="Priorità di acquisto del prodotto"
    )
    
    class Meta:
        verbose_name = "Elemento Lista"
        verbose_name_plural = "Elementi Lista"
        unique_together = ['lista', 'prodotto']  # Un prodotto può apparire solo una volta per lista
        ordering = ['-priorita', 'data_aggiunta']
        
    def __str__(self):
        return f"{self.prodotto.nome} x{self.quantita} - {self.lista.nome}"
    
    @property
    def prezzo_totale(self):
        """Calcola il prezzo totale per questo elemento (quantità * prezzo)"""
        prezzo_unitario = self.prodotto.prezzo
        if self.prodotto.sconto > 0:
            prezzo_unitario = prezzo_unitario * (100 - self.prodotto.sconto) / 100
        return prezzo_unitario * self.quantita
    
    @property
    def disponibile(self):
        """Verifica se il prodotto è disponibile in quantità sufficiente"""
        return self.prodotto.stock >= self.quantita
    
    def get_priorita_display_emoji(self):
        """Restituisce emoji per la priorità"""
        emoji_map = {
            0: '🔹',  # Normale
            1: '🟡',  # Alta
            2: '🔴'   # Urgente
        }
        return emoji_map.get(self.priorita, '🔹')


class ListaCondivisa(models.Model):
    """Modello per la condivisione delle liste tra utenti"""
    
    lista = models.ForeignKey(
        ListaSpesa, 
        on_delete=models.CASCADE, 
        related_name='condivisioni'
    )
    utente_condiviso = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="Utente con cui è condivisa la lista"
    )
    permessi = models.CharField(
        max_length=20,
        choices=[
            ('lettura', 'Solo Lettura'),
            ('modifica', 'Lettura e Modifica'),
            ('completo', 'Controllo Completo')
        ],
        default='lettura',
        help_text="Livello di permessi per l'utente"
    )
    data_condivisione = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = "Lista Condivisa"
        verbose_name_plural = "Liste Condivise"
        unique_together = ['lista', 'utente_condiviso']
        
    def __str__(self):
        return f"{self.lista.nome} condivisa con {self.utente_condiviso.username}"
        related_name='condivisioni'

    utente_condiviso = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="Utente con cui è condivisa la lista"
    )
    permessi = models.CharField(
        max_length=20,
        choices=[
            ('lettura', 'Solo Lettura'),
            ('modifica', 'Lettura e Modifica'),
            ('completo', 'Controllo Completo')
        ],
        default='lettura',
        help_text="Livello di permessi per l'utente"
    )
    data_condivisione = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = "Lista Condivisa"
        verbose_name_plural = "Liste Condivise"
        unique_together = ['lista', 'utente_condiviso']
        
    def __str__(self):
        return f"{self.lista.nome} condivisa con {self.utente_condiviso.username}"
