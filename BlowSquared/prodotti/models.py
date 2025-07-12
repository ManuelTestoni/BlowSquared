from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal

# Model per rappresentare un prodotto all'interno di un supermercato
class Prodotto(models.Model):
    CATEGORIE = [
        ('latticini', 'Latticini'),
        ('carne', 'Carne e Pesce'),
        ('verdura', 'Verdura'),
        ('frutta', 'Frutta'),
        ('conserve', 'Conserve e Sottoli'),
        ('pasta', 'Pasta e Riso'),
        ('olio', 'Olio e Condimenti'),
        ('spezie', 'Spezie e Aromi'),
        ('proteine', 'Proteine Vegetali'),
        ('snack', 'Snack e Merende'),        
        ('cereali', 'Cereali e Derivati'),
        ('bevande', 'Bevande'),
        ('dolci', 'Dolci e Snack'),
        ('surgelati', 'Surgelati'),
        ('altro', 'Altro'),
    ]
    
    nome = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, choices=CATEGORIE)
    descrizione = models.TextField(blank=True)
    codice_a_barre = models.CharField(max_length=50, unique=True)
    peso = models.CharField(max_length=50) 
    data_scadenza = models.DateField()
    foto = models.ImageField(upload_to='prodotti/', blank=True)
    valori_nutrizionali = models.JSONField(default=dict, blank=True)
    prezzo = models.DecimalField(max_digits=8, decimal_places=2)
    sconto = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                validators=[MinValueValidator(0), MaxValueValidator(100)])
    stock = models.PositiveIntegerField(default=0)
    ingredienti = models.TextField(blank=True)

    numero_recensioni = models.PositiveIntegerField(default=0)
    negozi = models.ManyToManyField(
        'negozi.Negozio',
        related_name='prodotti_disponibili',
        blank=True,
        help_text="Negozi dove questo prodotto è disponibile. Lascia vuoto per renderlo disponibile in tutti i negozi."
    )

    def __str__(self):
        negozi_info = ""
        if self.negozi.exists():
            negozi_nomi = [n.nome for n in self.negozi.all()[:2]]  # Primi 2 negozi
            negozi_info = f" - {', '.join(negozi_nomi)}"
            if self.negozi.count() > 2:
                negozi_info += f" (+{self.negozi.count()-2} altri)"
        return f"{self.nome} ({self.marca}){negozi_info}"

    @property 
    def prezzo_scontato(self):
        if self.sconto > 0:
            return self.prezzo * (100 - self.sconto) / 100
        return self.prezzo
    
    def is_disponibile_in_negozio(self, negozio):
        """Verifica se il prodotto è disponibile in un negozio specifico"""
        if not self.negozi.exists():
            # Se non ha negozi associati, è disponibile ovunque (prodotto comune)
            return True
        return self.negozi.filter(id=negozio.id).exists()
    
    def get_negozi_disponibilita(self):
        """Restituisce la lista dei negozi dove è disponibile"""
        if not self.negozi.exists():
            return "Tutti i negozi"
        return ", ".join([n.nome for n in self.negozi.all()])

