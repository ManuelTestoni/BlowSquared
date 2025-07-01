from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Prodotto
from decimal import Decimal

def list(request):
    """Vista per la lista di tutti i prodotti con filtri e ricerca"""
    
    # Recupera tutti i prodotti
    prodotti = Prodotto.objects.all()
    
    # Filtri dalla query string
    search_query = request.GET.get('search', '')
    categoria = request.GET.get('categoria', '')
    prezzo_min = request.GET.get('prezzo_min', '')
    prezzo_max = request.GET.get('prezzo_max', '')
    ordine = request.GET.get('ordine', 'nome')
    
    # Applica filtri se presenti
    if search_query:
        prodotti = prodotti.filter(
            Q(nome__icontains=search_query) |
            Q(marca__icontains=search_query) |
            Q(descrizione__icontains=search_query) |
            Q(ingredienti__icontains=search_query)
        )
    
    if categoria:
        prodotti = prodotti.filter(categoria=categoria)
    
    if prezzo_min:
        try:
            prodotti = prodotti.filter(prezzo__gte=Decimal(prezzo_min))
        except:
            pass
    
    if prezzo_max:
        try:
            prodotti = prodotti.filter(prezzo__lte=Decimal(prezzo_max))
        except:
            pass
    
    # Ordinamento
    ordini_validi = {
        'nome': 'nome',
        'prezzo_asc': 'prezzo',
        'prezzo_desc': '-prezzo',
        'categoria': 'categoria',
        'marca': 'marca',
        'sconto': '-sconto'
    }
    
    if ordine in ordini_validi:
        prodotti = prodotti.order_by(ordini_validi[ordine])
    
    # Aggiungi prezzo scontato per ogni prodotto
    for prodotto in prodotti:
        if prodotto.sconto > 0:
            prodotto.prezzo_scontato = prodotto.prezzo * (100 - prodotto.sconto) / 100
        else:
            prodotto.prezzo_scontato = prodotto.prezzo
    
    # Se è una richiesta AJAX, restituisci JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        prodotti_data = []
        for prodotto in prodotti:
            prodotti_data.append({
                'id': prodotto.id,
                'nome': prodotto.nome,
                'marca': prodotto.marca,
                'categoria': prodotto.get_categoria_display(),
                'categoria_key': prodotto.categoria,
                'prezzo': str(prodotto.prezzo),
                'sconto': str(prodotto.sconto),
                'prezzo_scontato': str(prodotto.prezzo_scontato),
                'foto': prodotto.foto.url if prodotto.foto else '',
                'descrizione': prodotto.descrizione,
                'peso': prodotto.peso,
                'stock': prodotto.stock,
                'numero_recensioni': prodotto.numero_recensioni
            })
        
        return JsonResponse({
            'prodotti': prodotti_data,
            'count': len(prodotti_data)
        })
    
    # Lista categorie per il filtro
    categorie = Prodotto.CATEGORIE
    
    context = {
        'prodotti': prodotti,
        'categorie': categorie,
        'search_query': search_query,
        'categoria_selected': categoria,
        'prezzo_min': prezzo_min,
        'prezzo_max': prezzo_max,
        'ordine_selected': ordine,
        'total_prodotti': prodotti.count()
    }
    
    return render(request, 'prodotti/prodotti_list.html', context)

def detail(request, product_id):
    """Vista per il dettaglio di un singolo prodotto"""
    
    # Recupera il prodotto specifico o restituisce 404
    prodotto = get_object_or_404(Prodotto, id=product_id)
    
    # Calcola prezzo scontato e risparmio se presente
    if prodotto.sconto > 0:
        prodotto.prezzo_scontato = prodotto.prezzo * (100 - prodotto.sconto) / 100
        prodotto.risparmio = prodotto.prezzo - prodotto.prezzo_scontato
    else:
        prodotto.prezzo_scontato = prodotto.prezzo
        prodotto.risparmio = 0
    
    # Per il futuro sistema di raccomandazioni - ora vuoto
    prodotti_raccomandati = []
    
    context = {
        'prodotto': prodotto,
        'prodotti_raccomandati': prodotti_raccomandati,
    }
    
    return render(request, 'prodotti/product_detail.html', context)
