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
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
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
    
    # Ottieni i negozi accessibili
    negozi_accessibili = dirigente.get_negozi_accessibili()
    
    # Statistiche generali
    stats = {
        'negozi_gestiti': negozi_accessibili.count(),
        'dipendenti_totali': Dipendente.objects.filter(negozio__in=negozi_accessibili).count(),
        'prodotti_totali': Prodotto.objects.filter(negozi__in=negozi_accessibili).distinct().count(),
    }
    
    # Statistiche vendite (ultimi 30 giorni)
    data_inizio = timezone.now() - timedelta(days=30)
    ordini_recenti = Ordine.objects.filter(
        negozio__in=negozi_accessibili,
        data_ordine__gte=data_inizio
    )
    
    stats['ordini_mese'] = ordini_recenti.count()
    stats['fatturato_mese'] = ordini_recenti.aggregate(Sum('totale_finale'))['totale_finale__sum'] or 0
    
    # Dati per grafici - Vendite per giorno (ultimi 7 giorni)
    vendite_giornaliere = []
    labels_giorni = []
    
    for i in range(6, -1, -1):  # Ultimi 7 giorni
        giorno = timezone.now().date() - timedelta(days=i)
        ordini_giorno = Ordine.objects.filter(
            negozio__in=negozi_accessibili,
            data_ordine__date=giorno
        )
        
        fatturato_giorno = ordini_giorno.aggregate(Sum('totale_finale'))['totale_finale__sum'] or 0
        vendite_giornaliere.append(float(fatturato_giorno))
        labels_giorni.append(giorno.strftime('%d/%m'))
    
    # Dati per grafico - Vendite per negozio
    vendite_per_negozio = []
    labels_negozi = []
    
    for negozio in negozi_accessibili:
        fatturato_negozio = Ordine.objects.filter(
            negozio=negozio,
            data_ordine__gte=data_inizio
        ).aggregate(Sum('totale_finale'))['totale_finale__sum'] or 0
        
        vendite_per_negozio.append(float(fatturato_negozio))
        labels_negozi.append(negozio.nome.split()[-1])  # Solo l'ultima parola del nome
    
    # Prodotti più venduti
    from django.db.models import F
    try:
        prodotti_top = Prodotto.objects.filter(
            negozi__in=negozi_accessibili
        ).annotate(
            vendite_totali=Count('dettaglioordine')
        ).order_by('-vendite_totali')[:5]
    except:
        prodotti_top = Prodotto.objects.filter(negozi__in=negozi_accessibili)[:5]
    
    # Prepara i dati per il template
    charts_data = {
        'vendite_giornaliere': {
            'labels': labels_giorni,
            'data': vendite_giornaliere
        },
        'vendite_per_negozio': {
            'labels': labels_negozi,
            'data': vendite_per_negozio
        }
    }
    
    context = {
        'dirigente': dirigente,
        'stats': stats,
        'charts_data': json.dumps(charts_data),
        'negozi_gestiti': negozi_accessibili,
        'prodotti_top': prodotti_top,
        'ordini_recenti': ordini_recenti.order_by('-data_ordine')[:10],
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
