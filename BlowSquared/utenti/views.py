from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q
from .forms import CustomUserCreationForm
from prodotti.models import Prodotto

def index(request):
    return render(request, 'utenti/index.html')

def signup_view(request):
    """Vista per la registrazione utente"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account creato con successo per {username}!')
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Errore nella registrazione. Controlla i dati inseriti.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'utenti/signup.html', {'form': form})

def login_view(request):
    """Vista per il login utente"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Benvenuto, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Username o password non validi.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'utenti/login.html', {'form': form})

@login_required
def logout_view(request):
    """Vista per il logout utente"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logout effettuato con successo!')
        return redirect('home')
    
    return render(request, 'utenti/logout_confirm.html')

@login_required
def profile_view(request):
    """Vista per il profilo utente completo"""
    try:
        from .models import ListaSpesa
        
        # Dati reali dalle liste della spesa
        tutte_liste = ListaSpesa.objects.filter(utente=request.user)
        liste_spesa = tutte_liste.order_by('-data_modifica')  # Rimuovo lo slice per ora
        ordini_recenti = []  # Qui andranno gli ordini dal database quando implementato
        
        # Statistiche utente reali
        stats = {
            'ordini_totali': 0,  # Da implementare con gli ordini
            'importo_totale': 0.00,  # Da implementare con gli ordini
            'prodotti_preferiti': 0,  # Da implementare
            'liste_attive': tutte_liste.filter(completata=False).count()
        }
    except Exception as e:
        # Fallback se le tabelle non esistono ancora
        print(f"Errore nel caricamento liste: {e}")  # Debug
        liste_spesa = []
        ordini_recenti = []
        stats = {
            'ordini_totali': 0,
            'importo_totale': 0.00,
            'prodotti_preferiti': 0,
            'liste_attive': 0
        }
    
    context = {
        'user': request.user,
        'ordini_recenti': ordini_recenti,
        'liste_spesa': liste_spesa,
        'stats': stats
    }
    
    return render(request, 'utenti/profile.html', context)

@login_required
def liste_spesa_view(request):
    """Vista per visualizzare tutte le liste della spesa dell'utente"""
    from .models import ListaSpesa
    
    try:
        liste_spesa = ListaSpesa.objects.filter(utente=request.user).order_by('-data_modifica')
        
        context = {
            'liste_spesa': liste_spesa,
        }
        return render(request, 'utenti/liste_spesa.html', context)
    except Exception:
        # Fallback se le tabelle non esistono ancora
        messages.error(request, 'Sistema liste non ancora configurato. Esegui le migrazioni.')
        return redirect('utenti:profile')

@login_required
def crea_lista_view(request):
    """Vista per creare una nuova lista della spesa"""
    from .models import ListaSpesa, ElementoLista
    
    if request.method == 'POST':
        nome_lista = request.POST.get('nome_lista')
        descrizione = request.POST.get('descrizione', '')
        
        if nome_lista:
            try:
                # Crea la lista
                lista = ListaSpesa.objects.create(
                    nome=nome_lista,
                    utente=request.user,
                    descrizione=descrizione
                )
                
                # Aggiungi prodotti se specificati
                prodotti_ids = request.POST.getlist('prodotti')
                quantita_values = request.POST.getlist('quantita')
                note_values = request.POST.getlist('note')
                priorita_values = request.POST.getlist('priorita')
                
                for i, prodotto_id in enumerate(prodotti_ids):
                    if prodotto_id:
                        try:
                            prodotto = Prodotto.objects.get(id=prodotto_id)
                            quantita = int(quantita_values[i]) if i < len(quantita_values) and quantita_values[i] else 1
                            note = note_values[i] if i < len(note_values) else ''
                            priorita = int(priorita_values[i]) if i < len(priorita_values) and priorita_values[i] else 0
                            
                            ElementoLista.objects.create(
                                lista=lista,
                                prodotto=prodotto,
                                quantita=quantita,
                                note=note,
                                priorita=priorita
                            )
                        except (Prodotto.DoesNotExist, ValueError):
                            continue
                
                messages.success(request, f'Lista "{nome_lista}" creata con successo!')
                return redirect('utenti:profile')  # Cambiato da dettaglio_lista a profile
            
            except Exception as e:
                messages.error(request, f'Errore nella creazione della lista: {str(e)}')
        else:
            messages.error(request, 'Nome della lista obbligatorio.')
    
    # Recupera tutti i prodotti per il form
    prodotti = Prodotto.objects.all().order_by('nome')
    
    context = {
        'prodotti': prodotti,
    }
    return render(request, 'utenti/crea_lista.html', context)

@login_required
def dettaglio_lista_view(request, lista_id):
    """Vista per visualizzare il dettaglio di una lista"""
    from .models import ListaSpesa
    
    lista = get_object_or_404(ListaSpesa, id=lista_id, utente=request.user)
    elementi = lista.elementi.all().order_by('-priorita', 'data_aggiunta')
    
    context = {
        'lista': lista,
        'elementi': elementi,
    }
    return render(request, 'utenti/dettaglio_lista.html', context)

