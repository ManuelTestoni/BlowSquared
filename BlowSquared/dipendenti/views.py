from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Dipendente
from .forms import ProdottoForm
from prodotti.models import Prodotto
from django.contrib.auth import authenticate, login
from django.contrib import messages


@login_required
def dashboard_dipendente(request):
    dipendente = get_object_or_404(Dipendente, user=request.user)
    
    # Metodo 1: Prodotti specifici del negozio
    prodotti_negozio = Prodotto.objects.filter(negozi=dipendente.negozio)
    
    # Metodo 2: Prodotti senza negozi associati (prodotti comuni)
    prodotti_comuni = Prodotto.objects.filter(negozi__isnull=True)
    
    # Unione dei due QuerySet
    prodotti = (prodotti_negozio | prodotti_comuni).distinct().order_by('nome')
    
    return render(request, 'dipendenti/dashboard.html', {
        'prodotti': prodotti, 
        'negozio': dipendente.negozio
    })

@login_required
def aggiungi_prodotto(request):
    dipendente = get_object_or_404(Dipendente, user=request.user)
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES)
        if form.is_valid():
            prodotto = form.save(commit=False)
            prodotto.stock = form.cleaned_data['quantita']
            prodotto.save()
            
            # Aggiungiamo il prodotto solamente al negozio del dipendente,
            # sennò creeremmo un prodotto comune.
            prodotto.negozi.add(dipendente.negozio)
            
            messages.success(request, f'Prodotto "{prodotto.nome}" aggiunto con successo al catalogo di {dipendente.negozio.nome}!')
            return redirect('dipendenti:dashboard')
        else:
            messages.error(request, 'Errori nel form. Controlla i dati inseriti.')
    else:
        form = ProdottoForm()
    return render(request, 'dipendenti/aggiungi_prodotto.html', {'form': form, 'negozio': dipendente.negozio})

@login_required
def aggiorna_quantita(request, prodotto_id):
    dipendente = get_object_or_404(Dipendente, user=request.user)
    prodotti_negozio = Prodotto.objects.filter(negozi=dipendente.negozio)
    prodotti_comuni = Prodotto.objects.filter(negozi__isnull=True)
    prodotti_accessibili = (prodotti_negozio | prodotti_comuni).distinct()
    
    prodotto = get_object_or_404(prodotti_accessibili, id=prodotto_id)
    
    if request.method == 'POST':
        try:
            # Ottieni il tipo di operazione e la quantità
            operazione = request.POST.get('operazione')  # 'aumenta' o 'diminuisci' o 'imposta'
            quantita_input = request.POST.get('quantita', 0)
            
            try:
                quantita = int(quantita_input)
            except ValueError:
                messages.error(request, 'Quantità non valida. Inserisci un numero.')
                return render(request, 'dipendenti/aggiorna_quantita.html', {
                    'prodotto': prodotto, 
                    'negozio': dipendente.negozio
                })
            
            # Controlli di validazione custom
            if quantita < 0:
                messages.error(request, 'La quantità non può essere negativa.')
                return render(request, 'dipendenti/aggiorna_quantita.html', {
                    'prodotto': prodotto, 
                    'negozio': dipendente.negozio
                })
            
            if quantita > 100:
                messages.error(request, 'Non è possibile aggiungere più di 100 prodotti alla volta.')
                return render(request, 'dipendenti/aggiorna_quantita.html', {
                    'prodotto': prodotto, 
                    'negozio': dipendente.negozio
                })
            
            # Calcola la nuova quantità basata sull'operazione
            stock_attuale = prodotto.stock
            
            if operazione == 'aumenta':
                nuova_quantita = stock_attuale + quantita
            elif operazione == 'diminuisci':
                nuova_quantita = stock_attuale - quantita
                if nuova_quantita < 0:
                    messages.error(request, f'Non puoi rimuovere {quantita} prodotti. Disponibili solo {stock_attuale}.')
                    return render(request, 'dipendenti/aggiorna_quantita.html', {
                        'prodotto': prodotto, 
                        'negozio': dipendente.negozio
                    })
            elif operazione == 'imposta':
                nuova_quantita = quantita
            else:
                messages.error(request, 'Operazione non valida.')
                return render(request, 'dipendenti/aggiorna_quantita.html', {
                    'prodotto': prodotto, 
                    'negozio': dipendente.negozio
                })
            
            # Controllo finale sulla quantità massima
            if nuova_quantita > 250:
                messages.error(request, 'La quantità massima consentita è 250.')
                return render(request, 'dipendenti/aggiorna_quantita.html', {
                    'prodotto': prodotto, 
                    'negozio': dipendente.negozio
                })
            
            # Aggiorna il database - LOGICA UNIFICATA
            from negozi.models import DisponibilitaProdotto
            
            # Controlla se è un prodotto comune o specifico del negozio
            if not prodotto.negozi.exists():
                # È un prodotto COMUNE - aggiorna solo lo stock generale
                prodotto.stock = nuova_quantita
                prodotto.save(update_fields=['stock'])
                
                # Rimuovi eventuali record specifici di DisponibilitaProdotto per questo prodotto
                # perché per i prodotti comuni dovrebbe essere usato sempre prodotto.stock
                DisponibilitaProdotto.objects.filter(prodotto=prodotto).delete()
                
            else:
                # È un prodotto SPECIFICO del negozio - aggiorna sia stock generale che disponibilità specifica
                
                # Aggiorna lo stock generale
                prodotto.stock = nuova_quantita
                prodotto.save(update_fields=['stock'])
                
                # Aggiorna anche la disponibilità specifica per il negozio
                disponibilita, created = DisponibilitaProdotto.objects.get_or_create(
                    prodotto=prodotto,
                    negozio=dipendente.negozio,
                    defaults={'quantita_disponibile': nuova_quantita}
                )
                
                if not created:
                    disponibilita.quantita_disponibile = nuova_quantita
                    disponibilita.save()
                
        except Exception as e:
            # Fallback: almeno aggiorna lo stock generale
            prodotto.stock = nuova_quantita
            prodotto.save(update_fields=['stock'])
            
            # Messaggio di successo personalizzato
            if operazione == 'aumenta':
                action_msg = f'Aggiunti {quantita} prodotti'
            elif operazione == 'diminuisci':
                action_msg = f'Rimossi {quantita} prodotti'
            else:
                action_msg = f'Quantità impostata a {quantita}'
                
            messages.success(request, f'{action_msg}. Stock attuale: {nuova_quantita} pezzi per "{prodotto.nome}"')
            return redirect('dipendenti:dashboard')
            
        except Exception as e:
            messages.error(request, f'Errore durante l\'aggiornamento: {str(e)}')
            
    return render(request, 'dipendenti/aggiorna_quantita.html', {
        'prodotto': prodotto, 
        'negozio': dipendente.negozio
    })

def login_dipendente(request):
    if request.user.is_authenticated and hasattr(request.user, 'dipendente'):
        return redirect('dipendenti:dashboard')
    
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
            if hasattr(user, 'dipendente'):
                login(request, user)
                return redirect('dipendenti:dashboard')
            else:
                error = "Questo utente non è un dipendente."
        else:
            error = "Credenziali non valide."
    
    return render(request, 'dipendenti/login.html', {'error': error})
       