"""
Test Suite per il Sistema Carrello
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
import json

from tests.test_base import BaseTestCase, TestUtilities
from carrello.models import Carrello, ElementoCarrello


class CarrelloModelTest(BaseTestCase):
    """Test per il modello Carrello"""
    
    def test_creazione_carrello(self):
        """Test creazione carrello per utente"""
        carrello = Carrello.objects.create(
            utente=self.utente_normale,
            negozio=self.negozio1
        )
        
        self.assertEqual(carrello.utente, self.utente_normale)
        self.assertEqual(carrello.negozio, self.negozio1)
        self.assertEqual(carrello.numero_articoli, 0)
        self.assertEqual(carrello.subtotale, Decimal('0.00'))
    
    def test_aggiunta_elementi_carrello(self):
        """Test aggiunta elementi al carrello"""
        carrello = TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            {self.prodotto1: 2, self.prodotto2: 1}
        )
        
        self.assertEqual(carrello.numero_articoli, 3)  # 2+1
        self.assertEqual(carrello.subtotale, Decimal('5.00'))  # 1.50*2 + 2.00*1
        self.assertEqual(carrello.elementi.count(), 2)  # 2 prodotti diversi
    
    def test_svuota_carrello(self):
        """Test svuotamento carrello"""
        carrello = TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            {self.prodotto1: 3, self.prodotto2: 2}
        )
        
        # Verifica che il carrello ha elementi
        self.assertEqual(carrello.numero_articoli, 5)
        self.assertTrue(carrello.elementi.exists())
        
        # Svuota il carrello
        carrello.svuota_carrello()
        
        # Verifica che è vuoto
        self.assertEqual(carrello.numero_articoli, 0)
        self.assertFalse(carrello.elementi.exists())


class CarrelloViewTest(BaseTestCase):
    """Test per le views del carrello"""
    
    def test_visualizza_carrello_vuoto(self):
        """Test visualizzazione carrello vuoto"""
        TestUtilities.login_user(self.client, self.utente_normale)
        
        response = self.client.get(reverse('carrello:visualizza'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Il tuo carrello è vuoto')
    
    def test_aggiungi_prodotto_carrello_ajax(self):
        """Test aggiunta prodotto al carrello via AJAX"""
        TestUtilities.login_user(self.client, self.utente_normale)
        
        response = self.client.post(
            reverse('carrello:aggiungi', args=[self.prodotto1.id]),
            {'quantita': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['carrello_count'], 2)
        
        # Verifica nel database
        carrello = Carrello.objects.get(utente=self.utente_normale)
        self.assertEqual(carrello.numero_articoli, 2)
    
    def test_rimuovi_prodotto_carrello_ajax(self):
        """Test rimozione prodotto dal carrello"""
        # Crea carrello con elementi
        carrello = TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            {self.prodotto1: 3}
        )
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        elemento = carrello.elementi.first()
        response = self.client.post(
            reverse('carrello:rimuovi', args=[elemento.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['carrello_count'], 0)
    
    def test_svuota_carrello_ajax(self):
        """Test svuotamento carrello via AJAX"""
        # Crea carrello con elementi
        TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            {self.prodotto1: 2, self.prodotto2: 1}
        )
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        response = self.client.post(
            reverse('carrello:svuota'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['carrello_count'], 0)
        
        # Verifica nel database
        carrello = Carrello.objects.get(utente=self.utente_normale)
        self.assertEqual(carrello.numero_articoli, 0)
    
    def test_prodotto_non_disponibile_negozio(self):
        """Test aggiunta prodotto non disponibile nel negozio"""
        # Il prodotto2 non è disponibile nel negozio2
        self.utente_normale.profilo.negozio_preferito = self.negozio2
        self.utente_normale.profilo.save()
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        response = self.client.post(
            reverse('carrello:aggiungi', args=[self.prodotto2.id]),
            {'quantita': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertFalse(data['success'])
        self.assertIn('non disponibile', data['message'].lower())


class CarrelloPermissionTest(BaseTestCase):
    """Test per i permessi del carrello"""
    
    def test_dipendente_non_puo_usare_carrello(self):
        """Test che i dipendenti non possono usare il carrello"""
        TestUtilities.login_user(self.client, self.dipendente_user)
        
        response = self.client.get(reverse('carrello:visualizza'))
        
        # Dovrebbe essere reindirizzato o avere accesso negato
        self.assertNotEqual(response.status_code, 200)
    
    def test_dirigente_non_puo_usare_carrello(self):
        """Test che i dirigenti non possono usare il carrello"""
        TestUtilities.login_user(self.client, self.dirigente_user)
        
        response = self.client.post(
            reverse('carrello:aggiungi', args=[self.prodotto1.id]),
            {'quantita': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Dovrebbe essere reindirizzato o avere accesso negato
        self.assertNotEqual(response.status_code, 200)
