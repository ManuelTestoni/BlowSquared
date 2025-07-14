"""
Test per la Performance e Stress Test
"""
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
import time

from tests.test_base import BaseTestCase, TestUtilities
from carrello.models import Carrello, ElementoCarrello
from prodotti.models import Prodotto


class PerformanceTest(BaseTestCase):
    """Test di performance per operazioni critiche"""
    
    def test_performance_aggiunta_multipla_carrello(self):
        """Test performance aggiunta multipla al carrello"""
        from datetime import date, timedelta
        
        TestUtilities.login_user(self.client, self.utente_normale)
        
        # Crea molti prodotti
        prodotti = []
        for i in range(50):
            prodotto = Prodotto.objects.create(
                nome=f'Prodotto Test {i}',
                marca='Test Brand',
                categoria='pasta',
                descrizione=f'Descrizione {i}',
                codice_a_barre=f'123456789{i:04d}',
                peso='100g',
                data_scadenza=date.today() + timedelta(days=365),
                prezzo=Decimal('1.00')
            )
            self.negozio1.prodotti_disponibili.add(prodotto)
            prodotti.append(prodotto)
        
        # Test aggiunta sequenziale
        start_time = time.time()
        
        for i, prodotto in enumerate(prodotti[:10]):  # Testa primi 10
            response = self.client.post(
                f'/carrello/aggiungi/{prodotto.id}/',
                {'quantita': 1},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEqual(response.status_code, 200)
        
        elapsed_time = time.time() - start_time
        
        # Dovrebbe completare in meno di 5 secondi
        self.assertLess(elapsed_time, 5.0, 
                       f"Aggiunta multipla troppo lenta: {elapsed_time:.2f}s")
    
    def test_performance_calcolo_subtotale(self):
        """Test performance calcolo subtotale con molti elementi"""
        from datetime import date, timedelta
        
        # Crea carrello con molti elementi
        carrello_items = {}
        for i in range(100):
            prodotto = Prodotto.objects.create(
                nome=f'Prodotto {i}',
                marca='Test Brand',
                categoria='pasta',
                descrizione=f'Desc {i}',
                codice_a_barre=f'987654321{i:04d}',
                peso='100g',
                data_scadenza=date.today() + timedelta(days=365),
                prezzo=Decimal(f'{i % 10 + 1}.00')
            )
            carrello_items[prodotto] = i % 5 + 1
        
        carrello = TestUtilities.create_carrello_with_items(
            self.utente_normale,
            self.negozio1,
            carrello_items
        )
        
        # Test calcolo subtotale
        start_time = time.time()
        
        for _ in range(10):  # Calcola 10 volte
            subtotale = carrello.subtotale
        
        elapsed_time = time.time() - start_time
        
        # Dovrebbe essere veloce anche con molti elementi
        self.assertLess(elapsed_time, 1.0,
                       f"Calcolo subtotale troppo lento: {elapsed_time:.2f}s")


class StressTest(TransactionTestCase):
    """Stress test per situazioni di carico"""
    
    def setUp(self):
        """Setup per stress test"""
        super().setUp()
        
        # Crea setup base
        self.setup_base_data()
    
    def setup_base_data(self):
        """Setup dati base per stress test"""
        from negozi.models import Negozio
        from prodotti.models import Prodotto
        from datetime import date, timedelta
        
        self.negozio = Negozio.objects.create(
            nome='Stress Test Store',
            codice_negozio='STS001',
            indirizzo='Via Test',
            cap='41100',
            citta='Modena',
            provincia='MO',
            regione='Emilia-Romagna',
            telefono='1234567890',
            latitudine=Decimal('44.6471700'),
            longitudine=Decimal('10.9251400'),
            data_apertura=date(2020, 1, 1),
            attivo=True
        )
        
        self.categoria = 'pasta'
        
        self.prodotto = Prodotto.objects.create(
            nome='Stress Product',
            marca='Test Brand',
            categoria=self.categoria,
            descrizione='Per stress test',
            codice_a_barre='0000000000001',
            peso='100g',
            data_scadenza=date.today() + timedelta(days=365),
            prezzo=Decimal('1.00')
        )
        
        self.negozio.prodotti_disponibili.add(self.prodotto)
    
    def test_concurrent_cart_operations(self):
        """Test operazioni concorrenti sul carrello"""
        # Crea multipli utenti
        users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'stress_user_{i}',
                email=f'stress{i}@test.com',
                password='testpass123'
            )
            user.profilo.negozio_preferito = self.negozio
            user.profilo.save()
            users.append(user)
        
        # Simula operazioni concorrenti
        for user in users:
            with transaction.atomic():
                carrello, created = Carrello.objects.get_or_create(
                    utente=user,
                    defaults={'negozio': self.negozio}
                )
                
                ElementoCarrello.objects.create(
                    carrello=carrello,
                    prodotto=self.prodotto,
                    quantita=1
                )
        
        # Verifica che tutti abbiano il carrello
        for user in users:
            carrello = Carrello.objects.get(utente=user)
            self.assertEqual(carrello.numero_articoli, 1)
    
    def test_memory_usage_large_cart(self):
        """Test utilizzo memoria con carrello molto grande"""
        user = User.objects.create_user(
            username='memory_test_user',
            email='memory@test.com',
            password='testpass123'
        )
        user.profilo.negozio_preferito = self.negozio
        user.profilo.save()
        
        carrello = Carrello.objects.create(
            utente=user,
            negozio=self.negozio
        )
        
        # Crea molti elementi carrello
        elementi = []
        for i in range(1000):
            elemento = ElementoCarrello(
                carrello=carrello,
                prodotto=self.prodotto,
                quantita=1
            )
            elementi.append(elemento)
        
        # Inserimento bulk per efficienza
        ElementoCarrello.objects.bulk_create(elementi)
        
        # Test che il sistema gestisca il carico
        self.assertEqual(carrello.numero_articoli, 1000)
        
        # Test svuotamento
        start_time = time.time()
        carrello.svuota_carrello()
        elapsed_time = time.time() - start_time
        
        # Dovrebbe svuotare rapidamente anche un carrello grande
        self.assertLess(elapsed_time, 2.0,
                       f"Svuotamento carrello grande troppo lento: {elapsed_time:.2f}s")
        
        self.assertEqual(carrello.numero_articoli, 0)