class Ordine(models.Model):
    STATO = [
        ('in_attesa', 'In Attesa'),
        ('confermato', 'Confermato'),
        ('preparazione', 'In Preparazione'),
        ('spedito', 'Spedito'),
        ('consegnato', 'Consegnato'),
        ('annullato', 'Annullato'),
    ]
    
    METODO_PAGAMENTO = [
        ('carta', 'Carta di Credito'),
        ('paypal', 'PayPal'),
        ('contrassegno', 'Contrassegno'),
        ('bonifico', 'Bonifico Bancario'),
    ]
    
    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    numero_ordine = models.CharField(max_length=20, unique=True)
    data_ordine = models.DateTimeField(auto_now_add=True)
    stato = models.CharField(max_length=20, choices=STATO, default='in_attesa')

    nome_fatturazione = models.CharField(max_length=100)
    cognome_fatturazione = models.CharField(max_length=100)
    email_fatturazione = models.EmailField()
    telefono_fatturazione = models.CharField(max_length=20)
    
    indirizzo_fatturazione = models.CharField(max_length=200)
    citta_fatturazione = models.CharField(max_length=100)
    cap_fatturazione = models.CharField(max_length=10)
    provincia_fatturazione = models.CharField(max_length=50)
    
    spedizione_diversa = models.BooleanField(default=False)
    nome_spedizione = models.CharField(max_length=100, blank=True)
    cognome_spedizione = models.CharField(max_length=100, blank=True)
    indirizzo_spedizione = models.CharField(max_length=200, blank=True)
    citta_spedizione = models.CharField(max_length=100, blank=True)
    cap_spedizione = models.CharField(max_length=10, blank=True)
    provincia_spedizione = models.CharField(max_length=50, blank=True)
    
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_PAGAMENTO)
    
    subtotale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sconto_totale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    spese_spedizione = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    totale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    note = models.TextField(blank=True)
    
    def calcola_totali(self):
        """Calcola i totali dell'ordine basandosi sui dettagli"""
        dettagli = self.dettaglioordine_set.all()
        
        self.subtotale = sum(dettaglio.subtotale for dettaglio in dettagli)
        self.sconto_totale = sum(dettaglio.sconto_applicato for dettaglio in dettagli)
        
        imponibile = self.subtotale - self.sconto_totale
        self.iva = imponibile * Decimal('0.22')
        
        self.totale = imponibile + self.iva + self.spese_spedizione
        
        self.save()
    
    def genera_numero_ordine(self):
        """Genera un numero ordine univoco"""
        import datetime
        now = datetime.datetime.now()
        return f"ORD-{now.strftime('%Y%m%d')}-{self.id:06d}"
    
    def save(self, *args, **kwargs):
        if not self.numero_ordine:
            super().save(*args, **kwargs) 
            self.numero_ordine = self.genera_numero_ordine()
        super().save(*args, **kwargs)
    
    def genera_riepilogo_email(self):
        """Genera il riepilogo dell'ordine per l'email"""
        dettagli = self.dettaglioordine_set.all()
        
        riepilogo = f"""
RIEPILOGO ORDINE {self.numero_ordine}
Data: {self.data_ordine.strftime('%d/%m/%Y %H:%M')}
Stato: {self.get_stato_display()}

DATI CLIENTE:
{self.nome_fatturazione} {self.cognome_fatturazione}
Email: {self.email_fatturazione}
Telefono: {self.telefono_fatturazione}

INDIRIZZO FATTURAZIONE:
{self.indirizzo_fatturazione}
{self.cap_fatturazione} {self.citta_fatturazione} ({self.provincia_fatturazione})

PRODOTTI ORDINATI:
"""
        for dettaglio in dettagli:
            riepilogo += f"- {dettaglio.prodotto.nome} ({dettaglio.prodotto.marca})\n"
            riepilogo += f"  Quantità: {dettaglio.quantita} x €{dettaglio.prezzo_unitario}\n"
            if dettaglio.sconto_percentuale > 0:
                riepilogo += f"  Sconto: {dettaglio.sconto_percentuale}% (-€{dettaglio.sconto_applicato})\n"
            riepilogo += f"  Subtotale: €{dettaglio.subtotale}\n\n"
        
        riepilogo += f"""
RIEPILOGO COSTI:
Subtotale: €{self.subtotale}
Sconto totale: -€{self.sconto_totale}
Spese spedizione: €{self.spese_spedizione}
IVA (22%): €{self.iva}
TOTALE: €{self.totale}

Metodo di pagamento: {self.get_metodo_pagamento_display()}
"""
        if self.note:
            riepilogo += f"\nNote: {self.note}"
            
        return riepilogo
    
    def __str__(self):
        return f"Ordine {self.numero_ordine} - {self.utente.username}"
    
    class Meta:
        ordering = ['-data_ordine']


class DettaglioOrdine(models.Model):
    ordine = models.ForeignKey(Ordine, on_delete=models.CASCADE)
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    quantita = models.PositiveIntegerField()
    prezzo_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    sconto_percentuale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sconto_applicato = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    subtotale = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):

        self.sconto_applicato = (self.prezzo_unitario * self.quantita * self.sconto_percentuale) / 100
        self.subtotale = (self.prezzo_unitario * self.quantita) - self.sconto_applicato
        super().save(*args, **kwargs)
        
        self.ordine.calcola_totali()
    
    def __str__(self):
        return f"{self.prodotto.nome} x{self.quantita} - Ordine {self.ordine.numero_ordine}"
    
    class Meta:
        unique_together = ['ordine', 'prodotto']