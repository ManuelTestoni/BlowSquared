from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from functools import wraps
from .models import Prodotto
from decimal import Decimal
from negozi.models import Negozio


#Controlliamo che le persone che visualizzano alle pagine abbiano i permessi giusti. 
def dipendente_non_allowed(view_func):
    """
    Decorator che blocca l'accesso ai dipendenti mostrando la pagina 404.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (hasattr(request.user, 'dipendente') or hasattr(request.user, 'dirigente')):
            return render(request, '404.html', status=404)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@dipendente_non_allowed
def list(request):
    """Vista per la lista di tutti i prodotti con filtri e ricerca"""
    
    negozio_selezionato = None
    
    # Per gli utenti autenticati, filtra per negozio preferito
    if request.user.is_authenticated:
        try:
            profilo = request.user.profilo
            if not profilo.negozio_preferito:
                messages.info(request, 'Seleziona un negozio per vedere i prodotti disponibili.')
                return redirect('negozi:seleziona_negozio')
            negozio_selezionato = profilo.negozio_preferito
        except:
            # Se non ha un profilo o ci sono errori, redirigi alla selezione negozio
            messages.info(request, 'Completa il tuo profilo selezionando un negozio.')
            return redirect('negozi:seleziona_negozio')
    else:
        # Per gli utenti non autenticati, verifica se hanno selezionato un negozio temporaneo
        negozio_temporaneo_id = request.session.get('negozio_temporaneo_id')
        if negozio_temporaneo_id:
            try:
                
                negozio_selezionato = Negozio.objects.get(id=negozio_temporaneo_id, attivo=True)
            except Negozio.DoesNotExist:
                # Il negozio temporaneo non è più valido
                del request.session['negozio_temporaneo_id']
                if 'negozio_temporaneo_nome' in request.session:
                    del request.session['negozio_temporaneo_nome']
        
        if not negozio_selezionato:
            messages.info(request, 'Seleziona un negozio per vedere i prodotti disponibili.')
            return redirect('negozi:seleziona_negozio')
    
    # Filtra prodotti in base al negozio selezionato
    # Metodo 1: Prodotti specifici del negozio
    prodotti_negozio = Prodotto.objects.filter(negozi=negozio_selezionato)
    
    # Metodo 2: Prodotti senza negozi associati (prodotti comuni)
    prodotti_comuni = Prodotto.objects.filter(negozi__isnull=True)
    
    # Unione dei due QuerySet - solo prodotti con stock > 0
    prodotti = (prodotti_negozio | prodotti_comuni).filter(stock__gt=0).distinct()
    
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
        'negozio_selezionato': negozio_selezionato,
        'categorie': categorie,
        'search_query': search_query,
        'categoria_selected': categoria,
        'prezzo_min': prezzo_min,
        'prezzo_max': prezzo_max,
        'ordine_selected': ordine,
        'total_prodotti': prodotti.count()
    }
    
    return render(request, 'prodotti/prodotti_list.html', context)


@dipendente_non_allowed
def detail(request, product_id):
    """Vista per il dettaglio di un singolo prodotto"""
    prodotto = get_object_or_404(Prodotto, id=product_id)
    
    # Verifica se l'utente può vedere questo prodotto nel suo negozio
    negozio_selezionato = None
    
    if request.user.is_authenticated:
        try:
            profilo = request.user.profilo
            if profilo.negozio_preferito:
                negozio_selezionato = profilo.negozio_preferito
        except:
            pass
    else:
        # Per gli utenti non autenticati, verifica se hanno selezionato un negozio temporaneo
        negozio_temporaneo_id = request.session.get('negozio_temporaneo_id')
        if negozio_temporaneo_id:
            try:
                from negozi.models import Negozio
                negozio_selezionato = Negozio.objects.get(id=negozio_temporaneo_id, attivo=True)
            except Negozio.DoesNotExist:
                pass
    
    # Verifica disponibilità del prodotto nel negozio selezionato
    if negozio_selezionato:
        #Verifica se il prodotto è associato al negozio
        prodotto_disponibile = (
            # Prodotto specifico del negozio
            prodotto.negozi.filter(id=negozio_selezionato.id).exists() or
            # Prodotto comune (senza negozi associati)
            not prodotto.negozi.exists()
        )
        
        if not prodotto_disponibile:
            messages.warning(request, 'Questo prodotto non è disponibile nel negozio selezionato.')
        elif prodotto.stock <= 0:
            messages.warning(request, 'Questo prodotto non è attualmente disponibile (esaurito).')
    
    context = {
        'prodotto': prodotto,
        'negozio_selezionato': negozio_selezionato
    }
    
    return render(request, 'prodotti/product_detail.html', context)
