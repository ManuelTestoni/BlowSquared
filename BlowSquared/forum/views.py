from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
import json
from negozi.models import Negozio
from prodotti.models import Prodotto
from .models import MessaggioForum

#VIew che ci permette di redirectare chi non ha i permerssi necessari
def dipendente_non_allowed(view_func):
    """
    Decorator che blocca l'accesso ai dipendenti e dirigenti mostrando la pagina 404.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (hasattr(request.user, 'dipendente') or hasattr(request.user, 'dirigente')):
            return render(request, '404.html', status=404)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@dipendente_non_allowed
@login_required
def forum_home(request):
    """Vista principale del forum"""
    context = {
        'user': request.user,
    }
    return render(request, 'forum/forum.html', context)

@login_required 
def api_negozi(request):
    """API per ricerca negozi"""
    query = request.GET.get('q', '')
    
    negozi = Negozio.objects.filter(
        Q(nome__icontains=query) | Q(citta__icontains=query)
    )[:10]
    
    results = [{
        'id': negozio.id,
        'nome': negozio.nome,
        'citta': negozio.citta,
        'indirizzo': negozio.indirizzo_completo,
    } for negozio in negozi]
    
    return JsonResponse({'negozi': results})

@login_required
def api_prodotti(request):
    """API per ricerca prodotti per ricette"""
    query = request.GET.get('q', '')
    
    prodotti = Prodotto.objects.filter(
        Q(nome__icontains=query) | Q(marca__icontains=query)
    ).distinct()[:15]
    
    results = [{
        'id': prodotto.id,
        'nome': prodotto.nome,
        'marca': prodotto.marca,
        'categoria': prodotto.get_categoria_display(),
        'prezzo': str(prodotto.prezzo),
        'peso': prodotto.peso,
    } for prodotto in prodotti]
    
    return JsonResponse({'prodotti': results})

@login_required
def api_messaggi_recenti(request):
    """API per caricare messaggi recenti"""
    messaggi = MessaggioForum.objects.select_related(
        'autore', 'negozio_recensito'
    ).order_by('-data_creazione')[:20]
    
    results = [msg.to_dict() for msg in reversed(messaggi)]
    
    return JsonResponse({
        'success': True,
        'messaggi': results
    })

@login_required
def api_invia_messaggio(request):
    """API per inviare nuovo messaggio"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metodo non permesso'})
    
    try:
        data = json.loads(request.body)
        tipo = data.get('tipo', 'chat')
        
        messaggio_data = {
            'autore': request.user,
            'tipo': tipo,
        }
        
        if tipo == 'chat':
            messaggio_data['contenuto'] = data.get('contenuto', '')
            
        elif tipo == 'recensione':
            messaggio_data['contenuto'] = data.get('contenuto', '')
            if data.get('negozio_id'):
                try:
                    negozio = Negozio.objects.get(id=data['negozio_id'])
                    messaggio_data['negozio_recensito'] = negozio
                except Negozio.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Negozio non trovato'})
            messaggio_data['stelle'] = data.get('stelle', 5)
            
        elif tipo == 'ricetta':
            nome_ricetta = data.get('nome_ricetta', '')
            ingredienti = data.get('ingredienti', [])
            note_ricetta = data.get('note_ricetta', '')
            
            # Genera automaticamente il contenuto per le ricette
            ingredienti_nomi = []
            for ing in ingredienti:
                try:
                    prodotto = Prodotto.objects.get(id=ing['prodotto_id'])
                    ingredienti_nomi.append(f"{prodotto.nome} ({ing.get('quantita', '1')})")
                except Prodotto.DoesNotExist:
                    continue
            
            contenuto_auto = f"🍝 Condivide la ricetta: {nome_ricetta}"
            if ingredienti_nomi:
                contenuto_auto += f"\n📝 Ingredienti: {', '.join(ingredienti_nomi[:3])}"
                if len(ingredienti_nomi) > 3:
                    contenuto_auto += f" e altri {len(ingredienti_nomi) - 3}..."
            
            messaggio_data['contenuto'] = contenuto_auto
            messaggio_data['nome_ricetta'] = nome_ricetta
            messaggio_data['ingredienti_ricetta'] = ingredienti
            messaggio_data['note_ricetta'] = note_ricetta
        
        # Validazione contenuto
        if not messaggio_data.get('contenuto') or messaggio_data['contenuto'].strip() == '':
            return JsonResponse({'success': False, 'error': 'Contenuto del messaggio richiesto'})
        
        messaggio = MessaggioForum.objects.create(**messaggio_data)
        
        return JsonResponse({
            'success': True,
            'messaggio': messaggio.to_dict()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dati JSON non validi'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Errore server: {str(e)}'})
