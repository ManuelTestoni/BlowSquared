from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ProfiloUtente

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Il tuo indirizzo email'
        })
    )
    
    # Campi semplificati per la posizione (solo manuali)
    citta = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control location-input',
            'placeholder': 'La tua città (es: Modena, Bologna, Rimini)'
        }),
        label='Città'
    )
    provincia = forms.CharField(
        max_length=2,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control provincia-input',
            'placeholder': 'Sigla provincia (es: MO, BO, RN)',
            'maxlength': '2'
        }),
        label='Provincia'
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizza i widget per tutti i campi
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Scegli un username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Crea una password sicura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Conferma la tua password'
        })
    
    def clean_provincia(self):
        provincia = self.cleaned_data.get('provincia', '').upper().strip()
        
        # Lista delle province italiane valide
        province_valide = [
            'AG', 'AL', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AT', 'AV', 'BA', 'BG', 'BI', 'BL', 'BN', 'BO',
            'BR', 'BS', 'BT', 'BZ', 'CA', 'CB', 'CE', 'CH', 'CI', 'CL', 'CN', 'CO', 'CR', 'CS', 'CT',
            'CZ', 'EN', 'FC', 'FE', 'FG', 'FI', 'FM', 'FR', 'GE', 'GO', 'GR', 'IM', 'IS', 'KR', 'LC',
            'LE', 'LI', 'LO', 'LT', 'LU', 'MB', 'MC', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NA', 'NO',
            'NU', 'OG', 'OR', 'PA', 'PC', 'PD', 'PE', 'PG', 'PI', 'PN', 'PO', 'PR', 'PT', 'PU', 'PV',
            'PZ', 'RA', 'RC', 'RE', 'RG', 'RI', 'RM', 'RN', 'RO', 'SA', 'SI', 'SO', 'SP', 'SR', 'SS',
            'SU', 'SV', 'TA', 'TE', 'TN', 'TO', 'TP', 'TR', 'TS', 'TV', 'UD', 'VA', 'VB', 'VC', 'VE',
            'VI', 'VR', 'VS', 'VT', 'VV'
        ]
        
        if provincia and provincia not in province_valide:
            raise forms.ValidationError('Inserisci una sigla di provincia italiana valida (es: MO, BO, RN)')
        
        return provincia
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
            
            # Crea il profilo utente con le informazioni di posizione (solo manuali)
            ProfiloUtente.objects.create(
                user=user,
                citta=self.cleaned_data.get('citta', '').strip(),
                provincia=self.cleaned_data.get('provincia', '').upper().strip(),
                condividi_posizione=True  # Default True dato che non c'è geolocalizzazione
            )
        
        return user
        
        return user
