from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Dipendente
from .forms import ProdottoForm
from prodotti.models import Prodotto
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import models

@login_required
def dashboard_dipendente(request):
    dipendente = get_object_or_404(Dipendente, user=request.user)
    
    # LOGICA CORRETTA: Mostra SOLO prodotti del negozio specifico + prodotti comuni (senza negozio)
    # NON deve mostrare prodotti di altri negozi specifici
    prodotti = Prodotto.objects.filter(
        models.Q(negozio=dipendente.negozio) |  # Prodotti specifici del negozio del dipendente
        models.Q(negozio__isnull=True)         # Prodotti comuni (presenti in tutti i negozi)
    ).order_by('nome')
    
    # Debug per verificare la query
    print(f"Dipendente: {dipendente.nome} - Negozio: {dipendente.negozio.nome}")
    print(f"Prodotti trovati: {prodotti.count()}")
    for p in prodotti:
        negozio_info = p.negozio.nome if p.negozio else "COMUNE"
        print(f"- {p.nome} ({p.categoria}) - Negozio: {negozio_info}")
    
    return render(request, 'dipendenti/dashboard.html', {'prodotti': prodotti, 'negozio': dipendente.negozio})

@login_required
def aggiungi_prodotto(request):
    dipendente = get_object_or_404(Dipendente, user=request.user)
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES)
        if form.is_valid():
            prodotto = form.save(commit=False)
            # IMPORTANTE: Assegna il negozio del dipendente al prodotto
            prodotto.negozio = dipendente.negozio
            prodotto.stock = form.cleaned_data['quantita']
            prodotto.save()
            
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
    
    # OPZIONE 1: Query separata più leggibile
    prodotti_accessibili = Prodotto.objects.filter(
        models.Q(negozio=dipendente.negozio) | models.Q(negozio__isnull=True)
    )
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
            
            # Controlli di validazione
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
            if nuova_quantita > 9999:
                messages.error(request, 'La quantità massima consentita è 9999.')
                return render(request, 'dipendenti/aggiorna_quantita.html', {
                    'prodotto': prodotto, 
                    'negozio': dipendente.negozio
                })
            
            # Aggiorna il database
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
        
        print(f"Tentativo login: {email_or_username} / {password}")  # Debug
        
        # Prova prima con username diretto
        user = authenticate(request, username=email_or_username, password=password)
        print(f"Authenticate con username: {user}")  # Debug
        
        # Se non funziona, prova a cercare l'utente per email e usa il suo username
        if user is None:
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=email_or_username)
                print(f"Trovato utente per email: {user_obj.username}")  # Debug
                user = authenticate(request, username=user_obj.username, password=password)
                print(f"Authenticate con username trovato: {user}")  # Debug
            except User.DoesNotExist:
                print("Nessun utente trovato per questa email")  # Debug
        
        if user is not None:
            print(f"User autenticato, controllo dipendente...")  # Debug
            if hasattr(user, 'dipendente'):
                login(request, user)
                print("Login dipendente riuscito!")  # Debug
                return redirect('dipendenti:dashboard')
            else:
                error = "Questo utente non è un dipendente."
            print("Credenziali non valide")  # Debug
    
    return render(request, 'dipendenti/login.html', {'error': error})
       