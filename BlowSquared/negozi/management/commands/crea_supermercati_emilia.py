from django.core.management.base import BaseCommand
from negozi.models import Negozio
from prodotti.models import Prodotto
from negozi.models import DisponibilitaProdotto
from datetime import date
import random

class Command(BaseCommand):
    help = 'Crea supermercati strategici in Emilia-Romagna con inventario'
    
    def handle(self, *args, **options):
        self.stdout.write('🏪 Creazione supermercati BlowSquared in Emilia-Romagna...')
        
        # Dati dei supermercati strategici
        supermercati_data = [
            {
                'nome': 'BlowSquared Modena Centro',
                'codice_negozio': 'BS001',
                'indirizzo': 'Via Emilia Centro, 123',
                'cap': '41121',
                'citta': 'Modena',
                'provincia': 'MO',
                'latitudine': 44.6471700,
                'longitudine': 10.9251400,
                'telefono': '059-123456',
                'email': 'modena@blowsquared.it',
                'superficie_mq': 2500,
                'numero_casse': 8,
                'posti_parcheggio': 150,
                'servizio_farmacia': True,
                'servizio_panetteria': True,
                'servizio_macelleria': True,
                'servizio_pescheria': True,
                'direttore': 'Dott. Marco Rossi',
                'orari': {
                    'lunedi': '08:00-20:00',
                    'martedi': '08:00-20:00',
                    'mercoledi': '08:00-20:00',
                    'giovedi': '08:00-20:00',
                    'venerdi': '08:00-20:00',
                    'sabato': '08:00-20:00',
                    'domenica': '09:00-19:00'
                }
            },
            {
                'nome': 'BlowSquared Bologna Borgo Panigale',
                'codice_negozio': 'BS002',
                'indirizzo': 'Via Marco Emilio Lepido, 456',
                'cap': '40132',
                'citta': 'Bologna',
                'provincia': 'BO',
                'latitudine': 44.5075100,
                'longitudine': 11.2710700,
                'telefono': '051-789012',
                'email': 'bologna@blowsquared.it',
                'superficie_mq': 3200,
                'numero_casse': 12,
                'posti_parcheggio': 200,
                'servizio_farmacia': True,
                'servizio_panetteria': True,
                'servizio_macelleria': True,
                'servizio_pescheria': True,
                'direttore': 'Dott.ssa Laura Bianchi',
                'orari': {
                    'lunedi': '07:30-21:00',
                    'martedi': '07:30-21:00',
                    'mercoledi': '07:30-21:00',
                    'giovedi': '07:30-21:00',
                    'venerdi': '07:30-21:00',
                    'sabato': '07:30-21:00',
                    'domenica': '08:30-20:00'
                }
            },
            {
                'nome': 'BlowSquared Rimini Mare',
                'codice_negozio': 'BS003',
                'indirizzo': 'Viale Vespucci, 789',
                'cap': '47921',
                'citta': 'Rimini',
                'provincia': 'RN',
                'latitudine': 44.0678800,
                'longitudine': 12.5664600,
                'telefono': '0541-345678',
                'email': 'rimini@blowsquared.it',
                'superficie_mq': 2000,
                'numero_casse': 6,
                'posti_parcheggio': 100,
                'servizio_farmacia': False,
                'servizio_panetteria': True,
                'servizio_macelleria': True,
                'servizio_pescheria': True,
                'direttore': 'Dott. Giuseppe Verdi',
                'orari': {
                    'lunedi': '08:00-20:00',
                    'martedi': '08:00-20:00',
                    'mercoledi': '08:00-20:00',
                    'giovedi': '08:00-20:00',
                    'venerdi': '08:00-20:00',
                    'sabato': '08:00-20:00',
                    'domenica': '09:00-19:00'
                }
            }
        ]
        
        negozi_creati = []
        
        for data in supermercati_data:
            # Controlla se il negozio esiste già
            if Negozio.objects.filter(codice_negozio=data['codice_negozio']).exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Negozio {data["nome"]} già esistente')
                )
                continue
            
            # Crea il negozio
            negozio = Negozio.objects.create(
                nome=data['nome'],
                codice_negozio=data['codice_negozio'],
                indirizzo=data['indirizzo'],
                cap=data['cap'],
                citta=data['citta'],
                provincia=data['provincia'],
                regione='Emilia-Romagna',
                nazione='Italia',
                latitudine=data['latitudine'],
                longitudine=data['longitudine'],
                telefono=data['telefono'],
                email=data['email'],
                superficie_mq=data['superficie_mq'],
                numero_casse=data['numero_casse'],
                parcheggio_disponibile=True,
                posti_parcheggio=data['posti_parcheggio'],
                servizio_farmacia=data['servizio_farmacia'],
                servizio_panetteria=data['servizio_panetteria'],
                servizio_macelleria=data['servizio_macelleria'],
                servizio_pescheria=data['servizio_pescheria'],
                servizio_consegna_domicilio=True,
                ritiro_click_collect=True,
                direttore=data['direttore'],
                data_apertura=date(2020, 6, 15),
                orari_apertura=data['orari'],
                attivo=True
            )
            
            negozi_creati.append(negozio)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Creato {negozio.nome} - {negozio.citta}')
            )
        
        # Popola inventario per ogni negozio
        self.stdout.write('\n📦 Creazione inventario prodotti...')
        
        # Recupera tutti i prodotti
        prodotti = list(Prodotto.objects.all())
        
        if not prodotti:
            self.stdout.write(
                self.style.WARNING('⚠️  Nessun prodotto trovato. Popola prima i prodotti!')
            )
            return
        
        for negozio in negozi_creati:
            prodotti_aggiunti = 0
            
            # Ogni negozio ha l'80-95% dei prodotti disponibili
            percentuale_disponibilita = random.uniform(0.80, 0.95)
            num_prodotti_da_aggiungere = int(len(prodotti) * percentuale_disponibilita)
            
            # Seleziona prodotti random
            prodotti_negozio = random.sample(prodotti, num_prodotti_da_aggiungere)
            
            for prodotto in prodotti_negozio:
                # Quantità variabile per settore
                if prodotto.categoria in ['fresco', 'latticini']:
                    quantita = random.randint(10, 50)
                elif prodotto.categoria in ['surgelati']:
                    quantita = random.randint(5, 30)
                else:
                    quantita = random.randint(20, 100)
                
                # Settore del negozio
                settore_mapping = {
                    'fresco': 'Reparto Fresco',
                    'latticini': 'Reparto Fresco',
                    'surgelati': 'Reparto Surgelati',
                    'conserve': 'Reparto Secco',
                    'bevande': 'Reparto Bevande',
                    'dolci': 'Reparto Dolci',
                    'condimenti': 'Reparto Secco'
                }
                
                settore = settore_mapping.get(prodotto.categoria, 'Reparto Generale')
                corridoio = f"C{random.randint(1, 12)}"
                scaffale = f"S{random.randint(1, 8)}"
                
                # Prezzi locali occasionali (5% dei prodotti)
                prezzo_locale = None
                sconto_locale = 0
                in_promozione = False
                
                if random.random() < 0.05:  # 5% di probabilità
                    # Sconto locale aggiuntivo
                    sconto_locale = random.uniform(5, 20)
                    in_promozione = True
                
                DisponibilitaProdotto.objects.create(
                    negozio=negozio,
                    prodotto=prodotto,
                    quantita_disponibile=quantita,
                    quantita_minima=random.randint(3, 10),
                    quantita_massima=quantita * 2,
                    settore=settore,
                    corridoio=corridoio,
                    scaffale=scaffale,
                    prezzo_locale=prezzo_locale,
                    in_promozione_locale=in_promozione,
                    sconto_locale=sconto_locale,
                    vendite_giornaliere_media=random.uniform(0.5, 5.0)
                )
                
                prodotti_aggiunti += 1
            
            self.stdout.write(
                f'  📋 {negozio.nome}: {prodotti_aggiunti} prodotti aggiunti'
            )
        
        self.stdout.write('\n🎉 Setup completato!')
        self.stdout.write(f'✅ {len(negozi_creati)} supermercati creati in Emilia-Romagna')
        self.stdout.write('✅ Inventario popolato per tutti i negozi')
        self.stdout.write('\n📍 Località coperte:')
        for negozio in negozi_creati:
            self.stdout.write(f'   • {negozio.citta} ({negozio.provincia}) - {negozio.nome}')
        
        self.stdout.write(f'\n🔧 Per testare la geolocalizzazione, registra un nuovo utente!')
