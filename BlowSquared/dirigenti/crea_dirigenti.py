"""
Script per creare dirigenti di test nel database.
Esegui con: python manage.py shell < dirigenti/crea_dirigenti.py
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlowSquared.settings')
django.setup()

from django.contrib.auth.models import User
from dirigenti.models import Dirigente
from negozi.models import Negozio

def crea_dirigenti():
    print("🏢 === INIZIO CREAZIONE DIRIGENTI ===")
    
    # Verifica negozi esistenti
    negozi = Negozio.objects.all()
    print(f"🏪 Negozi disponibili: {negozi.count()}")
    
    if negozi.count() == 0:
        print("❌ Nessun negozio trovato! Crea prima i negozi.")
        return
    
    # Trova negozi specifici
    bologna = negozi.filter(citta__icontains='bologna').first()
    modena = negozi.filter(citta__icontains='modena').first()
    rimini = negozi.filter(citta__icontains='rimini').first()
    
    print(f"🎯 Negozi identificati:")
    print(f"   - BOLOGNA: {bologna.nome if bologna else 'NON TROVATO'}")
    print(f"   - MODENA: {modena.nome if modena else 'NON TROVATO'}")
    print(f"   - RIMINI: {rimini.nome if rimini else 'NON TROVATO'}")
    
    # Dirigente 1 - Direttore Generale
    print("\n👔 Creazione Direttore Generale...")
    try:
        if User.objects.filter(username='alessandro.verdi').exists():
            print("🗑️ Rimuovo utente esistente: alessandro.verdi")
            User.objects.filter(username='alessandro.verdi').delete()
        
        user1 = User.objects.create_user(
            username='alessandro.verdi',
            email='alessandro.verdi@blowsquared.com',
            password='password123',
            first_name='Alessandro',
            last_name='Verdi'
        )
        print(f"✅ Utente creato: {user1.username} - Email: {user1.email}")
        
        dirigente1 = Dirigente.objects.create(
            user=user1,
            nome='Alessandro',
            cognome='Verdi',
            eta=45,
            telefono='051-7654321',
            indirizzo='Via Roma 456, Bologna',
            data_nascita=date(1978, 3, 15),
            livello_accesso='direttore_generale',
            negozio_principale=bologna if bologna else negozi.first(),
            data_assunzione=date(2010, 1, 15),
            stipendio_base=75000.00,
            note_direzione='Direttore Generale con piena autonomia decisionale su tutti i negozi della catena.'
        )
        
        # Il direttore generale ha accesso a tutti i negozi
        dirigente1.negozi_supervisionati.set(negozi.all())
        
        print(f"✅ Dirigente creato: {dirigente1.nome} {dirigente1.cognome} - {dirigente1.get_livello_accesso_display()}")
        print(f"   Negozio principale: {dirigente1.negozio_principale.nome}")
        print(f"   Negozi supervisionati: {dirigente1.negozi_supervisionati.count()} (tutti)")
        
    except Exception as e:
        print(f"❌ ERRORE creazione direttore generale: {e}")
        import traceback
        traceback.print_exc()
    
    # Dirigente 2 - Vice Direttore
    print("\n👩‍💼 Creazione Vice Direttore...")
    try:
        if User.objects.filter(username='sofia.bianchi').exists():
            print("🗑️ Rimuovo utente esistente: sofia.bianchi")
            User.objects.filter(username='sofia.bianchi').delete()
        
        user2 = User.objects.create_user(
            username='sofia.bianchi',
            email='sofia.bianchi@blowsquared.com',
            password='password123',
            first_name='Sofia',
            last_name='Bianchi'
        )
        print(f"✅ Utente creato: {user2.username} - Email: {user2.email}")
        
        dirigente2 = Dirigente.objects.create(
            user=user2,
            nome='Sofia',
            cognome='Bianchi',
            eta=38,
            telefono='059-1234567',
            indirizzo='Corso Vittorio Emanuele 789, Modena',
            data_nascita=date(1985, 7, 22),
            livello_accesso='vice_direttore',
            negozio_principale=modena if modena else negozi.first(),
            data_assunzione=date(2015, 9, 1),
            stipendio_base=55000.00,
            note_direzione='Vice Direttore specializzata in operations e supply chain management.'
        )
        
        # Il vice direttore supervisiona tutti i negozi tranne quello principale
        altri_negozi = negozi.exclude(id=dirigente2.negozio_principale.id)
        dirigente2.negozi_supervisionati.set(altri_negozi)
        
        print(f"✅ Dirigente creato: {dirigente2.nome} {dirigente2.cognome} - {dirigente2.get_livello_accesso_display()}")
        print(f"   Negozio principale: {dirigente2.negozio_principale.nome}")
        print(f"   Negozi supervisionati: {dirigente2.negozi_supervisionati.count()}")
        
    except Exception as e:
        print(f"❌ ERRORE creazione vice direttore: {e}")
        import traceback
        traceback.print_exc()
    
    # Dirigente 3 - Direttore di Negozio (Bologna)
    if bologna:
        print("\n🏪 Creazione Direttore Negozio Bologna...")
        try:
            if User.objects.filter(username='marco.rossi.dir').exists():
                print("🗑️ Rimuovo utente esistente: marco.rossi.dir")
                User.objects.filter(username='marco.rossi.dir').delete()
            
            user3 = User.objects.create_user(
                username='marco.rossi.dir',
                email='marco.rossi.dir@blowsquared.com',
                password='password123',
                first_name='Marco',
                last_name='Rossi'
            )
            print(f"✅ Utente creato: {user3.username} - Email: {user3.email}")
            
            dirigente3 = Dirigente.objects.create(
                user=user3,
                nome='Marco',
                cognome='Rossi',
                eta=42,
                telefono='051-9876543',
                indirizzo='Via Indipendenza 321, Bologna',
                data_nascita=date(1981, 11, 8),
                livello_accesso='direttore_negozio',
                negozio_principale=bologna,
                data_assunzione=date(2018, 3, 15),
                stipendio_base=40000.00,
                note_direzione='Direttore del negozio di Bologna, responsabile delle performance locali.'
            )
            
            # Non aggiungiamo negozi supervisionati per un direttore di negozio
            
            print(f"✅ Dirigente creato: {dirigente3.nome} {dirigente3.cognome} - {dirigente3.get_livello_accesso_display()}")
            print(f"   Negozio principale: {dirigente3.negozio_principale.nome}")
            
        except Exception as e:
            print(f"❌ ERRORE creazione direttore negozio: {e}")
            import traceback
            traceback.print_exc()
    
    # Dirigente 4 - Manager di Area (se ci sono abbastanza negozi)
    if negozi.count() >= 2:
        print("\n🌍 Creazione Manager di Area...")
        try:
            if User.objects.filter(username='laura.ferrari').exists():
                print("🗑️ Rimuovo utente esistente: laura.ferrari")
                User.objects.filter(username='laura.ferrari').delete()
            
            user4 = User.objects.create_user(
                username='laura.ferrari',
                email='laura.ferrari@blowsquared.com',
                password='password123',
                first_name='Laura',
                last_name='Ferrari'
            )
            print(f"✅ Utente creato: {user4.username} - Email: {user4.email}")
            
            dirigente4 = Dirigente.objects.create(
                user=user4,
                nome='Laura',
                cognome='Ferrari',
                eta=35,
                telefono='0541-654321',
                indirizzo='Via Mare 12, Rimini',
                data_nascita=date(1988, 4, 18),
                livello_accesso='manager_area',
                negozio_principale=rimini if rimini else negozi.last(),
                data_assunzione=date(2020, 6, 1),
                stipendio_base=35000.00,
                note_direzione='Manager di Area responsabile della zona Emilia-Romagna.'
            )
            
            # Manager di area supervisiona alcuni negozi (escludendo il principale)
            if modena:
                dirigente4.negozi_supervisionati.add(modena)
            
            print(f"✅ Dirigente creato: {dirigente4.nome} {dirigente4.cognome} - {dirigente4.get_livello_accesso_display()}")
            print(f"   Negozio principale: {dirigente4.negozio_principale.nome}")
            print(f"   Negozi supervisionati: {dirigente4.negozi_supervisionati.count()}")
            
        except Exception as e:
            print(f"❌ ERRORE creazione manager di area: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 === CREAZIONE DIRIGENTI COMPLETATA ===")
    print("\n📋 CREDENZIALI PER IL TEST:")
    print("=" * 60)
    print("🏢 Direttore Generale:")
    print("   Username: alessandro.verdi")
    print("   Email: alessandro.verdi@blowsquared.com")
    print("   Password: password123")
    print("   Accesso: TUTTI I NEGOZI")
    print()
    print("🏢 Vice Direttore:")
    print("   Username: sofia.bianchi")
    print("   Email: sofia.bianchi@blowsquared.com")
    print("   Password: password123")
    print("   Accesso: TUTTI I NEGOZI")
    print()
    print("🏪 Direttore Negozio (Bologna):")
    print("   Username: marco.rossi.dir")
    print("   Email: marco.rossi.dir@blowsquared.com")
    print("   Password: password123")
    print("   Accesso: SOLO NEGOZIO BOLOGNA")
    print()
    print("🌍 Manager di Area:")
    print("   Username: laura.ferrari")
    print("   Email: laura.ferrari@blowsquared.com")
    print("   Password: password123")
    print("   Accesso: NEGOZI AREA EMILIA-ROMAGNA")
    print("=" * 60)
    print(f"\n💡 Vai su: http://127.0.0.1:8000/dirigenti/login/ per testare l'accesso")
    
    # Verifica finale con stampa dettagliata
    print("\n🔍 VERIFICA FINALE:")
    dirigenti_creati = Dirigente.objects.all()
    for d in dirigenti_creati:
        print(f"✅ {d.nome} {d.cognome} ({d.get_livello_accesso_display()})")
        print(f"   - Username: {d.user.username}")
        print(f"   - Email: {d.user.email}")
        print(f"   - Negozio principale: {d.negozio_principale.nome}")
        print(f"   - Negozi gestiti: {d.numero_negozi_gestiti}")
        print(f"   - Può gestire dipendenti: {'Sì' if d.can_manage_dipendenti() else 'No'}")
        print(f"   - Può vedere finanze: {'Sì' if d.can_view_financials() else 'No'}")
        print()

if __name__ == "__main__":
    crea_dirigenti()
