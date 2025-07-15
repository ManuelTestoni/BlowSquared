from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import Negozio, DisponibilitaProdotto
import datetime


#Come prima ci assicuriamo che i dipendenti e dirigeti non vedano queste pagine del sito.
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
def lista_negozi(request):
    """Vista per la lista dei negozi"""
    negozi = Negozio.objects.filter(attivo=True).order_by('provincia', 'citta', 'nome')
    
    context = {
        'negozi': negozi,
    }
    return render(request, 'negozi/seleziona_negozio.html', context)

@dipendente_non_allowed
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
        negozio_precedente = profilo.negozio_preferito
        
        # Se l'utente sta cambiando negozio e ha elementi nel carrello
        if negozio_precedente and negozio_precedente != negozio:
            from carrello.models import Carrello
            
            # Verifica se ha un carrello con elementi
            try:
                carrello = Carrello.objects.get(utente=request.user)
                if carrello.elementi.exists():
                    # Se non ha confermato lo svuotamento, chiedi conferma
                    conferma = request.POST.get('conferma_svuotamento')
                    if not conferma:
                        context = {
                            'negozio_corrente': negozio_precedente,
                            'negozio_nuovo': negozio,
                            'elementi_carrello': carrello.elementi.count(),
                            'quantita_totale': carrello.numero_articoli,
                            'subtotale': carrello.subtotale,
                        }
                        return render(request, 'negozi/conferma_cambio_negozio.html', context)
                    
                    # Se ha confermato, svuota il carrello
                    # Questa logica ci serve perchè ogni negozio ha un carosello di prodotti differente.
                    # Permettere all'utente di comprare un prodotto da un negozio e un prodotto da un altro
                    # non è uno scenario fattibile nella vita reale, dato che dovrebbero partire due ordini in base alle
                    # disponibilità dei magazzini.
                    if conferma == 'si':
                        carrello.svuota_carrello()
                        messages.warning(request, f'Il carrello è stato svuotato per il cambio da "{negozio_precedente.nome}" a "{negozio.nome}".')
                    elif conferma == 'no':
                        messages.info(request, 'Cambio negozio annullato. Il carrello è rimasto invariato.')
                        return redirect('negozi:seleziona_negozio')
                        
            except Carrello.DoesNotExist:
                # L'utente non ha ancora un carrello, continua normalmente
                pass
        
        # Imposta il nuovo negozio
        profilo.negozio_preferito = negozio
        profilo.save()
        
        if negozio_precedente and negozio_precedente != negozio:
            messages.success(request, f'Hai cambiato negozio da "{negozio_precedente.nome}" a "{negozio.nome}"!')
        else:
            messages.success(request, f'Hai selezionato "{negozio.nome}" come tuo negozio preferito!')
            
        return redirect('prodotti:list')
        
    except Exception as e:
        messages.error(request, f'Errore nella selezione del negozio: {str(e)}')
        return redirect('negozi:seleziona_negozio')

@dipendente_non_allowed
def seleziona_negozio_temporaneo(request, negozio_id):
    """Vista per selezionare temporaneamente un negozio per utenti non autenticati"""
    negozio = get_object_or_404(Negozio, id=negozio_id, attivo=True)
    
    # Se l'utente è autenticato, reindirizza alla selezione normale
    if request.user.is_authenticated:
        return redirect('negozi:seleziona_preferito', negozio_id=negozio_id)
    
    # Salva il negozio selezionato nella sessione
    request.session['negozio_temporaneo_id'] = negozio.id
    request.session['negozio_temporaneo_nome'] = negozio.nome
    
    # Reindirizza alla lista prodotti
    messages.success(request, f'Hai selezionato "{negozio.nome}" per la navigazione. Registrati per salvare la tua scelta!')
    return redirect('prodotti:list')

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
    oggi_index = datetime.date.today().weekday()
    oggi_nome = list(giorni_settimana.values())[oggi_index]
    
    context = {
        'negozio': negozio,
        'prodotti_disponibili': prodotti_disponibili,
        'orari_formattati': orari_formattati,
        'oggi': oggi_nome,
    }
    
    return render(request, 'negozi/dettaglio_completo.html', context)
