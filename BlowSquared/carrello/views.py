from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from functools import wraps
from .models import Carrello, ElementoCarrello, Ordine, ElementoOrdine
from prodotti.models import Prodotto


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
def visualizza_carrello(request):
    """Vista per visualizzare il contenuto del carrello"""
    
    # Se l'utente non è autenticato, reindirizza alla registrazione
    if not request.user.is_authenticated:
        messages.info(request, 'Registrati o accedi per vedere il tuo carrello.')
        return redirect('utenti:signup')
    
    # Verifica che l'utente abbia selezionato un negozio
    try:
        profilo = request.user.profilo
        if not profilo.negozio_preferito:
            messages.info(request, 'Seleziona prima il tuo negozio preferito per vedere il carrello.')
            return redirect('negozi:seleziona_negozio')
    except:
        messages.info(request, 'Completa il tuo profilo selezionando un negozio.')
        return redirect('negozi:seleziona_negozio')
    
    # Ottieni o crea il carrello dell'utente
    carrello = Carrello.get_or_create_for_user(request.user)
    
    # Recupera gli elementi del carrello con query JOIN per ottimizzare
    elementi_carrello = ElementoCarrello.objects.filter(carrello=carrello).select_related('prodotto').order_by('-data_aggiunta')
    
    # Prepara i dati per il template
    carrello_data = []
    for elemento in elementi_carrello:
        carrello_data.append({
            'id': elemento.id,
            'prodotto_id': elemento.prodotto.id,
            'nome': elemento.prodotto.nome,
            'marca': elemento.prodotto.marca,
            'categoria': elemento.prodotto.get_categoria_display(),
            'prezzo_unitario': elemento.prezzo_unitario_scontato,
            'prezzo_originale': elemento.prezzo_unitario,
            'quantita': elemento.quantita,
            'prezzo_totale': elemento.prezzo_totale,
            'sconto_applicato': elemento.sconto_applicato,
            'risparmio_totale': elemento.risparmio_totale,
            'foto': elemento.prodotto.foto.url if elemento.prodotto.foto else None,
            'peso': elemento.prodotto.peso,
            'data_aggiunta': elemento.data_aggiunta,
        })
    
    # Calcola totali usando le properties del modello
    totale_prodotti = carrello.numero_prodotti_unici
    totale_quantita = carrello.numero_articoli
    subtotale = carrello.subtotale
    costo_spedizione = carrello.spese_spedizione
    totale_finale = carrello.totale_finale
    
    # Soglia spedizione gratuita
    soglia_spedizione_gratuita = 30.00
    
    context = {
        'carrello': carrello,
        'elementi_carrello': carrello_data,
        'totale_prodotti': totale_prodotti,
        'totale_quantita': totale_quantita,
        'subtotale': subtotale,
        'costo_spedizione': costo_spedizione,
        'soglia_spedizione_gratuita': soglia_spedizione_gratuita,
        'totale_finale': totale_finale,
        'negozio': profilo.negozio_preferito,
    }
    
    return render(request, 'carrello/carrello.html', context)

