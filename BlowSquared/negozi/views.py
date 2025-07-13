from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Negozio, DisponibilitaProdotto

def index(request):
    return render(request, 'negozi/index.html')

def lista_negozi(request):
    """Vista per la lista dei negozi"""
    negozi = Negozio.objects.filter(attivo=True).order_by('provincia', 'citta', 'nome')
    
    context = {
        'negozi': negozi,
    }
    return render(request, 'negozi/seleziona_negozio.html', context)

def seleziona_negozio(request):
    """Vista per la selezione del negozio preferito"""
    # Recupera TUTTI i negozi attivi
    tutti_negozi = Negozio.objects.filter(attivo=True).order_by('provincia', 'citta', 'nome')
    
    provincia_utente = None
    citta_utente = None
    negozi_consigliati = []
    altri_negozi = []
    
    if request.user.is_authenticated:
        try:
            profilo = request.user.profilo
            provincia_utente = profilo.provincia
            citta_utente = profilo.citta
            
            # Separa negozi consigliati da altri negozi
            for negozio in tutti_negozi:
                if provincia_utente and negozio.provincia == provincia_utente:
                    # Priorità: stessa città, poi stessa provincia
                    if citta_utente and citta_utente.lower() in negozio.citta.lower():
                        negozio.is_same_city = True
                        negozio.is_recommended = True
                        negozi_consigliati.insert(0, negozio)  # In cima
                    else:
                        negozio.is_same_city = False
                        negozio.is_recommended = True
                        negozi_consigliati.append(negozio)
                else:
                    negozio.is_same_city = False
                    negozio.is_recommended = False
                    altri_negozi.append(negozio)
        except:
            # Se non ha profilo, tutti i negozi sono "altri"
            altri_negozi = list(tutti_negozi)
            for negozio in altri_negozi:
                negozio.is_same_city = False
                negozio.is_recommended = False
    else:
        # Utente non autenticato - tutti i negozi sono "altri"
        altri_negozi = list(tutti_negozi)
        for negozio in altri_negozi:
            negozio.is_same_city = False
            negozio.is_recommended = False
    
    context = {
        'negozi_consigliati': negozi_consigliati,
        'altri_negozi': altri_negozi,
        'provincia_utente': provincia_utente,
        'citta_utente': citta_utente,
        'total_negozi': len(negozi_consigliati) + len(altri_negozi),
    }
    return render(request, 'negozi/seleziona_negozio.html', context)

def dettaglio_negozio(request, negozio_id):
    """Vista AJAX per il dettaglio di un negozio"""
    negozio = get_object_or_404(Negozio, id=negozio_id, attivo=True)
    
    # Calcola statistiche del negozio
    prodotti_disponibili = DisponibilitaProdotto.objects.filter(
        negozio=negozio,
        quantita_disponibile__gt=0
    ).count()
    
    # Prepara orari formattati
    orari_formattati = {}
    giorni_settimana = {
        'lunedi': 'Lunedì',
        'martedi': 'Martedì', 
        'mercoledi': 'Mercoledì',
        'giovedi': 'Giovedì',
        'venerdi': 'Venerdì',
        'sabato': 'Sabato',
        'domenica': 'Domenica'
    }
    
    for giorno_key, giorno_nome in giorni_settimana.items():
        orario = negozio.orari_apertura.get(giorno_key, 'Chiuso')
        orari_formattati[giorno_nome] = orario
    
    # Servizi disponibili
    servizi = []
    if negozio.servizio_farmacia:
        servizi.append({'nome': 'Farmacia', 'icona': '💊'})
    if negozio.servizio_panetteria:
        servizi.append({'nome': 'Panetteria', 'icona': '🍞'})
    if negozio.servizio_macelleria:
        servizi.append({'nome': 'Macelleria', 'icona': '🥩'})
    if negozio.servizio_pescheria:
        servizi.append({'nome': 'Pescheria', 'icona': '🐟'})
    if negozio.servizio_consegna_domicilio:
        servizi.append({'nome': 'Consegna a Domicilio', 'icona': '🚚'})
    if negozio.ritiro_click_collect:
        servizi.append({'nome': 'Click & Collect', 'icona': '📦'})
    
    return JsonResponse({
        'success': True,
        'negozio': {
            'id': negozio.id,
            'nome': negozio.nome,
            'codice': negozio.codice_negozio,
            'indirizzo_completo': negozio.indirizzo_completo,
            'telefono': negozio.telefono,
            'email': negozio.email,
            'superficie_mq': negozio.superficie_mq,
            'numero_casse': negozio.numero_casse,
            'posti_parcheggio': negozio.posti_parcheggio,
            'direttore': negozio.direttore,
            'data_apertura': negozio.data_apertura.strftime('%d/%m/%Y'),
            'prodotti_disponibili': prodotti_disponibili,
            'orari': orari_formattati,
            'servizi': servizi
        }
    })

