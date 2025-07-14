from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal

from tests.test_base import BaseTestCase, TestUtilities
from carrello.models import Carrello


class CambioNegozioTest(BaseTestCase):
    """Test per la logica di cambio negozio"""
    
    def test_cambio_negozio_senza_carrello(self):
        """Test cambio negozio quando l'utente non ha carrello"""
        TestUtilities.login_user(self.client, self.utente_normale)
        
        # Cambia da negozio1 a negozio2
        response = self.client.get(
            reverse('negozi:seleziona_preferito', args=[self.negozio2.id])
        )
        
        # Dovrebbe reindirizzare senza chiedere conferma
        self.assertEqual(response.status_code, 302)
        
        # Verifica che il negozio sia cambiato
        self.utente_normale.profilo.refresh_from_db()
        self.assertEqual(self.utente_normale.profilo.negozio_preferito, self.negozio2)
    
    def test_cambio_negozio_con_carrello_vuoto(self):
        """Test cambio negozio con carrello vuoto"""
        # Crea carrello vuoto
        Carrello.objects.create(utente=self.utente_normale, negozio=self.negozio1)
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        response = self.client.get(
            reverse('negozi:seleziona_preferito', args=[self.negozio2.id])
        )
        
        # Dovrebbe reindirizzare senza chiedere conferma (carrello vuoto)
        self.assertEqual(response.status_code, 302)
        
        self.utente_normale.profilo.refresh_from_db()
        self.assertEqual(self.utente_normale.profilo.negozio_preferito, self.negozio2)
    
    def test_cambio_negozio_con_carrello_pieno_mostra_conferma(self):
        """Test che il cambio negozio con carrello pieno mostra la pagina di conferma"""
        # Crea carrello con elementi
        TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            {self.prodotto1: 2, self.prodotto2: 1}
        )
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        response = self.client.get(
            reverse('negozi:seleziona_preferito', args=[self.negozio2.id])
        )
        
        # Dovrebbe mostrare la pagina di conferma
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Conferma Cambio Negozio')
        self.assertContains(response, 'Blow Squared Centro')  # negozio corrente
        self.assertContains(response, 'Blow Squared Periferia')  # negozio nuovo
        self.assertContains(response, '3')  # quantità totale articoli (2+1)
        self.assertContains(response, '2 prodotti diversi')
    
    def test_conferma_cambio_negozio_si(self):
        """Test conferma cambio negozio con 'si'"""
        # Crea carrello con elementi
        carrello = TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            {self.prodotto1: 3}
        )
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        # Conferma il cambio
        response = self.client.post(
            reverse('negozi:seleziona_preferito', args=[self.negozio2.id]),
            {'conferma_svuotamento': 'si'}
        )
        
        # Dovrebbe reindirizzare
        self.assertEqual(response.status_code, 302)
        
        # Verifica che il negozio sia cambiato
        self.utente_normale.profilo.refresh_from_db()
        self.assertEqual(self.utente_normale.profilo.negozio_preferito, self.negozio2)
        
        # Verifica che il carrello sia vuoto
        carrello.refresh_from_db()
        self.assertEqual(carrello.numero_articoli, 0)
    
    def test_conferma_cambio_negozio_no(self):
        """Test rifiuto cambio negozio con 'no'"""
        # Crea carrello con elementi
        carrello = TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            {self.prodotto1: 2, self.prodotto2: 1}
        )
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        # Rifiuta il cambio
        response = self.client.post(
            reverse('negozi:seleziona_preferito', args=[self.negozio2.id]),
            {'conferma_svuotamento': 'no'}
        )
        
        # Dovrebbe reindirizzare alla selezione negozio
        self.assertEqual(response.status_code, 302)
        
        # Verifica che il negozio NON sia cambiato
        self.utente_normale.profilo.refresh_from_db()
        self.assertEqual(self.utente_normale.profilo.negozio_preferito, self.negozio1)
        
        # Verifica che il carrello NON sia vuoto
        carrello.refresh_from_db()
        self.assertEqual(carrello.numero_articoli, 3)
    
    def test_cambio_stesso_negozio(self):
        """Test selezione dello stesso negozio non chiede conferma"""
        # Crea carrello con elementi
        TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            {self.prodotto1: 2}
        )
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        # Seleziona lo stesso negozio
        response = self.client.get(
            reverse('negozi:seleziona_preferito', args=[self.negozio1.id])
        )
        
        # Dovrebbe reindirizzare senza chiedere conferma
        self.assertEqual(response.status_code, 302)
        
        # Il carrello dovrebbe rimanere intatto
        carrello = Carrello.objects.get(utente=self.utente_normale)
        self.assertEqual(carrello.numero_articoli, 2)