@dipendente_non_allowed
def aggiungi_al_carrello(request, prodotto_id):
    """Vista per aggiungere un prodotto al carrello"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Metodo non permesso'})
    
    # Controlla se l'utente è autenticato
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Registrati o accedi per aggiungere prodotti al carrello',
            'redirect_login': True
        })
    
    try:
        # Verifica che l'utente abbia un negozio selezionato
        profilo = request.user.profilo
        if not profilo.negozio_preferito:
            return JsonResponse({
                'success': False, 
                'message': 'Seleziona prima un negozio per aggiungere prodotti al carrello'
            })
        
        # Recupera il prodotto
        prodotto = get_object_or_404(Prodotto, id=prodotto_id)
        
        # Verifica che il prodotto sia disponibile nel negozio dell'utente
        from negozi.models import DisponibilitaProdotto
        
        # LOGICA UNIFICATA: Gestisce prodotti specifici del negozio + prodotti comuni
        try:
            # Prova prima a cercare disponibilità specifica per il negozio
            disponibilita = DisponibilitaProdotto.objects.get(
                prodotto=prodotto,
                negozio=profilo.negozio_preferito
            )
            if disponibilita.quantita_disponibile <= 0:
                return JsonResponse({
                    'success': False, 
                    'message': f'Il prodotto "{prodotto.nome}" non è attualmente disponibile'
                })
            stock_disponibile = disponibilita.quantita_disponibile
            
        except DisponibilitaProdotto.DoesNotExist:
            # Verifica se il prodotto è associato al negozio dell'utente
            if prodotto.negozi.filter(id=profilo.negozio_preferito.id).exists():
                # È associato al negozio ma manca il record DisponibilitaProdotto
                # Usa lo stock del prodotto stesso
                if prodotto.stock <= 0:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Il prodotto "{prodotto.nome}" non è attualmente disponibile'
                    })
                stock_disponibile = prodotto.stock
                
            elif not prodotto.negozi.exists():
                # È un prodotto comune - usa lo stock del prodotto stesso
                if prodotto.stock <= 0:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Il prodotto "{prodotto.nome}" non è attualmente disponibile'
                    })
                stock_disponibile = prodotto.stock
            else:
                # È un prodotto specifico di altri negozi, non disponibile qui
                return JsonResponse({
                    'success': False, 
                    'message': f'Il prodotto "{prodotto.nome}" non è disponibile nel tuo negozio'
                })
        
        # Ottieni la quantità dalla richiesta (default 1)
        quantita = int(request.POST.get('quantita', 1))
        
        if quantita <= 0 or quantita > 99:
            return JsonResponse({'success': False, 'message': 'Quantità non valida'})
        
        # Ottieni o crea il carrello per verificare la quantità già presente
        carrello = Carrello.get_or_create_for_user(request.user)
        
        # Verifica se il prodotto è già nel carrello
        try:
            elemento_esistente = ElementoCarrello.objects.get(carrello=carrello, prodotto=prodotto)
            quantita_gia_presente = elemento_esistente.quantita
        except ElementoCarrello.DoesNotExist:
            quantita_gia_presente = 0
        
        # Calcola la quantità totale che si otterrebbe
        quantita_totale = quantita + quantita_gia_presente
        
        # Verifica che ci sia abbastanza stock considerando anche quello già nel carrello
        if quantita_totale > stock_disponibile:
            return JsonResponse({
                'success': False, 
                'message': f'Non ci sono abbastanza prodotti in magazzino. Disponibili: {stock_disponibile}, già nel carrello: {quantita_gia_presente}'
            })
        
        # Aggiorna il negozio del carrello se necessario
        if carrello.negozio != profilo.negozio_preferito:
            carrello.negozio = profilo.negozio_preferito
            carrello.save()
        
        # Aggiungi il prodotto al carrello
        elemento = carrello.aggiungi_prodotto(prodotto, quantita)
        
        # Messaggio di conferma
        messaggio = f'{prodotto.nome} aggiunto al carrello'
        
        return JsonResponse({
            'success': True, 
            'message': messaggio,
            'carrello_count': carrello.numero_articoli,
            'elemento_id': elemento.id,
            'quantita_totale': elemento.quantita
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Errore nell\'aggiunta al carrello: {str(e)}'
        })

@dipendente_non_allowed
@login_required
def rimuovi_dal_carrello(request, elemento_id):
    """Vista per rimuovere un elemento dal carrello"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Metodo non permesso'})
    
    try:
        carrello = Carrello.get_or_create_for_user(request.user)
        elemento = get_object_or_404(ElementoCarrello, id=elemento_id, carrello=carrello)
        
        prodotto_nome = elemento.prodotto.nome
        elemento.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'{prodotto_nome} rimosso dal carrello',
            'carrello_count': carrello.numero_articoli
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Errore nella rimozione: {str(e)}'
        })

