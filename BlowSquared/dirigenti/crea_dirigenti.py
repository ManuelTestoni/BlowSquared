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
        # Seleziona il primo negozio disponibile come negozio principale
        negozio_principale = negozi.first()
        
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
        print(f"✅ Utente creato: {user1.username}")
        print(f"   - Email: {user1.email}")
        print(f"   - Password hash: {user1.password[:30]}...")
        
        # Verifica password
        if user1.check_password('password123'):
            print("✅ Password verificata correttamente")
        else:
            print("❌ Errore nella verifica password")
        
        # Crea dirigente (senza i parametri errati)
        dirigente1 = Dirigente.objects.create(
            user=user1,
            nome='Alessandro',
            cognome='Verdi',
            eta=45,
            telefono='051-7654321',
            indirizzo='Via Roma 456, Bologna',
            data_nascita=date(1978, 3, 15),
            livello_accesso='direttore_generale',
            negozio_principale=negozio_principale,
            data_assunzione=date(2010, 1, 15),
            stipendio_base=75000.00,
            note_direzione='Direttore Generale con piena autonomia decisionale.'
        )
        print(f"✅ Dirigente creato: {dirigente1.nome_completo}")
        print(f"   - Livello: {dirigente1.get_livello_accesso_display()}")
        print(f"   - Negozio: {dirigente1.negozio_principale.nome}")
        
        # Il direttore generale ha accesso a tutti i negozi
        dirigente1.negozi_supervisionati.set(negozi.all())
        print(f"   - Negozi supervisionati: {dirigente1.negozi_supervisionati.count()}")
        
    except Exception as e:
        print(f"❌ ERRORE creazione direttore generale: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test immediato di autenticazione
    print(f"\n🧪 TEST AUTENTICAZIONE IMMEDIATO:")
    from django.contrib.auth import authenticate
    
    test_user = authenticate(username='alessandro.verdi', password='password123')
    if test_user:
        print(f"✅ Autenticazione riuscita per: {test_user.username}")
        if hasattr(test_user, 'dirigente'):
            print(f"✅ Profilo dirigente trovato: {test_user.dirigente.nome_completo}")
        else:
            print(f"❌ Profilo dirigente NON trovato")
    else:
        print(f"❌ Autenticazione fallita")
    
    # Dirigente 2 - Vice Direttore
    print("\n👔 Creazione Vice Direttore...")
    try:
        if User.objects.filter(username='marco.rossi').exists():
            print("🗑️ Rimuovo utente esistente: marco.rossi")
            User.objects.filter(username='marco.rossi').delete()
        
        user2 = User.objects.create_user(
            username='marco.rossi',
            email='marco.rossi@blowsquared.com',
            password='password123',
            first_name='Marco',
            last_name='Rossi'
        )
        print(f"✅ Utente creato: {user2.username}")
        
        dirigente2 = Dirigente.objects.create(
            user=user2,
            nome='Marco',
            cognome='Rossi',
            eta=38,
            telefono='051-8765432',
            indirizzo='Via Indipendenza 123, Bologna',
            data_nascita=date(1985, 7, 22),
            livello_accesso='vice_direttore',
            negozio_principale=negozio_principale,
            data_assunzione=date(2015, 3, 1),
            stipendio_base=55000.00,
            note_direzione='Vice Direttore con responsabilità operative.'
        )
        print(f"✅ Dirigente creato: {dirigente2.nome_completo}")
        
        # Il vice direttore ha accesso a tutti i negozi
        dirigente2.negozi_supervisionati.set(negozi.all())
        print(f"   - Negozi supervisionati: {dirigente2.negozi_supervisionati.count()}")
        
    except Exception as e:
        print(f"❌ ERRORE creazione vice direttore: {e}")
    
    # Dirigente 3 - Manager di Area (se ci sono più negozi)
    if negozi.count() > 1:
        print("\n👔 Creazione Manager di Area...")
        try:
            if User.objects.filter(username='giulia.bianchi').exists():
                print("🗑️ Rimuovo utente esistente: giulia.bianchi")
                User.objects.filter(username='giulia.bianchi').delete()
            
            user3 = User.objects.create_user(
                username='giulia.bianchi',
                email='giulia.bianchi@blowsquared.com',
                password='password123',
                first_name='Giulia',
                last_name='Bianchi'
            )
            print(f"✅ Utente creato: {user3.username}")
            
            # Usa il secondo negozio come principale
            secondo_negozio = negozi.all()[1]
            
            dirigente3 = Dirigente.objects.create(
                user=user3,
                nome='Giulia',
                cognome='Bianchi',
                eta=35,
                telefono='059-1234567',
                indirizzo='Via Emilia 89, Modena',
                data_nascita=date(1988, 11, 8),
                livello_accesso='manager_area',
                negozio_principale=secondo_negozio,
                data_assunzione=date(2018, 6, 15),
                stipendio_base=42000.00,
                note_direzione='Manager di Area responsabile per la zona Nord.'
            )
            print(f"✅ Dirigente creato: {dirigente3.nome_completo}")
            
            # Il manager di area supervisiona alcuni negozi
            dirigente3.negozi_supervisionati.add(secondo_negozio)
            if negozi.count() > 2:
                dirigente3.negozi_supervisionati.add(negozi.all()[2])
            print(f"   - Negozi supervisionati: {dirigente3.negozi_supervisionati.count()}")
            
        except Exception as e:
            print(f"❌ ERRORE creazione manager di area: {e}")
    
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
    print("   Username: marco.rossi")
    print("   Email: marco.rossi@blowsquared.com")
    print("   Password: password123")
    print("   Accesso: TUTTI I NEGOZI")
    if negozi.count() > 1:
        print()
        print("🏢 Manager di Area:")
        print("   Username: giulia.bianchi")
        print("   Email: giulia.bianchi@blowsquared.com")
        print("   Password: password123")
        print("   Accesso: NEGOZI ASSEGNATI")
    print("=" * 60)
    print(f"\n💡 Vai su: http://127.0.0.1:8000/dirigenti/login/")
    
    # Verifica finale dettagliata
    print("\n🔍 VERIFICA FINALE DETTAGLIATA:")
    dirigenti_creati = Dirigente.objects.all()
    print(f"Dirigenti totali nel database: {dirigenti_creati.count()}")
    
    for d in dirigenti_creati:
        print(f"✅ {d.nome_completo}")
        print(f"   - Username: {d.user.username}")
        print(f"   - Email: {d.user.email}")
        print(f"   - User ID: {d.user.id}")
        print(f"   - Dirigente ID: {d.id}")
        print(f"   - Is Active: {d.user.is_active}")
        print(f"   - Password Set: {'Sì' if d.user.password else 'No'}")
        print()

if __name__ == "__main__":
    crea_dirigenti()

# Esegui automaticamente
crea_dirigenti()
