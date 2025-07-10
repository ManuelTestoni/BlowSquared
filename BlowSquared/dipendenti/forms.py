from django import forms
from prodotti.models import Prodotto

class ProdottoForm(forms.ModelForm):
    quantita = forms.IntegerField(
        label="Quantità per punto vendita", 
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Inserisci quantità'})
    )

    class Meta:
        model = Prodotto
        fields = ['nome', 'marca', 'categoria', 'prezzo', 'sconto', 'descrizione', 'foto', 'quantita']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome del prodotto'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca del prodotto'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'prezzo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Prezzo in euro'}),
            'sconto': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'placeholder': 'Sconto in %'}),
            'descrizione': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descrizione del prodotto'}),
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'nome': 'Nome Prodotto',
            'marca': 'Marca',
            'categoria': 'Categoria',
            'prezzo': 'Prezzo (€)',
            'sconto': 'Sconto (%)',
            'descrizione': 'Descrizione',
            'foto': 'Foto Prodotto',
        }