@dipendente_non_allowed
@login_required
def aggiorna_quantita_carrello(request, elemento_id):
    """Vista per aggiornare la quantità di un elemento nel carrello"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Metodo non permesso'})
    
    try:
        carrello = Carrello.get_or_create_for_user(request.user)
        elemento = get_object_or_404(ElementoCarrello, id=elemento_id, carrello=carrello)
        
        nuova_quantita = int(request.POST.get('quantita', 1))
        if nuova_quantita <= 0 or nuova_quantita > 99:
            return JsonResponse({'success': False, 'message': 'Quantità non valida'})
        
        # Verifica disponibilità - LOGICA UNIFICATA
        from negozi.models import DisponibilitaProdotto
        try:
            # Prova prima a cercare disponibilità specifica per il negozio
            disponibilita = DisponibilitaProdotto.objects.get(
                prodotto=elemento.prodotto,
                negozio=carrello.negozio
            )
            
            if nuova_quantita > disponibilita.quantita_disponibile:
                return JsonResponse({
                    'success': False, 
                    'message': f'Disponibili solo {disponibilita.quantita_disponibile} pezzi'
                })
        except DisponibilitaProdotto.DoesNotExist:
            # Verifica se il prodotto è associato al negozio dell'utente
            if elemento.prodotto.negozi.filter(id=carrello.negozio.id).exists():
                # È associato al negozio ma manca il record DisponibilitaProdotto
                # Usa lo stock del prodotto stesso
                if nuova_quantita > elemento.prodotto.stock:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Disponibili solo {elemento.prodotto.stock} pezzi'
                    })
            elif not elemento.prodotto.negozi.exists():
                # È un prodotto comune - usa lo stock del prodotto stesso
                if nuova_quantita > elemento.prodotto.stock:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Disponibili solo {elemento.prodotto.stock} pezzi'
                    })
            else:
                # È un prodotto specifico di altri negozi, non più disponibile qui
                return JsonResponse({'success': False, 'message': 'Prodotto non più disponibile'})
        
        elemento.quantita = nuova_quantita
        elemento.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Quantità aggiornata',
            'carrello_count': carrello.numero_articoli,
            'elemento_prezzo_totale': float(elemento.prezzo_totale),
            'carrello_subtotale': float(carrello.subtotale),
            'carrello_totale': float(carrello.totale_finale)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Errore nell\'aggiornamento: {str(e)}'
        })

@dipendente_non_allowed
@login_required
def svuota_carrello(request):
    """Vista per svuotare completamente il carrello"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Metodo non permesso'})
    
    try:
        carrello = Carrello.get_or_create_for_user(request.user)
        carrello.svuota_carrello()
        
        return JsonResponse({
            'success': True, 
            'message': 'Carrello svuotato',
            'carrello_count': 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Errore nello svuotamento: {str(e)}'
        })

@login_required
def api_cart_count(request):
    """API per ottenere il numero di elementi nel carrello"""
    try:
        carrello = Carrello.get_or_create_for_user(request.user)
        return JsonResponse({
            'success': True,
            'count': carrello.numero_articoli
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'count': 0,
            'error': str(e)
        })

@dipendente_non_allowed
@login_required
def checkout(request):
    """Vista per la pagina di checkout"""
    
    # Verifica che l'utente abbia selezionato un negozio
    try:
        profilo = request.user.profilo
        if not profilo.negozio_preferito:
            messages.info(request, 'Seleziona prima il tuo negozio preferito per procedere al checkout.')
            return redirect('negozi:seleziona_negozio')
    except:
        messages.info(request, 'Completa il tuo profilo selezionando un negozio.')
        return redirect('negozi:seleziona_negozio')
    
    # Ottieni il carrello dell'utente
    carrello = Carrello.get_or_create_for_user(request.user)
    
    # Verifica che il carrello non sia vuoto
    if carrello.is_vuoto:
        messages.warning(request, 'Il tuo carrello è vuoto. Aggiungi dei prodotti prima di procedere al checkout.')
        return redirect('prodotti:list')
    
    # Recupera gli elementi del carrello
    elementi_carrello = ElementoCarrello.objects.filter(carrello=carrello).select_related('prodotto').order_by('-data_aggiunta')
    
    # Prepara i dati per il template
    carrello_items = []
    for elemento in elementi_carrello:
        carrello_items.append({
            'id': elemento.id,
            'prodotto_id': elemento.prodotto.id,
            'nome': elemento.prodotto.nome,
            'marca': elemento.prodotto.marca,
            'categoria': elemento.prodotto.get_categoria_display(),
            'prezzo_unitario': elemento.prezzo_unitario_scontato,
            'quantita': elemento.quantita,
            'prezzo_totale': elemento.prezzo_totale,
            'foto': elemento.prodotto.foto.url if elemento.prodotto.foto else None,
            'peso': elemento.prodotto.peso,
        })
    
    # Calcola totali
    subtotale = carrello.subtotale
    costo_spedizione = carrello.spese_spedizione
    totale_finale = carrello.totale_finale
    
    # Gestione del form POST (quando viene completato il checkout)
    if request.method == 'POST':
        return process_order(request, carrello, elementi_carrello, subtotale, costo_spedizione, totale_finale)
    
    context = {
        'carrello': carrello,
        'carrello_items': carrello_items,
        'subtotale': subtotale,
        'costo_spedizione': costo_spedizione,
        'totale_finale': totale_finale,
        'negozio': profilo.negozio_preferito,
        'user': request.user,
    }
    
    return render(request, 'carrello/checkout.html', context)

