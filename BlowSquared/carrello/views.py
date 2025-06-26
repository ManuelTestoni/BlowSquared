from django.shortcuts import render

def riepilogo(request):
    return render(request, 'carrello/riepilogo.html', {'carrello': []})
    return render(request, 'carrello/riepilogo.html', {'carrello': []})
