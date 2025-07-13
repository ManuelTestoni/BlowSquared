from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied


class DipendenteAccessMixin(UserPassesTestMixin):
    """
    Mixin che limita l'accesso dei dipendenti e dirigenti solo alle loro pagine autorizzate.
    Dipendenti e dirigenti possono accedere solo a:
    - Home page
    - Dashboard dipendenti/dirigenti
    - Operazioni sui prodotti (aggiungi, aggiorna stock) - solo dipendenti
    - Logout
    
    Per tutte le altre pagine vengono reindirizzati alla pagina 404 personalizzata.
    """
    
    def test_func(self):
        """
        Controlla se l'utente è un dipendente/dirigente e se può accedere alla pagina corrente.
        """
        user = self.request.user
        
        # Se non è autenticato, lascio che Django gestisca il redirect al login
        if not user.is_authenticated:
            return True
            
        # Se non è un dipendente o dirigente, può accedere normalmente
        if not (hasattr(user, 'dipendente') or hasattr(user, 'dirigente')):
            return True
            
        # Se è un dipendente o dirigente, controlla le pagine consentite
        current_url = self.request.resolver_match.url_name
        current_namespace = getattr(self.request.resolver_match, 'namespace', '')
        
        # Pagine consentite per dipendenti e dirigenti
        allowed_urls = {
            # Home page
            'home',
            # Dashboard dipendenti
            'dipendenti:dashboard',
            'dipendenti:aggiungi_prodotto', 
            'dipendenti:aggiorna_quantita',
            # Dashboard dirigenti e tutte le funzionalità dirigenti
            'dirigenti:dashboard',
            'dirigenti:login',
            'dirigenti:gestione_negozi',
            'dirigenti:gestione_dipendenti', 
            'dirigenti:statistiche',
            'dirigenti:gestione_prodotti',
            # Logout
            'logout',
            # Pagine di errore
            '404',
            '403',
            '500',
        }
        
        # Controlla se la URL corrente è consentita
        full_url = f"{current_namespace}:{current_url}" if current_namespace else current_url
        
        return full_url in allowed_urls or current_url in allowed_urls
    
    def handle_no_permission(self):
        """
        Gestisce il caso in cui il dipendente non ha il permesso di accedere alla pagina.
        Mostra la pagina 404 personalizzata invece del classico 403.
        """
        # Renderizza la pagina 404 personalizzata
        return render(self.request, '404.html', status=404)


class DipendenteRequiredMixin(UserPassesTestMixin):
    """
    Mixin che richiede che l'utente sia un dipendente o dirigente autenticato.
    Utilizzato per le pagine che sono esclusivamente per dipendenti/dirigenti.
    """
    
    def test_func(self):
        """
        Controlla se l'utente è un dipendente o dirigente autenticato.
        """
        user = self.request.user
        return user.is_authenticated and (hasattr(user, 'dipendente') or hasattr(user, 'dirigente'))
    
    def handle_no_permission(self):
        """
        Reindirizza alla home se non è un dipendente.
        """
        from django.shortcuts import redirect
        return redirect('home')


class NonDipendenteRequiredMixin(UserPassesTestMixin):
    """
    Mixin che blocca l'accesso ai dipendenti e dirigenti per pagine riservate ad altri utenti.
    Utilizzato per carrello, forum, negozi, ecc.
    """
    
    def test_func(self):
        """
        Controlla che l'utente NON sia un dipendente o dirigente.
        """
        user = self.request.user
        
        # Se non è autenticato, può accedere (poi eventualmente verrà reindirizzato al login)
        if not user.is_authenticated:
            return True
            
        # Se è un dipendente o dirigente, blocca l'accesso
        if hasattr(user, 'dipendente') or hasattr(user, 'dirigente'):
            return False
            
        return True
    
    def handle_no_permission(self):
        """
        Mostra la pagina 404 per i dipendenti che tentano di accedere.
        """
        return render(self.request, '404.html', status=404)