def process_order(request, carrello, elementi_carrello, subtotale, costo_spedizione, totale_finale):
    """Processa l'ordine dal checkout"""
    
    print(f"DEBUG: Process order chiamato, POST data: {request.POST}")
    
    # Validazione campi obbligatori
    required_fields = {
        'nome_completo': 'Nome completo',
        'email': 'Email',
        'telefono': 'Telefono',
        'indirizzo': 'Indirizzo',
        'citta': 'Città',
        'cap': 'CAP',
        'provincia': 'Provincia',
    }
    
    errors = []
    for field, label in required_fields.items():
        value = request.POST.get(field, '').strip()
        if not value:
            errors.append(f'Il campo {label} è obbligatorio')
            print(f"DEBUG: Campo {field} è vuoto")
        else:
            print(f"DEBUG: Campo {field} = '{value}'")
    
    # Validazione email
    import re
    email = request.POST.get('email', '').strip()
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append('Inserisci un indirizzo email valido')
        print(f"DEBUG: Email non valida: '{email}'")
    
    # Validazione CAP
    cap = request.POST.get('cap', '').strip()
    if cap and not re.match(r'^\d{5}$', cap):
        errors.append('Il CAP deve essere di 5 cifre')
        print(f"DEBUG: CAP non valido: '{cap}'")
    
    # Validazione provincia
    provincia = request.POST.get('provincia', '').strip().upper()
    if provincia and len(provincia) != 2:
        errors.append('La provincia deve essere di 2 lettere (es. MO, BO)')
        print(f"DEBUG: Provincia non valida: '{provincia}'")
    
    # Validazione campi di fatturazione se diversi
    if request.POST.get('different_billing'):
        billing_fields = {
            'indirizzo_fatturazione': 'Indirizzo fatturazione',
            'citta_fatturazione': 'Città fatturazione', 
            'cap_fatturazione': 'CAP fatturazione',
            'provincia_fatturazione': 'Provincia fatturazione',
        }
        
        for field, label in billing_fields.items():
            if not request.POST.get(field, '').strip():
                errors.append(f'Il campo {label} è obbligatorio')
    
    if errors:
        print(f"DEBUG: Errori trovati: {errors}")
        for error in errors:
            messages.error(request, error)
        return redirect('carrello:checkout')
    
    print("DEBUG: Validazione passata, creando ordine...")
    
    try:
        # Crea l'ordine
        ordine = Ordine.objects.create(
            utente=request.user,
            negozio=request.user.profilo.negozio_preferito,
            nome_completo=request.POST.get('nome_completo').strip(),
            email=email,
            telefono=request.POST.get('telefono').strip(),
            indirizzo=request.POST.get('indirizzo').strip(),
            citta=request.POST.get('citta').strip(),
            cap=cap,
            provincia=provincia,
            note_consegna=request.POST.get('note_consegna', '').strip(),
            subtotale=subtotale,
            spese_spedizione=costo_spedizione,
            totale_finale=totale_finale,
        )
        
        # Crea gli elementi dell'ordine e aggiorna lo stock
        from negozi.models import DisponibilitaProdotto
        
        for elemento in elementi_carrello:
            # Crea l'elemento dell'ordine
            ElementoOrdine.objects.create(
                ordine=ordine,
                prodotto=elemento.prodotto,
                quantita=elemento.quantita,
                prezzo_unitario=elemento.prezzo_unitario,
                sconto_applicato=elemento.sconto_applicato,
            )
            
            # Aggiorna lo stock del prodotto
            # LOGICA UNIFICATA per aggiornare lo stock
            try:
                # Prova prima a aggiornare la disponibilità specifica per il negozio
                disponibilita = DisponibilitaProdotto.objects.get(
                    prodotto=elemento.prodotto,
                    negozio=ordine.negozio
                )
                
                if disponibilita.quantita_disponibile >= elemento.quantita:
                    disponibilita.quantita_disponibile -= elemento.quantita
                    disponibilita.save()
                    
            except DisponibilitaProdotto.DoesNotExist:
                # Se non esiste record di disponibilità specifica, aggiorna lo stock generale
                if elemento.prodotto.stock >= elemento.quantita:
                    elemento.prodotto.stock -= elemento.quantita
                    elemento.prodotto.save()
        
        # Svuota il carrello dopo l'ordine
        carrello.svuota_carrello()
        
        # Messaggio di successo
        messages.success(request, f'Ordine #{ordine.codice_ordine} creato con successo!')
        
        print(f"DEBUG: Ordine creato con successo: {ordine.codice_ordine}")
        
        # Reindirizza alla pagina di conferma con il codice ordine
        return redirect('carrello:ordine_completato', codice_ordine=ordine.codice_ordine)
        
    except Exception as e:
        print(f"DEBUG: Errore durante creazione ordine: {e}")
        messages.error(request, f'Errore durante la creazione dell\'ordine. Riprova.')
        return redirect('carrello:checkout')

