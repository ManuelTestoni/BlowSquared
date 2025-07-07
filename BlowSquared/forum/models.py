from django.db import models
from django.contrib.auth.models import User
from negozi.models import Negozio
from prodotti.models import Prodotto
import json

class MessaggioForum(models.Model):
    TIPO_CHOICES = [
        ('chat', 'Messaggio Chat'),
        ('recensione', 'Recensione Negozio'),
        ('ricetta', 'Ricetta'),
    ]
    
    STELLE_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    autore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messaggi_forum')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='chat')
    contenuto = models.TextField(help_text="Contenuto del messaggio")
    
    # Campi per recensioni
    negozio_recensito = models.ForeignKey(
        Negozio, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Negozio recensito"
    )
    stelle = models.IntegerField(
        choices=STELLE_CHOICES, 
        null=True, 
        blank=True,
        help_text="Valutazione stelle"
    )
    
    # Campi per ricette
    nome_ricetta = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        help_text="Nome della ricetta"
    )
    ingredienti_ricetta = models.JSONField(
        default=list, 
        null=True, 
        blank=True,
        help_text="Lista ingredienti con prodotti"
    )
    note_ricetta = models.TextField(
        null=True, 
        blank=True,
        help_text="Note aggiuntive per la ricetta"
    )
    
    # Metadata
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Messaggio Forum"
        verbose_name_plural = "Messaggi Forum"
        ordering = ['-data_creazione']
    
    def __str__(self):
        if self.tipo == 'recensione':
            return f"Recensione di {self.autore.username} per {self.negozio_recensito.nome}"
        elif self.tipo == 'ricetta':
            return f"Ricetta '{self.nome_ricetta}' di {self.autore.username}"
        else:
            return f"Messaggio di {self.autore.username}"
    
    @property
    def stelle_emoji(self):
        """Restituisce le stelle come emoji"""
        if self.stelle:
            return '⭐' * self.stelle
        return ''
    
    @property
    def ingredienti_formattati(self):
        """Formatta gli ingredienti per la visualizzazione"""
        if not self.ingredienti_ricetta:
            return []
        
        ingredienti_con_nomi = []
        for ingrediente in self.ingredienti_ricetta:
            try:
                prodotto = Prodotto.objects.get(id=ingrediente['prodotto_id'])
                ingredienti_con_nomi.append({
                    'nome': prodotto.nome,
                    'marca': prodotto.marca,
                    'quantita': ingrediente.get('quantita', '1'),
                    'note': ingrediente.get('note', ''),
                })
            except Prodotto.DoesNotExist:
                continue
        
        return ingredienti_con_nomi
    
    def to_dict(self):
        """Converte il messaggio in dizionario per WebSocket"""
        data = {
            'id': self.id,
            'autore': self.autore.username,
            'tipo': self.tipo,
            'contenuto': self.contenuto,
            'data_creazione': self.data_creazione.strftime('%d/%m/%Y %H:%M'),
            'timestamp': self.data_creazione.timestamp(),
        }
        
        if self.tipo == 'recensione':
            data.update({
                'negozio': {
                    'nome': self.negozio_recensito.nome,
                    'citta': self.negozio_recensito.citta,
                } if self.negozio_recensito else None,
                'stelle': self.stelle,
                'stelle_emoji': self.stelle_emoji,
            })
        
        elif self.tipo == 'ricetta':
            data.update({
                'nome_ricetta': self.nome_ricetta,
                'ingredienti': self.ingredienti_formattati,
                'note_ricetta': self.note_ricetta,
            })
        
        return data
        return data