@login_required
def seleziona_negozio_preferito(request, negozio_id):
    """Vista per impostare il negozio preferito dell'utente"""
    negozio = get_object_or_404(Negozio, id=negozio_id, attivo=True)
    
    try:
        profilo = request.user.profilo
        profilo.negozio_preferito = negozio
        profilo.save()
        
        messages.success(request, f'Hai selezionato "{negozio.nome}" come tuo negozio preferito!')
        return redirect('prodotti:list')
    except:
        messages.error(request, 'Errore nella selezione del negozio.')
        return redirect('negozi:seleziona_negozio')

def cerca_negozi_vicini(request):
    """API per cercare negozi nelle vicinanze di una posizione"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    raggio = float(request.GET.get('raggio', 20))  # Default 20km
    
    if not lat or not lng:
        return JsonResponse({'error': 'Coordinate mancanti'}, status=400)
    
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return JsonResponse({'error': 'Coordinate non valide'}, status=400)
    
    negozi = Negozio.objects.filter(attivo=True)
    negozi_vicini = []
    
    for negozio in negozi:
        distanza = negozio.distanza_da(lat, lng)
        if distanza <= raggio:
            negozi_vicini.append({
                'id': negozio.id,
                'nome': negozio.nome,
                'indirizzo': negozio.indirizzo_completo,
                'distanza': round(distanza, 2),
                'coordinate': negozio.coordinate,
                'telefono': negozio.telefono,
                'servizi': {
                    'consegna': negozio.servizio_consegna_domicilio,
                    'click_collect': negozio.ritiro_click_collect,
                    'farmacia': negozio.servizio_farmacia,
                    'panetteria': negozio.servizio_panetteria,
                }
            })
    
    # Ordina per distanza
    negozi_vicini.sort(key=lambda x: x['distanza'])
    
    return JsonResponse({
        'negozi': negozi_vicini,
        'count': len(negozi_vicini)
    })

def dettaglio_completo_negozio(request, negozio_id):
    """Vista per la pagina completa di dettaglio negozio"""
    negozio = get_object_or_404(Negozio, id=negozio_id, attivo=True)
    
    # Calcola prodotti disponibili
    prodotti_disponibili = DisponibilitaProdotto.objects.filter(
        negozio=negozio,
        quantita_disponibile__gt=0
    ).count()
    
    # Prepara orari formattati
    orari_formattati = {}
    giorni_settimana = {
        'lunedi': 'Lunedì',
        'martedi': 'Martedì', 
        'mercoledi': 'Mercoledì',
        'giovedi': 'Giovedì',
        'venerdi': 'Venerdì',
        'sabato': 'Sabato',
        'domenica': 'Domenica'
    }
    
    for giorno_key, giorno_nome in giorni_settimana.items():
        orario = negozio.orari_apertura.get(giorno_key, 'Chiuso')
        orari_formattati[giorno_nome] = orario
    
    # Determina il giorno di oggi
    import datetime
    oggi_index = datetime.date.today().weekday()
    oggi_nome = list(giorni_settimana.values())[oggi_index]
    
    context = {
        'negozio': negozio,
        'prodotti_disponibili': prodotti_disponibili,
        'orari_formattati': orari_formattati,
        'oggi': oggi_nome,
    }
    
    return render(request, 'negozi/dettaglio_completo.html', context)