@login_required
def ordine_completato(request, codice_ordine):
    """Vista per la conferma ordine completato"""
    try:
        ordine = Ordine.objects.get(
            codice_ordine=codice_ordine,
            utente=request.user
        )
        
        elementi_ordine = ElementoOrdine.objects.filter(ordine=ordine).select_related('prodotto')
        
        context = {
            'ordine': ordine,
            'elementi_ordine': elementi_ordine,
        }
        
        return render(request, 'carrello/ordine_completato.html', context)
        
    except Ordine.DoesNotExist:
        messages.error(request, 'Ordine non trovato')
        return redirect('home')

@dipendente_non_allowed
@login_required
def incrementa_quantita(request, elemento_id):
    """Vista per incrementare la quantità di un elemento nel carrello"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Metodo non permesso'})
    
    try:
        carrello = Carrello.get_or_create_for_user(request.user)
        elemento = get_object_or_404(ElementoCarrello, id=elemento_id, carrello=carrello)
        
        nuova_quantita = elemento.quantita + 1
        
        # Verifica disponibilità - LOGICA UNIFICATA
        from negozi.models import DisponibilitaProdotto
        try:
            # Prova prima a cercare disponibilità specifica per il negozio
            disponibilita = DisponibilitaProdotto.objects.get(
                prodotto=elemento.prodotto,
                negozio=carrello.negozio
            )
            
            if nuova_quantita > disponibilita.quantita_disponibile:
                return JsonResponse({
                    'success': False, 
                    'message': f'Disponibili solo {disponibilita.quantita_disponibile} pezzi'
                })
        except DisponibilitaProdotto.DoesNotExist:
            # Verifica se il prodotto è associato al negozio dell'utente
            if elemento.prodotto.negozi.filter(id=carrello.negozio.id).exists():
                # È associato al negozio ma manca il record DisponibilitaProdotto
                # Usa lo stock del prodotto stesso
                if nuova_quantita > elemento.prodotto.stock:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Disponibili solo {elemento.prodotto.stock} pezzi'
                    })
            elif not elemento.prodotto.negozi.exists():
                # È un prodotto comune - usa lo stock del prodotto stesso
                if nuova_quantita > elemento.prodotto.stock:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Disponibili solo {elemento.prodotto.stock} pezzi'
                    })
            else:
                # È un prodotto specifico di altri negozi, non più disponibile qui
                return JsonResponse({'success': False, 'message': 'Prodotto non più disponibile'})
        
        elemento.quantita = nuova_quantita
        elemento.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Quantità aumentata',
            'quantita': elemento.quantita,
            'carrello_count': carrello.numero_articoli,
            'elemento_prezzo_totale': float(elemento.prezzo_totale),
            'carrello_subtotale': float(carrello.subtotale),
            'carrello_totale': float(carrello.totale_finale)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Errore nell\'incremento: {str(e)}'
        })

@dipendente_non_allowed
@login_required
def decrementa_quantita(request, elemento_id):
    """Vista per decrementare la quantità di un elemento nel carrello"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Metodo non permesso'})
    
    try:
        carrello = Carrello.get_or_create_for_user(request.user)
        elemento = get_object_or_404(ElementoCarrello, id=elemento_id, carrello=carrello)
        
        if elemento.quantita <= 1:
            return JsonResponse({
                'success': False, 
                'message': 'La quantità non può essere inferiore a 1'
            })
        
        elemento.quantita -= 1
        elemento.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Quantità diminuita',
            'quantita': elemento.quantita,
            'carrello_count': carrello.numero_articoli,
            'elemento_prezzo_totale': float(elemento.prezzo_totale),
            'carrello_subtotale': float(carrello.subtotale),
            'carrello_totale': float(carrello.totale_finale)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Errore nel decremento: {str(e)}'
        })
