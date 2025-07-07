from django.db import models
from django.contrib.auth.models import User
from prodotti.models import Prodotto
from decimal import Decimal

class Carrello(models.Model):
    """
    Modello per il carrello della spesa di un utente
    Relazione 1-1 con User: ogni utente ha un solo carrello attivo
    """
    
    utente = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='carrello',
        help_text="Utente proprietario del carrello"
    )
    
    data_creazione = models.DateTimeField(
        auto_now_add=True,
        help_text="Data di creazione del carrello"
    )
    
    data_modifica = models.DateTimeField(
        auto_now=True,
        help_text="Data dell'ultima modifica al carrello"
    )
    
    # Negozio di riferimento per verificare disponibilità
    negozio = models.ForeignKey(
        'negozi.Negozio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Negozio di riferimento per questo carrello"
    )
    
    class Meta:
        verbose_name = "Carrello"
        verbose_name_plural = "Carrelli"
        
    def __str__(self):
        return f"Carrello di {self.utente.username}"
    
    @property
    def numero_articoli(self):
        """Restituisce il numero totale di articoli nel carrello"""
        return sum(item.quantita for item in self.elementi.all())
    
    @property
    def numero_prodotti_unici(self):
        """Restituisce il numero di prodotti diversi nel carrello"""
        return self.elementi.count()
    
    @property
    def subtotale(self):
        """Calcola il subtotale (senza spese di spedizione)"""
        totale = Decimal('0.00')
        for item in self.elementi.all():
            totale += item.prezzo_totale
        return totale
    
    @property
    def spese_spedizione(self):
        """Calcola le spese di spedizione (gratis sopra €30)"""
        soglia_gratuita = Decimal('30.00')
        costo_standard = Decimal('4.90')
        
        if self.subtotale >= soglia_gratuita:
            return Decimal('0.00')
        return costo_standard
    
    @property
    def totale_finale(self):
        """Calcola il totale finale (subtotale + spedizione)"""
        return self.subtotale + self.spese_spedizione
    
    @property
    def is_vuoto(self):
        """Verifica se il carrello è vuoto"""
        return not self.elementi.exists()
    
    def svuota_carrello(self):
        """Rimuove tutti gli elementi dal carrello"""
        self.elementi.all().delete()
    
    def aggiungi_prodotto(self, prodotto, quantita=1):
        """
        Aggiunge un prodotto al carrello o incrementa la quantità se già presente
        """
        elemento, creato = ElementoCarrello.objects.get_or_create(
            carrello=self,
            prodotto=prodotto,
            defaults={'quantita': quantita}
        )
        
        if not creato:
            # Se l'elemento esiste già, incrementa la quantità
            elemento.quantita += quantita
            elemento.save()
        
        return elemento
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Metodo di classe per ottenere o creare il carrello dell'utente"""
        carrello, created = cls.objects.get_or_create(
            utente=user,
            defaults={'negozio': user.profilo.negozio_preferito if hasattr(user, 'profilo') else None}
        )
        return carrello


class ElementoCarrello(models.Model):
    """
    Modello per i singoli elementi (prodotti) all'interno del carrello
    """
    
    carrello = models.ForeignKey(
        Carrello,
        on_delete=models.CASCADE,
        related_name='elementi',
        help_text="Carrello di appartenenza"
    )
    
    prodotto = models.ForeignKey(
        Prodotto,
        on_delete=models.CASCADE,
        help_text="Prodotto nel carrello"
    )
    
    quantita = models.PositiveIntegerField(
        default=1,
        help_text="Quantità del prodotto nel carrello"
    )
    
    # Prezzo al momento dell'aggiunta (per storicizzare)
    prezzo_unitario = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Prezzo unitario al momento dell'aggiunta al carrello"
    )
    
    # Sconto al momento dell'aggiunta (per storicizzare)
    sconto_applicato = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentuale di sconto applicata al momento dell'aggiunta"
    )
    
    data_aggiunta = models.DateTimeField(
        auto_now_add=True,
        help_text="Data di aggiunta del prodotto al carrello"
    )
    
    data_modifica = models.DateTimeField(
        auto_now=True,
        help_text="Data dell'ultima modifica alla quantità"
    )
    
    class Meta:
        verbose_name = "Elemento Carrello"
        verbose_name_plural = "Elementi Carrello"
        unique_together = ['carrello', 'prodotto']  # Un prodotto può apparire solo una volta per carrello
        ordering = ['-data_aggiunta']
        
    def __str__(self):
        return f"{self.prodotto.nome} x{self.quantita} - {self.carrello.utente.username}"
    
    @property
    def prezzo_unitario_scontato(self):
        """Calcola il prezzo unitario con sconto applicato"""
        if self.sconto_applicato > 0:
            return self.prezzo_unitario * (100 - self.sconto_applicato) / 100
        return self.prezzo_unitario
    
    @property
    def prezzo_totale(self):
        """Calcola il prezzo totale per questo elemento (quantità * prezzo scontato)"""
        return self.prezzo_unitario_scontato * self.quantita
    
    @property
    def risparmio_totale(self):
        """Calcola il risparmio totale se c'è uno sconto"""
        if self.sconto_applicato > 0:
            prezzo_originale_totale = self.prezzo_unitario * self.quantita
            return prezzo_originale_totale - self.prezzo_totale
        return Decimal('0.00')
    
    def save(self, *args, **kwargs):
        """Override del save per storicizzare prezzo e sconto correnti"""
        if not self.prezzo_unitario:
            self.prezzo_unitario = self.prodotto.prezzo
            self.sconto_applicato = self.prodotto.sconto
        super().save(*args, **kwargs)


