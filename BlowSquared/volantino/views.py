from django.shortcuts import render
from django.http import JsonResponse

def sfoglia_volantino(request):
    """Vista per sfogliare il volantino interattivo"""
    # Per ora mock data - poi integreremo con i modelli
    volantino_data = {
        'titolo': 'Offerte di Febbraio 2024',
        'sottotitolo': 'Scopri i nostri prodotti in promozione',
        'data_inizio': '01/02/2024',
        'data_fine': '29/02/2024',
        'numero_pagine': 8,
        'pagine': [
            {
                'numero': 1,
                'immagine': '/static/img/volantino/pagina-1.png',
                'titolo': 'Copertina - Offerte del Mese'
            },
            {
                'numero': 2,
                'immagine': '/static/img/volantino/pagina-2.png',
                'titolo': 'Prodotti Freschi'
            },
            {
                'numero': 3,
                'immagine': '/static/img/volantino/pagina-3.png',
                'titolo': 'Salumi e Formaggi'
            },
            {
                'numero': 4,
                'immagine': '/static/img/volantino/pagina-4.png',
                'titolo': 'Bevande e Vini'
            },
            {
                'numero': 5,
                'immagine': '/static/img/volantino/pagina-5.png',
                'titolo': 'Prodotti per la Casa'
            },
            {
                'numero': 6,
                'immagine': '/static/img/volantino/pagina-6.png',
                'titolo': 'Offerte Speciali'
            },
            {
                'numero': 7,
                'immagine': '/static/img/volantino/pagina-7.png',
                'titolo': 'Prodotti Biologici'
            },
            {
                'numero': 8,
                'immagine': '/static/img/volantino/pagina-8.png',
                'titolo': 'Contatti e Orari'
            },
        ]
    }
    
    context = {
        'volantino': volantino_data,
    }
    
    return render(request, 'volantino/sfoglia.html', context)

def pagina_volantino(request, pagina_num):
    """Vista per una singola pagina del volantino (API JSON)"""
    # API per il viewer JavaScript
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        pagina_data = {
            'numero': pagina_num,
            'immagine': f'/static/img/volantino/pagina-{pagina_num}.png',  
            'titolo': f'Pagina {pagina_num}',
            'success': True
        }
        return JsonResponse(pagina_data)
    
    context = {
        'pagina_numero': pagina_num,
        'immagine': f'/static/img/volantino/pagina-{pagina_num}.png',  
    }
