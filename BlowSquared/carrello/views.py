from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Carrello, ElementoCarrello, Ordine, ElementoOrdine
from prodotti.models import Prodotto

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

@login_required
def aggiungi_al_carrello(request, prodotto_id):
    """Vista per aggiungere un prodotto al carrello"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Metodo non permesso'})
    
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
        try:
            disponibilita = DisponibilitaProdotto.objects.get(
                prodotto=prodotto,
                negozio=profilo.negozio_preferito
            )
            if disponibilita.quantita_disponibile <= 0:
                return JsonResponse({
                    'success': False, 
                    'message': f'Il prodotto "{prodotto.nome}" non è attualmente disponibile'
                })
        except DisponibilitaProdotto.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': f'Il prodotto "{prodotto.nome}" non è disponibile nel tuo negozio'
            })
        
        # Ottieni la quantità dalla richiesta (default 1)
        quantita = int(request.POST.get('quantita', 1))
        if quantita <= 0 or quantita > 99:
            return JsonResponse({'success': False, 'message': 'Quantità non valida'})
        
        # Verifica che ci sia abbastanza stock
        if quantita > disponibilita.quantita_disponibile:
            return JsonResponse({
                'success': False, 
                'message': f'Disponibili solo {disponibilita.quantita_disponibile} pezzi'
            })
        
        # Ottieni o crea il carrello
        carrello = Carrello.get_or_create_for_user(request.user)
        
        # Aggiorna il negozio del carrello se necessario
        if carrello.negozio != profilo.negozio_preferito:
            carrello.negozio = profilo.negozio_preferito
            carrello.save()
        
        # Aggiungi il prodotto al carrello
        elemento = carrello.aggiungi_prodotto(prodotto, quantita)
        
        # Verifica di nuovo lo stock dopo l'aggiunta
        if elemento.quantita > disponibilita.quantita_disponibile:
            elemento.quantita = disponibilita.quantita_disponibile
            elemento.save()
            messaggio = f'{prodotto.nome} aggiunto (quantità limitata a {disponibilita.quantita_disponibile})'
        else:
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
        
        # Verifica disponibilità
        from negozi.models import DisponibilitaProdotto
        try:
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

@login_required
def checkout(request):
    """Vista per la pagina di checkout"""
    
    # Debug del metodo
    print(f"Checkout method: {request.method}")
    if request.method == 'POST':
        print(f"POST data: {dict(request.POST)}")
    
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
        print("Processing order...")
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
        if not request.POST.get(field, '').strip():
            errors.append(f'Il campo {label} è obbligatorio')
    
    # Validazione email
    import re
    email = request.POST.get('email', '').strip()
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append('Inserisci un indirizzo email valido')
    
    # Validazione CAP
    cap = request.POST.get('cap', '').strip()
    if cap and not re.match(r'^\d{5}$', cap):
        errors.append('Il CAP deve essere di 5 cifre')
    
    # Validazione provincia
    provincia = request.POST.get('provincia', '').strip().upper()
    if provincia and len(provincia) != 2:
        errors.append('La provincia deve essere di 2 lettere (es. MO, BO)')
    
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
        for error in errors:
            messages.error(request, error)
        return redirect('carrello:checkout')
    
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
        
        # Crea gli elementi dell'ordine
        for elemento in elementi_carrello:
            ElementoOrdine.objects.create(
                ordine=ordine,
                prodotto=elemento.prodotto,
                quantita=elemento.quantita,
                prezzo_unitario=elemento.prezzo_unitario,
                sconto_applicato=elemento.sconto_applicato,
            )
        
        # Svuota il carrello dopo l'ordine
        carrello.svuota_carrello()
        
        # Messaggio di successo
        messages.success(request, f'Ordine #{ordine.codice_ordine} creato con successo!')
        
        # Reindirizza alla pagina di conferma con il codice ordine
        return redirect('carrello:ordine_completato', codice_ordine=ordine.codice_ordine)
        
    except Exception as e:
        print(f"Errore creazione ordine: {e}")  # Debug
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
