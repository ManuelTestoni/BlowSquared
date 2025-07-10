from django import forms
from prodotti.models import Prodotto

class ProdottoForm(forms.ModelForm):
    quantita = forms.IntegerField(label="Quantità per punto vendita", min_value=0)

    class Meta:
        model = Prodotto
        fields = ['nome', 'marca', 'categoria', 'prezzo', 'sconto', 'descrizione', 'foto', 'quantita']
