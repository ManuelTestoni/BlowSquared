from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Dipendente
from .forms import ProdottoForm
from prodotti.models import Prodotto

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
