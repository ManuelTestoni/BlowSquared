from django.core.management.base import BaseCommand
from prodotti.models import Prodotto
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Popola il database con prodotti d\'eccellenza'

    def handle(self, *args, **options):
        prodotti_da_creare = [
            {
                'nome': 'Aceto Balsamico Tradizionale di Modena DOP Extravecchio',
                'marca': 'Acetaia San Giacomo',
                'categoria': 'olio',
                'descrizione': 'Aceto balsamico tradizionale di Modena DOP invecchiato oltre 25 anni. Prodotto di eccellenza assoluta, simbolo del lusso gastronomico italiano. Ogni bottiglia è numerata e certificata dal Consorzio di Tutela.',
                'codice_a_barre': '8011111000001',
                'peso': '100ml',
                'data_scadenza': date.today() + timedelta(days=3650),  # 10 anni
                'foto': 'prodotti/aceto_balsamico_tradizionale_modena_dop_extravecchio.png',
                'valori_nutrizionali': {
                    'energia_kcal': 88,
                    'grassi': 0,
                    'carboidrati': 17,
                    'proteine': 0.5,
                    'sale': 0.01
                },
                'prezzo': Decimal('89.90'),
                'sconto': Decimal('0'),
                'stock': 15,
                'ingredienti': 'Mosto di uve Trebbiano e Lambrusco di Modena. Invecchiato in batterie di botti di legni diversi (rovere, castagno, ciliegio, frassino, gelso)',
                'numero_recensioni': 47
            },
            {
                'nome': 'Parmigiano Reggiano Biologico 36 Mesi',
                'marca': 'Caseificio Sociale Bio della Montagna',
                'categoria': 'latticini',
                'descrizione': 'Parmigiano Reggiano biologico stagionato 36 mesi, prodotto con latte di mucche allevate al pascolo secondo i principi dell\'agricoltura biologica. Sapore intenso e cristalli di calcio che scricchiolano.',
                'codice_a_barre': '8022222000002',
                'peso': '1kg',
                'data_scadenza': date.today() + timedelta(days=180),
                'foto': 'prodotti/parmigiano_reggiano_biologico_36_mesi.png',
                'valori_nutrizionali': {
                    'energia_kcal': 392,
                    'grassi': 28.1,
                    'carboidrati': 0,
                    'proteine': 32.7,
                    'sale': 1.39,
                    'calcio': 1184
                },
                'prezzo': Decimal('42.50'),
                'sconto': Decimal('5'),
                'stock': 28,
                'ingredienti': 'Latte biologico, sale, caglio. Senza conservanti, senza OGM',
                'numero_recensioni': 156
            },
            {
                'nome': 'Tortellini in Brodo di Cappone Artigianali',
                'marca': 'Pasta Fresca della Nonna Maria',
                'categoria': 'pasta',
                'descrizione': 'Tortellini freschi fatti a mano secondo la tradizione bolognese, con ripieno di prosciutto di Parma, mortadella, Parmigiano Reggiano 24 mesi. Serviti con brodo di cappone ruspante dell\'Appennino emiliano.',
                'codice_a_barre': '8033333000003',
                'peso': '500g + 1L brodo',
                'data_scadenza': date.today() + timedelta(days=5),
                'foto': 'prodotti/tortellini_brodo_cappone_artigianali.png',
                'valori_nutrizionali': {
                    'energia_kcal': 285,
                    'grassi': 12.5,
                    'carboidrati': 32.1,
                    'proteine': 14.8,
                    'sale': 0.95
                },
                'prezzo': Decimal('18.90'),
                'sconto': Decimal('0'),
                'stock': 12,
                'ingredienti': 'Pasta: farina di grano tenero tipo 00, uova fresche. Ripieno: prosciutto di Parma DOP, mortadella IGP, Parmigiano Reggiano DOP, noce moscata. Brodo: cappone, carote, sedano, cipolla, sale.',
                'numero_recensioni': 89
            },
            {
                'nome': 'Lambrusco di Sorbara DOC Secco Biologico',
                'marca': 'Cantina Sociale di Carpi e Sorbara',
                'categoria': 'bevande',
                'descrizione': 'Lambrusco di Sorbara DOC secco biologico, vitigno autoctono modenese. Vino frizzante dal colore rosso rubino con spuma rosata, profumo intenso e sapore asciutto. Perfetto con i salumi emiliani.',
                'codice_a_barre': '8044444000004',
                'peso': '750ml',
                'data_scadenza': date.today() + timedelta(days=1095),  # 3 anni
                'foto': 'prodotti/lambrusco_sorbara_doc_secco_biologico.png',
                'valori_nutrizionali': {
                    'energia_kcal': 83,
                    'grassi': 0,
                    'carboidrati': 2.5,
                    'proteine': 0.1,
                    'alcol': 11.5
                },
                'prezzo': Decimal('12.50'),
                'sconto': Decimal('10'),
                'stock': 45,
                'ingredienti': 'Uve Lambrusco di Sorbara 100% biologiche, solfiti (< 100mg/L)',
                'numero_recensioni': 72
            }
        ]

        for prodotto_data in prodotti_da_creare:
            prodotto, created = Prodotto.objects.get_or_create(
                codice_a_barre=prodotto_data['codice_a_barre'],
                defaults=prodotto_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Prodotto creato: {prodotto.nome}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Prodotto già esistente: {prodotto.nome}')
                )

        self.stdout.write(
            self.style.SUCCESS('Popolamento completato con successo!')
        )
