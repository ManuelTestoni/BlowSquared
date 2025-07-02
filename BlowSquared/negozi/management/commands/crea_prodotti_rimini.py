from django.core.management.base import BaseCommand
from prodotti.models import Prodotto
from negozi.models import Negozio, DisponibilitaProdotto
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Crea prodotti specifici di mare per il negozio di Rimini'
    
    def handle(self, *args, **options):
        self.stdout.write('🌊 Creazione prodotti di mare per Rimini...')
        
        # Trova il negozio di Rimini
        try:
            rimini = Negozio.objects.get(codice_negozio='BS003')
            self.stdout.write(f'✅ Trovato negozio: {rimini.nome}')
        except Negozio.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ Negozio di Rimini non trovato! Esegui prima crea_supermercati_emilia')
            )
            return
        
        # Prodotti specifici di mare per Rimini
        prodotti_mare = [
            {
                'nome': 'Ricci di Mare Freschi',
                'marca': 'Mare Adriatico',
                'categoria': 'fresco',
                'prezzo': Decimal('24.90'),
                'descrizione': 'Ricci di mare freschi pescati nel mare Adriatico, perfetti per un aperitivo gourmet o per preparare deliziosi primi piatti. Prodotto di alta qualità selezionato dai pescatori locali.',
                'ingredienti': 'Ricci di mare (Paracentrotus lividus) 100%',
                'peso': '250g (circa 6-8 ricci)',
                'codice_a_barre': '8055555000001',
                'stock': random.randint(15, 30),
                'data_scadenza': '2025-02-15',
                'sconto': 0,
                'valori_nutrizionali': {
                    'energia_kcal': 102,
                    'proteine': 12.8,
                    'carboidrati': 2.3,
                    'grassi': 5.1,
                    'sale': 1.2
                }
            },
            {
                'nome': 'Brodetto di Pesce Adriatico',
                'marca': 'Tradizioni Riminesi',
                'categoria': 'fresco',
                'prezzo': Decimal('18.50'),
                'descrizione': 'Mix di pesce fresco per brodetto tipico romagnolo: scorfano, gallinella, seppia, vongole e cozze. Perfetto per preparare il tradizionale brodetto adriatico.',
                'ingredienti': 'Scorfano, gallinella, seppia, vongole veraci, cozze, gamberetti',
                'peso': '1.2kg',
                'codice_a_barre': '8055555000002',
                'stock': random.randint(8, 15),
                'data_scadenza': '2025-01-20',
                'sconto': 10,
                'valori_nutrizionali': {
                    'energia_kcal': 95,
                    'proteine': 18.2,
                    'carboidrati': 1.1,
                    'grassi': 2.3,
                    'sale': 0.8
                }
            },
            {
                'nome': 'Vongole Veraci di Goro',
                'marca': 'Delta del Po',
                'categoria': 'fresco',
                'prezzo': Decimal('12.90'),
                'descrizione': 'Vongole veraci di Goro DOP, depurate e pronte da cucinare. Ideali per spaghetti alle vongole e risotti di mare. Provenienti dalle lagune del Delta del Po.',
                'ingredienti': 'Vongole veraci (Ruditapes philippinarum) 100%',
                'peso': '1kg',
                'codice_a_barre': '8055555000003',
                'stock': random.randint(20, 40),
                'data_scadenza': '2025-01-25',
                'sconto': 5,
                'valori_nutrizionali': {
                    'energia_kcal': 84,
                    'proteine': 14.2,
                    'carboidrati': 2.8,
                    'grassi': 1.9,
                    'sale': 2.1
                }
            },
            {
                'nome': 'Passatelli in Brodo di Pesce',
                'marca': 'Pasta Romagnola',
                'categoria': 'fresco',
                'prezzo': Decimal('8.90'),
                'descrizione': 'Passatelli freschi preparati secondo la tradizione romagnola, accompagnati da brodo di pesce concentrato. Piatto tipico della Romagna rivisitato in chiave marinara.',
                'ingredienti': 'Pane grattugiato, parmigiano reggiano, uova, noce moscata, brodo di pesce concentrato',
                'peso': '400g (2 porzioni)',
                'codice_a_barre': '8055555000004',
                'stock': random.randint(25, 45),
                'data_scadenza': '2025-01-30',
                'sconto': 0,
                'valori_nutrizionali': {
                    'energia_kcal': 245,
                    'proteine': 12.5,
                    'carboidrati': 28.3,
                    'grassi': 8.7,
                    'sale': 1.5
                }
            }
        ]
        
        prodotti_creati = []
        
        for prodotto_data in prodotti_mare:
            # Controlla se il prodotto esiste già
            if Prodotto.objects.filter(codice_a_barre=prodotto_data['codice_a_barre']).exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Prodotto {prodotto_data["nome"]} già esistente')
                )
                continue
            
            # Crea il prodotto
            prodotto = Prodotto.objects.create(
                nome=prodotto_data['nome'],
                marca=prodotto_data['marca'],
                categoria=prodotto_data['categoria'],
                prezzo=prodotto_data['prezzo'],
                descrizione=prodotto_data['descrizione'],
                ingredienti=prodotto_data['ingredienti'],
                peso=prodotto_data['peso'],
                codice_a_barre=prodotto_data['codice_a_barre'],
                stock=prodotto_data['stock'],
                data_scadenza=prodotto_data['data_scadenza'],
                sconto=prodotto_data['sconto'],
                valori_nutrizionali=prodotto_data['valori_nutrizionali']
            )
            
            prodotti_creati.append(prodotto)
            
            # Crea la disponibilità SOLO per Rimini
            DisponibilitaProdotto.objects.create(
                negozio=rimini,
                prodotto=prodotto,
                quantita_disponibile=prodotto_data['stock'],
                quantita_minima=5,
                quantita_massima=prodotto_data['stock'] * 2,
                settore='Reparto Fresco Mare',
                corridoio='C1',
                scaffale=f"SM{random.randint(1, 4)}",  # SM = Specialità Mare
                vendite_giornaliere_media=random.uniform(2.0, 8.0)
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Creato: {prodotto.nome} - €{prodotto.prezzo}')
            )
        
        self.stdout.write(f'\n🎉 Operazione completata!')
        self.stdout.write(f'🌊 {len(prodotti_creati)} prodotti di mare creati per Rimini')
        self.stdout.write(f'🏪 Disponibili esclusivamente presso: {rimini.nome}')
        self.stdout.write('\n📍 Prodotti aggiunti:')
        for prodotto in prodotti_creati:
            sconto_text = f' (SCONTO {prodotto.sconto}%)' if prodotto.sconto > 0 else ''
            self.stdout.write(f'   • {prodotto.nome} - €{prodotto.prezzo}{sconto_text}')
        
        self.stdout.write(f'\n🔧 Ora il negozio di Rimini ha un catalogo unico con specialità marine!')
        self.stdout.write(f'🛒 Gli utenti che scelgono Rimini vedranno questi prodotti esclusivi')
