from django.db import models
from django.contrib.auth.models import User

class Dipendente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dipendente')
    nome = models.CharField(max_length=50)
    cognome = models.CharField(max_length=50)
    eta = models.PositiveIntegerField()
    telefono = models.CharField(max_length=20, blank=True)
    indirizzo = models.CharField(max_length=255, blank=True)
    data_nascita = models.DateField(null=True, blank=True)
    negozio = models.ForeignKey('negozi.Negozio', on_delete=models.CASCADE, related_name='dipendenti')

    class Meta:
        verbose_name = "Dipendente"
        verbose_name_plural = "Dipendenti"

    def __str__(self):
        return f"{self.nome} {self.cognome} ({self.user.username}) - {self.negozio.nome}"
