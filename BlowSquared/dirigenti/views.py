from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Dirigente
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from prodotti.models import Prodotto
from dipendenti.models import Dipendente
from carrello.models import Ordine
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.http import JsonResponse

def login_dirigente(request):
    if request.user.is_authenticated and hasattr(request.user, 'dirigente'):
        return redirect('dirigenti:dashboard')
    
    error = None
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')
        
        # Prova prima con username diretto
        user = authenticate(request, username=email_or_username, password=password)
        
        # Se non funziona, prova a cercare l'utente per email e usa il suo username
        if user is None:
            from django.contrib.auth.models import User
            try:
                user_by_email = User.objects.get(email=email_or_username)
                user = authenticate(request, username=user_by_email.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            # Verifica se ha il profilo dirigente
            if hasattr(user, 'dirigente'):
                login(request, user)
                messages.success(request, f'Benvenuto, {user.dirigente.nome_completo}!')
                return redirect('dirigenti:dashboard')
            else:
                error = "Questo utente non è un dirigente."
        else:
            error = "Credenziali non valide."
    
    return render(request, 'dirigenti/login.html', {'error': error})

@login_required
def dashboard_dirigente(request):
    dirigente = get_object_or_404(Dirigente, user=request.user)
    
    # PER DIRIGENTI: Solo il negozio principale (associazione 1-1)
    negozio_principale = dirigente.negozio_principale
    
    # Statistiche specifiche per il negozio del dirigente
    # Calcolo prodotti: specifici del negozio + prodotti comuni (senza negozi associati)
    prodotti_negozio = Prodotto.objects.filter(negozi=negozio_principale)
    prodotti_comuni = Prodotto.objects.filter(negozi__isnull=True)
    prodotti_totali_count = (prodotti_negozio | prodotti_comuni).distinct().count()
    
    stats = {
        'negozi_gestiti': 1,  # Solo il negozio principale
        'dipendenti_totali': Dipendente.objects.filter(negozio=negozio_principale).count(),
        'prodotti_totali': prodotti_totali_count,
    }
    
    # Statistiche vendite (ultimi 30 giorni) - SOLO per il negozio del dirigente
    data_inizio = timezone.now() - timedelta(days=30)
    ordini_recenti = Ordine.objects.filter(
        negozio=negozio_principale,
        data_ordine__gte=data_inizio
    )
    
    stats['ordini_mese'] = ordini_recenti.count()
    stats['fatturato_mese'] = ordini_recenti.aggregate(Sum('totale_finale'))['totale_finale__sum'] or 0
    
    # Ottieni il parametro per i giorni (default 7)
    giorni = int(request.GET.get('giorni', 7))
    
    # Dati per grafici - Vendite per giorno (configurabile: 7 o 30 giorni)
    vendite_giornaliere = []
    labels_giorni = []
    
    for i in range(giorni-1, -1, -1):  # Ultimi X giorni
        giorno = timezone.now().date() - timedelta(days=i)
        ordini_giorno = Ordine.objects.filter(
            negozio=negozio_principale,
            data_ordine__date=giorno
        )
        
        fatturato_giorno = ordini_giorno.aggregate(Sum('totale_finale'))['totale_finale__sum'] or 0
        vendite_giornaliere.append(float(fatturato_giorno))
        labels_giorni.append(giorno.strftime('%d/%m'))
    
    # Prodotti più venduti (SOLO per il negozio del dirigente + prodotti comuni)
    from django.db.models import F
    try:
        # Unisce prodotti specifici del negozio + prodotti comuni
        prodotti_accessibili = (prodotti_negozio | prodotti_comuni).distinct()
        prodotti_top = prodotti_accessibili.annotate(
            vendite_totali=Count('dettaglioordine')
        ).order_by('-vendite_totali')[:5]
    except:
        prodotti_top = (prodotti_negozio | prodotti_comuni).distinct()[:5]
    
    # Prepara i dati per il template
    charts_data = {
        'vendite_giornaliere': {
            'labels': labels_giorni,
            'data': vendite_giornaliere
        }
    }
    
    context = {
        'dirigente': dirigente,
        'stats': stats,
        'charts_data': json.dumps(charts_data),
        'negozio_gestito': negozio_principale,  # Solo il negozio principale
        'prodotti_top': prodotti_top,
        'ordini_recenti': ordini_recenti.order_by('-data_ordine')[:10],
        'giorni_selezionati': giorni,
    }
    
    return render(request, 'dirigenti/dashboard.html', context)

@login_required
def gestione_negozi(request):
    dirigente = get_object_or_404(Dirigente, user=request.user)
    negozi_accessibili = dirigente.get_negozi_accessibili()
    
    context = {
        'dirigente': dirigente,
        'negozi': negozi_accessibili,
    }
    
    return render(request, 'dirigenti/gestione_negozi.html', context)

@login_required
def gestione_dipendenti(request):
    dirigente = get_object_or_404(Dirigente, user=request.user)
    
    if not dirigente.can_manage_dipendenti():
        messages.error(request, 'Non hai i permessi per gestire i dipendenti.')
        return redirect('dirigenti:dashboard')
    
    negozi_accessibili = dirigente.get_negozi_accessibili()
    dipendenti = Dipendente.objects.filter(negozio__in=negozi_accessibili)
    
    context = {
        'dirigente': dirigente,
        'dipendenti': dipendenti,
        'negozi': negozi_accessibili,
    }
    
    return render(request, 'dirigenti/gestione_dipendenti.html', context)

@login_required
def statistiche(request):
    dirigente = get_object_or_404(Dirigente, user=request.user)
    
    if not dirigente.can_view_financials():
        messages.error(request, 'Non hai i permessi per visualizzare le statistiche finanziarie.')
        return redirect('dirigenti:dashboard')
    
    context = {
        'dirigente': dirigente,
    }
    
    return render(request, 'dirigenti/statistiche.html', context)

@login_required
def gestione_prodotti(request):
    dirigente = get_object_or_404(Dirigente, user=request.user)
    negozi_accessibili = dirigente.get_negozi_accessibili()
    
    # Prodotti accessibili ai negozi gestiti
    prodotti = Prodotto.objects.filter(negozi__in=negozi_accessibili).distinct()
    
    context = {
        'dirigente': dirigente,
        'prodotti': prodotti,
        'negozi': negozi_accessibili,
    }
    
    return render(request, 'dirigenti/gestione_prodotti.html', context)

@login_required
def ajax_vendite_periodo(request):
    """Vista AJAX per aggiornare il grafico delle vendite con periodo dinamico"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Richiesta non valida'}, status=400)
    
    dirigente = get_object_or_404(Dirigente, user=request.user)
    negozio_principale = dirigente.negozio_principale
    
    giorni = int(request.GET.get('giorni', 7))
    if giorni not in [7, 30]:
        giorni = 7  # Default
    
    # Dati per grafici - Vendite per giorno
    vendite_giornaliere = []
    labels_giorni = []
    
    for i in range(giorni-1, -1, -1):
        giorno = timezone.now().date() - timedelta(days=i)
        ordini_giorno = Ordine.objects.filter(
            negozio=negozio_principale,
            data_ordine__date=giorno
        )
        
        fatturato_giorno = ordini_giorno.aggregate(Sum('totale_finale'))['totale_finale__sum'] or 0
        vendite_giornaliere.append(float(fatturato_giorno))
        
        if giorni == 7:
            labels_giorni.append(giorno.strftime('%d/%m'))
        else:  # 30 giorni
            labels_giorni.append(giorno.strftime('%d/%m'))
    
    return JsonResponse({
        'labels': labels_giorni,
        'data': vendite_giornaliere,
        'periodo': f'{giorni} giorni'
    })
