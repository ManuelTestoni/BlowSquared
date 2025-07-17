"""
Test Suite per BlowSquared - Configurazione Base
"""
import os
import django
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal

# Models
from utenti.models import ProfiloUtente
from negozi.models import Negozio
from prodotti.models import Prodotto
from carrello.models import Carrello, ElementoCarrello
from dipendenti.models import Dipendente
from dirigenti.models import Dirigente


class BaseTestCase(TestCase):
    """Classe base per tutti i test con setup comune"""
    
    def setUp(self):
        """Setup comune per tutti i test"""
        # Creazione utenti
        self.utente_normale = User.objects.create_user(
            username='utente_test',
            email='utente@test.com',
            password='testpass123'
        )
        
        self.dipendente_user = User.objects.create_user(
            username='dipendente_test',
            email='dipendente@test.com', 
            password='testpass123'
        )
        
        self.dirigente_user = User.objects.create_user(
            username='dirigente_test',
            email='dirigente@test.com',
            password='testpass123'
        )
        
        # Creazione negozi
        from datetime import date
        
        self.negozio1 = Negozio.objects.create(
            nome='Blow Squared Centro',
            codice_negozio='BS001',
            indirizzo='Via Roma 1',
            cap='41100',
            citta='Modena',
            provincia='MO',
            regione='Emilia-Romagna',
            telefono='0123456789',
            data_apertura=date(2020, 1, 15),
            attivo=True
        )
        
        self.negozio2 = Negozio.objects.create(
            nome='Blow Squared Periferia',
            codice_negozio='BS002',
            indirizzo='Via Milano 10',
            cap='41100',
            citta='Modena',
            provincia='MO',
            regione='Emilia-Romagna',
            telefono='0987654321',
            data_apertura=date(2021, 3, 20),
            attivo=True
        )
        
        # Creazione profili utente
        self.profilo_utente = ProfiloUtente.objects.create(
            user=self.utente_normale,
            citta='Modena',
            provincia='MO',
            negozio_preferito=self.negozio1
        )
        
        # Creazione dipendente e dirigente
        self.dipendente = Dipendente.objects.create(
            user=self.dipendente_user,
            nome='Mario',
            cognome='Rossi',
            eta=30,
            telefono='3331234567',
            negozio=self.negozio1
        )
        
        self.dirigente = Dirigente.objects.create(
            user=self.dirigente_user,
            nome='Giuseppe',
            cognome='Verdi',
            eta=45,
            telefono='3339876543',
            livello_accesso='direttore_negozio',
            negozio_principale=self.negozio1
        )
        
        # Creazione prodotti
        from datetime import date, timedelta
        
        self.prodotto1 = Prodotto.objects.create(
            nome='Pasta Barilla',
            marca='Barilla',
            categoria='pasta',
            descrizione='Pasta di semola di grano duro',
            codice_a_barre='1234567890123',
            peso='500g',
            data_scadenza=date.today() + timedelta(days=365),
            prezzo=Decimal('1.50')
        )
        
        self.prodotto2 = Prodotto.objects.create(
            nome='Pane Integrale',
            marca='Pane & Co',
            categoria='conserve',
            descrizione='Pane integrale fresco',
            codice_a_barre='9876543210987',
            peso='400g',
            data_scadenza=date.today() + timedelta(days=7),
            prezzo=Decimal('2.00')
        )
        
        # Aggiunta prodotti ai negozi
        self.negozio1.prodotti_disponibili.add(self.prodotto1, self.prodotto2)
        self.negozio2.prodotti_disponibili.add(self.prodotto1)
        
        # Client per le richieste HTTP
        self.client = Client()


class TestUtilities:
    """Utility class per funzioni di supporto ai test"""
    
    @staticmethod
    def login_user(client, user):
        """Helper per login utente"""
        return client.login(username=user.username, password='testpass123')
    
    @staticmethod
    def create_carrello_with_items(user, negozio, prodotti_quantita=None):
        """Helper per creare carrello con elementi
        prodotti_quantita: dict {prodotto: quantita}
        """
        if prodotti_quantita is None:
            return None
            
        carrello, created = Carrello.objects.get_or_create(
            utente=user,
            defaults={'negozio': negozio}
        )
        
        for prodotto, quantita in prodotti_quantita.items():
            ElementoCarrello.objects.create(
                carrello=carrello,
                prodotto=prodotto,
                quantita=quantita
            )
        
        return carrello