@login_required
def aggiungi_prodotto_lista(request, lista_id):
    """Vista AJAX per aggiungere un prodotto alla lista"""
    from .models import ListaSpesa, ElementoLista
    
    if request.method == 'POST':
        try:
            lista = get_object_or_404(ListaSpesa, id=lista_id, utente=request.user)
            prodotto_id = request.POST.get('prodotto_id')
            quantita = int(request.POST.get('quantita', 1))
            note = request.POST.get('note', '')
            priorita = int(request.POST.get('priorita', 0))
            
            prodotto = get_object_or_404(Prodotto, id=prodotto_id)
            
            # Verifica se il prodotto è già nella lista
            elemento, created = ElementoLista.objects.get_or_create(
                lista=lista,
                prodotto=prodotto,
                defaults={
                    'quantita': quantita,
                    'note': note,
                    'priorita': priorita
                }
            )
            
            if not created:
                # Se esiste già, aggiorna la quantità
                elemento.quantita += quantita
                elemento.save()
                message = f'Quantità aggiornata per {prodotto.nome}'
            else:
                message = f'{prodotto.nome} aggiunto alla lista'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'elemento_id': elemento.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Errore: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Metodo non consentito'})

@login_required
def rimuovi_prodotto_lista(request, lista_id, elemento_id):
    """Vista per rimuovere un prodotto dalla lista"""
    from .models import ListaSpesa, ElementoLista
    
    lista = get_object_or_404(ListaSpesa, id=lista_id, utente=request.user)
    elemento = get_object_or_404(ElementoLista, id=elemento_id, lista=lista)
    
    nome_prodotto = elemento.prodotto.nome
    elemento.delete()
    
    messages.success(request, f'{nome_prodotto} rimosso dalla lista')
    return redirect('utenti:dettaglio_lista', lista_id=lista_id)

@login_required
def ordina_lista_view(request, lista_id):
    """Vista per ordinare tutti i prodotti di una lista (simulazione)"""
    from .models import ListaSpesa
    
    lista = get_object_or_404(ListaSpesa, id=lista_id, utente=request.user)
    
    if request.method == 'POST':
        # Simulazione ordine - in futuro implementare logica carrello/ordini
        lista.completata = True
        lista.save()
        
        # Calcola totale
        totale = lista.prezzo_stimato
        
        messages.success(request, f'Ordine simulato per la lista "{lista.nome}" - Totale: €{totale:.2f}')
        return redirect('utenti:profile')  # Cambiato da liste_spesa a profile
    
    elementi = lista.elementi.all()
    context = {
        'lista': lista,
        'elementi': elementi,
        'totale': lista.prezzo_stimato
    }
    return render(request, 'utenti/ordina_lista.html', context)

@login_required
def cerca_prodotti_ajax(request):
    """Vista AJAX per cercare prodotti"""
    query = request.GET.get('q', '')
    
    if len(query) >= 2:
        prodotti = Prodotto.objects.filter(
            Q(nome__icontains=query) | 
            Q(marca__icontains=query)
        )[:10]
        
        results = []
        for prodotto in prodotti:
            prezzo_display = prodotto.prezzo
            if prodotto.sconto > 0:
                prezzo_scontato = prodotto.prezzo * (100 - prodotto.sconto) / 100
                prezzo_display = prezzo_scontato
            
            results.append({
                'id': prodotto.id,
                'nome': prodotto.nome,
                'marca': prodotto.marca,
                'prezzo': float(prezzo_display),
                'foto': prodotto.foto.url if prodotto.foto else '',
                'stock': prodotto.stock
            })
        
        return JsonResponse({'prodotti': results})
    
    return JsonResponse({'prodotti': []})

@login_required
def elimina_lista_view(request, lista_id):
    """Vista per eliminare una lista della spesa"""
    from .models import ListaSpesa
    
    lista = get_object_or_404(ListaSpesa, id=lista_id, utente=request.user)
    nome_lista = lista.nome
    
    if request.method == 'POST':
        lista.delete()
        messages.success(request, f'Lista "{nome_lista}" eliminata con successo!')
        return redirect('utenti:profile')
    
    # Se è una richiesta AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        lista.delete()
        return JsonResponse({'success': True, 'message': f'Lista "{nome_lista}" eliminata!'})
    
    return redirect('utenti:profile')

@login_required
def visualizza_lista_popup(request, lista_id):
    """Vista AJAX per visualizzare lista in popup"""
    from .models import ListaSpesa
    
    lista = get_object_or_404(ListaSpesa, id=lista_id, utente=request.user)
    elementi = lista.elementi.all().order_by('-priorita', 'data_aggiunta')
    
    elementi_data = []
    for elemento in elementi:
        elementi_data.append({
            'nome': elemento.prodotto.nome,
            'marca': elemento.prodotto.marca,
            'quantita': elemento.quantita,
            'prezzo_unitario': float(elemento.prodotto.prezzo),
            'prezzo_totale': float(elemento.prezzo_totale),
            'priorita': elemento.get_priorita_display(),
            'priorita_emoji': elemento.get_priorita_display_emoji(),
            'note': elemento.note or '',
            'disponibile': elemento.disponibile,
            'categoria': elemento.prodotto.get_categoria_display()
        })
    
    return JsonResponse({
        'success': True,
        'lista': {
            'nome': lista.nome,
            'descrizione': lista.descrizione or '',
            'numero_prodotti': lista.numero_prodotti,
            'quantita_totale': lista.quantita_totale,
            'prezzo_stimato': float(lista.prezzo_stimato),
            'data_creazione': lista.data_creazione.strftime('%d/%m/%Y'),
            'completata': lista.completata
        },
        'elementi': elementi_data
    })
