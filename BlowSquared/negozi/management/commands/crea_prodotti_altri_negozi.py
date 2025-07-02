from django.core.management.base import BaseCommand
from prodotti.models import Prodotto
from negozi.models import Negozio, DisponibilitaProdotto
import random

class Command(BaseCommand):
    help = 'Popola gli altri negozi con i prodotti generici (escludendo quelli specifici di Rimini)'
    
    def handle(self, *args, **options):
        self.stdout.write('🏪 Popolamento negozi con prodotti generici...')
        
        # Trova tutti i negozi eccetto Rimini
        negozi = Negozio.objects.exclude(codice_negozio='BS003')
        
        # Prodotti specifici di Rimini da escludere (SOLO quelli di mare)
        codici_rimini = [
            '8055555000001',  # Ricci di Mare
            '8055555000002',  # Brodetto 
            '8055555000003',  # Vongole
            '8055555000004',  # Passatelli
            # Rimosso il Lambrusco - ora è disponibile per tutti i negozi
        ]
        
        # Recupera tutti i prodotti ECCETTO quelli specifici di Rimini
        prodotti_generici = Prodotto.objects.exclude(codice_a_barre__in=codici_rimini)
        
        self.stdout.write(f'📦 {prodotti_generici.count()} prodotti generici da distribuire')
        self.stdout.write(f'🏪 {negozi.count()} negozi da popolare')
        
        for negozio in negozi:
            self.stdout.write(f'\n🏢 Popolamento {negozio.nome}...')
            
            prodotti_aggiunti = 0
            
            # Ogni negozio ha l'85-95% dei prodotti generici disponibili
            percentuale_disponibilita = random.uniform(0.85, 0.95)
            num_prodotti_da_aggiungere = int(len(prodotti_generici) * percentuale_disponibilita)
            
            # Seleziona prodotti random
            prodotti_negozio = random.sample(list(prodotti_generici), num_prodotti_da_aggiungere)
            
            for prodotto in prodotti_negozio:
                # Verifica se la disponibilità esiste già
                if DisponibilitaProdotto.objects.filter(negozio=negozio, prodotto=prodotto).exists():
                    continue
                
                # Quantità variabile per settore
                if prodotto.categoria in ['fresco', 'latticini']:
                    quantita = random.randint(15, 60)
                elif prodotto.categoria in ['surgelati']:
                    quantita = random.randint(8, 40)
                else:
                    quantita = random.randint(25, 120)
                
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
                
                # Prezzi locali occasionali (3% dei prodotti)
                prezzo_locale = None
                sconto_locale = 0
                in_promozione = False
                
                if random.random() < 0.03:  # 3% di probabilità
                    sconto_locale = random.uniform(3, 15)
                    in_promozione = True
                
                DisponibilitaProdotto.objects.create(
                    negozio=negozio,
                    prodotto=prodotto,
                    quantita_disponibile=quantita,
                    quantita_minima=random.randint(5, 15),
                    quantita_massima=quantita * 2,
                    settore=settore,
                    corridoio=corridoio,
                    scaffale=scaffale,
                    prezzo_locale=prezzo_locale,
                    in_promozione_locale=in_promozione,
                    sconto_locale=sconto_locale,
                    vendite_giornaliere_media=random.uniform(1.0, 6.0)
                )
                
                prodotti_aggiunti += 1
            
            self.stdout.write(f'  ✅ {prodotti_aggiunti} prodotti aggiunti')
        
        self.stdout.write(f'\n🎉 Operazione completata!')
        self.stdout.write(f'📋 Ora ogni negozio ha il suo catalogo specifico:')
        self.stdout.write(f'   • Rimini: Prodotti generici + Specialità marine esclusive')
        self.stdout.write(f'   • Altri negozi: Solo prodotti generici')
        self.stdout.write(f'\n🔧 I cataloghi sono ora differenziati per negozio!')
