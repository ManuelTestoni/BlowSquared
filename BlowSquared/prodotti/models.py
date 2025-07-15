from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

# Model per rappresentare un prodotto all'interno di un supermercato
class Prodotto(models.Model):
    #Categorie di prodotti disponibili
    CATEGORIE = [
        ('latticini', 'Latticini'),
        ('carne', 'Carne e Pesce'),
        ('fresco', 'Fresco (Pesce e Frutti di Mare)'),
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
                                validators=[MinValueValidator(0), MaxValueValidator(70)])
    stock = models.PositiveIntegerField(default=0)
    ingredienti = models.TextField(blank=True)

    numero_recensioni = models.PositiveIntegerField(default=0)
    #Relazione con il modello Negozi 
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

    def clean(self):
        """Validazione personalizzata del modello"""
        if self.data_scadenza and self.data_scadenza < timezone.now().date():
            raise ValidationError({'data_scadenza': 'La data di scadenza non può essere nel passato.'})
        
        if self.sconto and (self.sconto < 0 or self.sconto > 70):
            raise ValidationError({'sconto': 'Lo sconto deve essere compreso tra 0% e 70%.'})
    
    def save(self, *args, **kwargs):
        """Override del save per eseguire la validazione"""
        self.clean()
        super().save(*args, **kwargs)

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

