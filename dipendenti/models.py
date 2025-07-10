from django.db import models
from django.contrib.auth.models import User

class Dipendente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dipendente')
    negozio = models.ForeignKey('negozi.Negozio', on_delete=models.CASCADE, related_name='dipendenti')

    def __str__(self):
        return f"{self.user.username} ({self.negozio.nome})"
