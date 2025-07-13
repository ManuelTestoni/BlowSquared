from django import forms
from prodotti.models import Prodotto
from decimal import Decimal
from django.utils import timezone

class ProdottoForm(forms.ModelForm):
    quantita = forms.IntegerField(
        label="Quantità per punto vendita", 
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control styled-input', 
            'placeholder': 'Inserisci quantità disponibile'
        })
    )

    class Meta:
        model = Prodotto
        fields = [
            'nome', 'marca', 'categoria', 'descrizione', 'prezzo', 'sconto', 
            'peso', 'codice_a_barre', 'ingredienti', 'valori_nutrizionali', 
            'data_scadenza', 'foto'
        ]
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control styled-input', 
                'placeholder': 'Nome del prodotto'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control styled-input', 
                'placeholder': 'Marca del prodotto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control styled-select'
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'form-control styled-textarea', 
                'rows': 4, 
                'placeholder': 'Descrizione dettagliata del prodotto'
            }),
            'prezzo': forms.NumberInput(attrs={
                'class': 'form-control styled-input', 
                'step': '0.01', 
                'min': '0',
                'placeholder': 'Prezzo in euro (es. 2.50)'
            }),
            'sconto': forms.NumberInput(attrs={
                'class': 'form-control styled-input', 
                'min': '0', 
                'max': '70',
                'placeholder': 'Sconto in percentuale (0-70)'
            }),
            'peso': forms.TextInput(attrs={
                'class': 'form-control styled-input', 
                'placeholder': 'Peso/Volume (es. 500g, 1L, 250ml)'
            }),
            'codice_a_barre': forms.TextInput(attrs={
                'class': 'form-control styled-input', 
                'placeholder': 'Codice a barre (EAN-13)'
            }),
            'ingredienti': forms.Textarea(attrs={
                'class': 'form-control styled-textarea', 
                'rows': 3,
                'placeholder': 'Lista ingredienti separati da virgola'
            }),
            'valori_nutrizionali': forms.Textarea(attrs={
                'class': 'form-control styled-textarea', 
                'rows': 4,
                'placeholder': 'Valori nutrizionali per 100g/100ml'
            }),
            'data_scadenza': forms.DateInput(attrs={
                'class': 'form-control styled-input', 
                'type': 'date'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control styled-file', 
                'accept': 'image/*'
            }),
        }
        
        labels = {
            'nome': 'Nome Prodotto *',
            'marca': 'Marca *',
            'categoria': 'Categoria *',
            'descrizione': 'Descrizione',
            'prezzo': 'Prezzo (€) *',
            'sconto': 'Sconto (%)',
            'peso': 'Peso/Volume',
            'codice_a_barre': 'Codice a Barre',
            'ingredienti': 'Ingredienti',
            'valori_nutrizionali': 'Valori Nutrizionali',
            'data_scadenza': 'Data di Scadenza',
            'foto': 'Foto Prodotto',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendi obbligatori alcuni campi
        self.fields['nome'].required = True
        self.fields['marca'].required = True
        self.fields['categoria'].required = True
        self.fields['prezzo'].required = True
        
        # Imposta valori predefiniti
        if not self.instance.pk:  # Solo per nuovi prodotti
            self.fields['sconto'].initial = 0
            self.fields['quantita'].initial = 0

    def clean_prezzo(self):
        prezzo = self.cleaned_data.get('prezzo')
        if prezzo is not None and prezzo <= 0:
            raise forms.ValidationError("Il prezzo deve essere maggiore di zero.")
        return prezzo

    def clean_sconto(self):
        sconto = self.cleaned_data.get('sconto')
        if sconto is not None:
            if sconto < 0:
                raise forms.ValidationError("Lo sconto non può essere negativo.")
            if sconto > 70:
                raise forms.ValidationError("Lo sconto non può essere superiore al 70%.")
        return sconto

    def clean_data_scadenza(self):
        data_scadenza = self.cleaned_data.get('data_scadenza')
        if data_scadenza and data_scadenza < timezone.now().date():
            raise forms.ValidationError("La data di scadenza non può essere nel passato.")
        return data_scadenza

    def clean_codice_a_barre(self):
        codice = self.cleaned_data.get('codice_a_barre')
        if codice and len(codice) not in [8, 12, 13]:
            raise forms.ValidationError("Il codice a barre deve essere di 8, 12 o 13 cifre.")
        return codice

    def save(self, commit=True):
        prodotto = super().save(commit=False)
        if commit:
            prodotto.save()
            # Imposta la quantità stock
            prodotto.stock = self.cleaned_data.get('quantita', 0)
            prodotto.save()
        return prodotto
