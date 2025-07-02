from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import math

class Negozio(models.Model):
    """Modello per i punti vendita della catena BlowSquared"""
    
    # Informazioni di base
    nome = models.CharField(
        max_length=100,
        help_text="Nome del punto vendita (es: 'BlowSquared Centro', 'BlowSquared Nord')"
    )
    codice_negozio = models.CharField(
        max_length=10,
        unique=True,
        help_text="Codice identificativo univoco del negozio (es: 'BS001', 'BS002')"
    )
    
    # Indirizzo completo
    indirizzo = models.CharField(
        max_length=200,
        help_text="Via e numero civico"
    )
    cap = models.CharField(
        max_length=10,
        help_text="Codice di Avviamento Postale"
    )
    citta = models.CharField(
        max_length=100,
        help_text="Città del negozio"
    )
    provincia = models.CharField(
        max_length=2,
        help_text="Sigla della provincia (es: 'MO', 'BO', 'RE')"
    )
    regione = models.CharField(
        max_length=50,
        help_text="Regione di appartenenza"
    )
    nazione = models.CharField(
        max_length=50,
        default="Italia",
        help_text="Nazione del negozio"
    )
    
    # Coordinate geografiche
    latitudine = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(Decimal('-90')), MaxValueValidator(Decimal('90'))],
        help_text="Coordinate GPS - Latitudine (es: 44.6471700)"
    )
    longitudine = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(Decimal('-180')), MaxValueValidator(Decimal('180'))],
        help_text="Coordinate GPS - Longitudine (es: 10.9251400)"
    )
    
    # Informazioni operative
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Numero di telefono del negozio"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email del punto vendita"
    )
    
    # Orari di apertura (JSON field per flessibilità)
    orari_apertura = models.JSONField(
        default=dict,
        blank=True,
        help_text="Orari di apertura per ogni giorno della settimana"
    )
    
    # Caratteristiche del negozio
    superficie_mq = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Superficie del negozio in metri quadrati"
    )
    numero_casse = models.PositiveIntegerField(
        default=1,
        help_text="Numero di casse disponibili"
    )
    parcheggio_disponibile = models.BooleanField(
        default=True,
        help_text="Indica se il negozio ha parcheggio"
    )
    posti_parcheggio = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Numero di posti parcheggio disponibili"
    )
    
    # Servizi disponibili
    servizio_farmacia = models.BooleanField(
        default=False,
        help_text="Presenza di servizio farmacia"
    )
    servizio_panetteria = models.BooleanField(
        default=False,
        help_text="Presenza di panetteria interna"
    )
    servizio_macelleria = models.BooleanField(
        default=False,
        help_text="Presenza di banco macelleria"
    )
    servizio_pescheria = models.BooleanField(
        default=False,
        help_text="Presenza di banco pescheria"
    )
    servizio_consegna_domicilio = models.BooleanField(
        default=True,
        help_text="Disponibilità servizio consegna a domicilio"
    )
    ritiro_click_collect = models.BooleanField(
        default=True,
        help_text="Disponibilità ritiro ordini online (Click & Collect)"
    )
    
    # Dati amministrativi
    direttore = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nome del direttore del punto vendita"
    )
    data_apertura = models.DateField(
        help_text="Data di apertura del negozio"
    )
    attivo = models.BooleanField(
        default=True,
        help_text="Indica se il negozio è attualmente operativo"
    )
    
    # Timestamp
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Negozio"
        verbose_name_plural = "Negozi"
        ordering = ['nome', 'citta']
        
    def __str__(self):
        return f"{self.nome} - {self.citta}"
    
    @property
    def indirizzo_completo(self):
        """Restituisce l'indirizzo completo formattato"""
        return f"{self.indirizzo}, {self.cap} {self.citta} ({self.provincia})"
    
    @property
    def coordinate(self):
        """Restituisce le coordinate come tupla"""
        return (float(self.latitudine), float(self.longitudine))
    
    def distanza_da(self, lat, lng):
        """Calcola la distanza in km da un punto specificato usando la formula di Haversine"""
        R = 6371  # Raggio della Terra in km
        
        lat1, lon1 = math.radians(float(self.latitudine)), math.radians(float(self.longitudine))
        lat2, lon2 = math.radians(lat), math.radians(lng)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def prodotti_disponibili(self):
        """Restituisce il queryset dei prodotti disponibili in questo negozio"""
        from prodotti.models import Prodotto
        return Prodotto.objects.filter(
            disponibilita_negozi__negozio=self,
            disponibilita_negozi__quantita_disponibile__gt=0
        ).distinct()
    
    def get_orari_oggi(self):
        """Restituisce gli orari di apertura di oggi"""
        import datetime
        giorni = ['lunedi', 'martedi', 'mercoledi', 'giovedi', 'venerdi', 'sabato', 'domenica']
        oggi = datetime.date.today().weekday()
        giorno_oggi = giorni[oggi]
        
        return self.orari_apertura.get(giorno_oggi, "Orari non disponibili")
    
    def is_aperto_ora(self):
        """Verifica se il negozio è attualmente aperto"""
        import datetime
        now = datetime.datetime.now().time()
        orari_oggi = self.get_orari_oggi()
        
        if isinstance(orari_oggi, str) and "chiuso" in orari_oggi.lower():
            return False
        
        # Logica semplificata - da implementare parsing orari
        return True  # Placeholder


