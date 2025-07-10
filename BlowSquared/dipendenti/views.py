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
    prodotti = Prodotto.objects.filter(negozio=dipendente.negozio)
    return render(request, 'dipendenti/dashboard.html', {'prodotti': prodotti, 'negozio': dipendente.negozio})

@login_required
def aggiungi_prodotto(request):
    dipendente = get_object_or_404(Dipendente, user=request.user)
    if request.method == 'POST':
        form = ProdottoForm(request.POST, request.FILES)
        if form.is_valid():
            prodotto = form.save(commit=False)
            prodotto.negozio = dipendente.negozio
            prodotto.stock = form.cleaned_data['quantita']
            prodotto.save()
            return redirect('dipendenti:dashboard')
    else:
        form = ProdottoForm()
    return render(request, 'dipendenti/aggiungi_prodotto.html', {'form': form})

@login_required
def aggiorna_quantita(request, prodotto_id):
    dipendente = get_object_or_404(Dipendente, user=request.user)
    prodotto = get_object_or_404(Prodotto, id=prodotto_id, negozio=dipendente.negozio)
    if request.method == 'POST':
        quantita = int(request.POST.get('quantita', prodotto.stock))
        prodotto.stock = quantita
        prodotto.save()
        return redirect('dipendenti:dashboard')
    return render(request, 'dipendenti/aggiorna_quantita.html', {'prodotto': prodotto})

def login_dipendente(request):
    if request.user.is_authenticated and hasattr(request.user, 'dipendente'):
        return redirect('dipendenti:dashboard')
    
    error = None
    if request.method == 'POST':
        # Prendi il campo email ma usalo come username
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')
        
        # Prova prima con username
        user = authenticate(request, username=email_or_username, password=password)
        
        # Se non funziona, prova a cercare per email
        if user is None:
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None and hasattr(user, 'dipendente'):
            login(request, user)
            return redirect('dipendenti:dashboard')
        else:
            error = "Credenziali non valide o non sei un dipendente."
    
    return render(request, 'dipendenti/login.html', {'error': error})
