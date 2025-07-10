"""
Script per creare dipendenti di test nel database.
Esegui con: python manage.py shell < dipendenti/crea_dipendenti.py
"""

import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlowSquared.settings')
django.setup()

from django.contrib.auth.models import User
from dipendenti.models import Dipendente
from negozi.models import Negozio

def crea_negozi_test():
    """Crea negozi di test se non esistono"""
    print("🔍 Controllo negozi esistenti...")
    negozi_esistenti = Negozio.objects.all()
    print(f"Negozi trovati: {[n.nome for n in negozi_esistenti]}")
    
    if not negozi_esistenti.exists():
        print("📍 Creazione negozi di test...")
        
        negozio1 = Negozio.objects.create(
            nome="BlowSquared Bologna Centro",
            indirizzo="Via Indipendenza 123",
            citta="Bologna",
            provincia="BO",
            cap="40121",
            telefono="051-1234567",
            email="bologna@blowsquared.com",
            servizio_consegna_domicilio=True,
            ritiro_click_collect=True,
            servizio_farmacia=False
        )
        
        negozio2 = Negozio.objects.create(
            nome="BlowSquared Modena Stazione",
            indirizzo="Corso Vittorio Emanuele 45",
            citta="Modena", 
            provincia="MO",
            cap="41121",
            telefono="059-9876543",
            email="modena@blowsquared.com",
            servizio_consegna_domicilio=True,
            ritiro_click_collect=True,
            servizio_farmacia=True
        )
        
        print(f"✅ Creati negozi: {negozio1.nome} e {negozio2.nome}")
        return negozio1, negozio2
    else:
        negozi_list = list(negozi_esistenti)
        print(f"📍 Usando negozi esistenti: {[n.nome for n in negozi_list]}")
        return negozi_list[0], negozi_list[-1] if len(negozi_list) > 1 else negozi_list[0]

def crea_dipendenti():
    print("🏪 === INIZIO CREAZIONE DIPENDENTI ===")
    
    # Crea o recupera negozi
    try:
        negozio1, negozio2 = crea_negozi_test()
        print(f"✅ Negozi pronti: {negozio1.nome} e {negozio2.nome}")
    except Exception as e:
        print(f"❌ ERRORE nella creazione negozi: {e}")
        return
    
    # Dipendente 1
    print("\n👤 Creazione Dipendente 1...")
    try:
        if User.objects.filter(username='mario.rossi').exists():
            print("🗑️ Rimuovo utente esistente: mario.rossi")
            User.objects.filter(username='mario.rossi').delete()
        
        user1 = User.objects.create_user(
            username='mario.rossi',
            email='mario.rossi@blowsquared.com',
            password='password123',
            first_name='Mario',
            last_name='Rossi'
        )
        print(f"✅ Utente creato: {user1.username}")
        
        dipendente1 = Dipendente.objects.create(
            user=user1,
            nome='Mario',
            cognome='Rossi',
            eta=32,
            telefono='051-1234567',
            indirizzo='Via Roma 123, Bologna',
            data_nascita=date(1991, 5, 15),
            negozio=negozio1
        )
        print(f"✅ Dipendente creato: {dipendente1.nome} {dipendente1.cognome} - {dipendente1.negozio.nome}")
        
    except Exception as e:
        print(f"❌ ERRORE creazione dipendente 1: {e}")
        import traceback
        traceback.print_exc()
    
    # Dipendente 2
    print("\n👤 Creazione Dipendente 2...")
    try:
        if User.objects.filter(username='laura.bianchi').exists():
            print("🗑️ Rimuovo utente esistente: laura.bianchi")
            User.objects.filter(username='laura.bianchi').delete()
        
        user2 = User.objects.create_user(
            username='laura.bianchi',
            email='laura.bianchi@blowsquared.com', 
            password='password123',
            first_name='Laura',
            last_name='Bianchi'
        )
        print(f"✅ Utente creato: {user2.username}")
        
        dipendente2 = Dipendente.objects.create(
            user=user2,
            nome='Laura',
            cognome='Bianchi',
            eta=28,
            telefono='059-9876543',
            indirizzo='Corso Vittorio Emanuele 45, Modena',
            data_nascita=date(1995, 11, 22),
            negozio=negozio2
        )
        print(f"✅ Dipendente creato: {dipendente2.nome} {dipendente2.cognome} - {dipendente2.negozio.nome}")
        
    except Exception as e:
        print(f"❌ ERRORE creazione dipendente 2: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 === CREAZIONE COMPLETATA ===")
    print("\n📋 CREDENZIALI PER IL TEST:")
    print("=" * 50)
    print("🏪 Dipendente 1:")
    print("   Username: mario.rossi")
    print("   Password: password123")
    print()
    print("🏪 Dipendente 2:")
    print("   Username: laura.bianchi")  
    print("   Password: password123")
    print("=" * 50)
    print(f"\n💡 Vai su: http://127.0.0.1:8000/dipendenti/login/ per testare l'accesso")
    
    # Verifica finale
    print("\n🔍 VERIFICA FINALE:")
    dipendenti_creati = Dipendente.objects.all()
    for d in dipendenti_creati:
        print(f"✅ {d.nome} {d.cognome} - {d.negozio.nome}")

if __name__ == "__main__":
    crea_dipendenti()