class DisponibilitaProdotto(models.Model):
    """Modello per gestire la disponibilità dei prodotti nei singoli negozi"""
    
    negozio = models.ForeignKey(
        Negozio,
        on_delete=models.CASCADE,
        related_name='disponibilita_prodotti',
        help_text="Negozio di riferimento"
    )
    prodotto = models.ForeignKey(
        'prodotti.Prodotto',
        on_delete=models.CASCADE,
        related_name='disponibilita_negozi',
        help_text="Prodotto di riferimento"
    )
    
    # Gestione scorte
    quantita_disponibile = models.PositiveIntegerField(
        default=0,
        help_text="Quantità attualmente disponibile nel negozio"
    )
    quantita_minima = models.PositiveIntegerField(
        default=5,
        help_text="Quantità minima sotto la quale riordinare"
    )
    quantita_massima = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantità massima che il negozio può contenere"
    )
    
    # Posizione nel negozio
    settore = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Settore del negozio (es: 'Fresco', 'Secco', 'Surgelati')"
    )
    corridoio = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Numero corridoio o zona specifica"
    )
    scaffale = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Identificativo scaffale"
    )
    
    # Informazioni commerciali specifiche del negozio
    prezzo_locale = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Prezzo specifico per questo negozio (se diverso dal prezzo base)"
    )
    in_promozione_locale = models.BooleanField(
        default=False,
        help_text="Indica se il prodotto è in promozione in questo specifico negozio"
    )
    sconto_locale = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text="Sconto percentuale specifico del negozio"
    )
    
    # Gestione ordini
    ultimo_rifornimento = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data dell'ultimo rifornimento"
    )
    prossimo_rifornimento = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data del prossimo rifornimento previsto"
    )
    
    # Vendite
    vendite_giornaliere_media = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Media vendite giornaliere per questo prodotto nel negozio"
    )
    
    # Timestamp
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Disponibilità Prodotto"
        verbose_name_plural = "Disponibilità Prodotti"
        unique_together = ['negozio', 'prodotto']
        ordering = ['negozio__nome', 'prodotto__nome']
        
    def __str__(self):
        return f"{self.prodotto.nome} @ {self.negozio.nome} ({self.quantita_disponibile} pz)"
    
    @property
    def disponibile(self):
        """Verifica se il prodotto è disponibile"""
        return self.quantita_disponibile > 0
    
    @property
    def scorta_bassa(self):
        """Verifica se la scorta è sotto il minimo"""
        return self.quantita_disponibile <= self.quantita_minima
    
    @property
    def prezzo_finale(self):
        """Calcola il prezzo finale considerando sconti locali"""
        prezzo_base = self.prezzo_locale or self.prodotto.prezzo
        
        if self.in_promozione_locale and self.sconto_locale > 0:
            return prezzo_base * (100 - self.sconto_locale) / 100
        elif self.prodotto.sconto > 0:
            return prezzo_base * (100 - self.prodotto.sconto) / 100
        
        return prezzo_base
    
    @property
    def posizione_completa(self):
        """Restituisce la posizione completa nel negozio"""
        posizione = []
        if self.settore:
            posizione.append(f"Settore: {self.settore}")
        if self.corridoio:
            posizione.append(f"Corridoio: {self.corridoio}")
        if self.scaffale:
            posizione.append(f"Scaffale: {self.scaffale}")
        
        return " - ".join(posizione) if posizione else "Posizione non specificata"
    
    def giorni_autonomia(self):
        """Calcola i giorni di autonomia basati sulle vendite medie"""
        if self.vendite_giornaliere_media > 0:
            return float(self.quantita_disponibile) / float(self.vendite_giornaliere_media)
        return float('inf')
