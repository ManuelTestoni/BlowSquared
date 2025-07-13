from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from .models import Prodotto
from decimal import Decimal

def list(request):
    """Vista per la lista di tutti i prodotti con filtri e ricerca"""
    
    # Per gli utenti autenticati, filtra per negozio preferito
    try:
        profilo = request.user.profilo
        if not profilo.negozio_preferito:
            messages.info(request, 'Seleziona un negozio per vedere i prodotti disponibili.')
            return redirect('negozi:seleziona_negozio')
        
        # Filtra prodotti in base al negozio selezionato - LOGICA UNIFICATA
        negozio_preferito = profilo.negozio_preferito
        
        # METODO UNIFICATO: Usa la stessa logica della vista dipendenti
        # Metodo 1: Prodotti specifici del negozio
        prodotti_negozio = Prodotto.objects.filter(negozi=negozio_preferito)
        
        # Metodo 2: Prodotti senza negozi associati (prodotti comuni)
        prodotti_comuni = Prodotto.objects.filter(negozi__isnull=True)
        
        # Unione dei due QuerySet - solo prodotti con stock > 0
        prodotti = (prodotti_negozio | prodotti_comuni).filter(stock__gt=0).distinct()
        
    except Exception as e:
        # Se non ha un profilo o ci sono errori, redirigi alla selezione negozio
        messages.info(request, 'Completa il tuo profilo selezionando un negozio.')
        return redirect('negozi:seleziona_negozio')
    
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
    
    # Il prezzo scontato è già disponibile come proprietà del modello
    
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
    prodotto = get_object_or_404(Prodotto, id=product_id)
    
    # Il prezzo scontato è già disponibile come proprietà del modello
    
    # Verifica se l'utente può vedere questo prodotto nel suo negozio - LOGICA UNIFICATA
    if request.user.is_authenticated:
        try:
            profilo = request.user.profilo
            if profilo.negozio_preferito:
                negozio_preferito = profilo.negozio_preferito
                
                # CONTROLLO UNIFICATO: Verifica se il prodotto è associato al negozio
                prodotto_disponibile = (
                    # Prodotto specifico del negozio
                    prodotto.negozi.filter(id=negozio_preferito.id).exists() or
                    # Prodotto comune (senza negozi associati)
                    not prodotto.negozi.exists()
                )
                
                if not prodotto_disponibile:
                    messages.warning(request, 'Questo prodotto non è disponibile nel tuo negozio.')
                elif prodotto.stock <= 0:
                    messages.warning(request, 'Questo prodotto non è attualmente disponibile (esaurito).')
        except:
            pass
    
    context = {
        'prodotto': prodotto
    }
    
    return render(request, 'prodotti/product_detail.html', context)


def list_prodotti(request):
    """Vista alternativa per lista prodotti senza autenticazione richiesta"""
    # Ottieni tutti i prodotti
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
    
    # Il prezzo scontato è già disponibile come proprietà del modello
    
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
