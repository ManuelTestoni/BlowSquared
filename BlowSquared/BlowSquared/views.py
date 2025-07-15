from django.shortcuts import render
from prodotti.models import Prodotto

def home(request):
    # Recupera i 4 prodotti d'eccellenza specifici tramite codice a barre
    codici_eccellenza = [
        '8011111000001',  # Aceto Balsamico
        '8022222000002',  # Parmigiano Reggiano 
        '8033333000003',  # Tortellini
        '8044444000004',  # Lambrusco
    ]
    
    # Recupera i prodotti mantenendo l'ordine specificato
    prodotti_eccellenza = []
    for codice in codici_eccellenza:
        try:
            prodotto = Prodotto.objects.get(codice_a_barre=codice)
            prodotti_eccellenza.append(prodotto)
        except Prodotto.DoesNotExist:
            continue
    
    # Badge mapping per ogni prodotto
    badge_mapping = {
        '8011111000001': 'Premium',
        '8022222000002': 'Biologico', 
        '8033333000003': 'Artigianale',
        '8044444000004': 'Locale',
    }
    
    # Aggiungi badge ai prodotti
    for prodotto in prodotti_eccellenza:
        prodotto.badge = badge_mapping.get(prodotto.codice_a_barre, 'Eccellenza')
    
    context = {
        'prodotti_eccellenza': prodotti_eccellenza,
    }
    
    return render(request, 'home.html', context)