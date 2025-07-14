# 🛒 BlowSquared - Web App Supermercato

## 📋 Panoramica

BlowSquared è una web app Django completa per la gestione di una catena di supermercati, con funzionalità distinte per 4 tipi di utenti. L'applicazione gestisce tutto, dalla ricerca prodotti alle analisi statistiche di vendita.

## 👥 Classi di Utenti e Funzionalità

### 🔓 **Utente Anonimo**
*Accesso libero senza registrazione*

**✅ Ricerca Prodotti**
- Sistema di ricerca avanzato con filtri per categoria, prezzo, marca
- Visualizzazione prodotti con foto, descrizione, prezzi e sconti
- Ordinamento per nome, prezzo, categoria
- Ricerca in tempo reale con AJAX

**✅ Visualizzazione Volantino**
- Volantino interattivo sfogliabile con viewer dedicato
- Navigazione touch-friendly per mobile
- Visualizzazione offerte e promozioni

**✅ Navigazione Supermercati per Zona**
- Ricerca negozi per posizione geografica
- Visualizzazione dettagliata: orari, servizi, contatti
- Info complete: superficie, parcheggi, casse disponibili
- Filtri per città e provincia

**✅ Informazioni Dettagliate Supermercati**
- Orari di apertura completi
- Servizi disponibili (farmacia, panetteria, macelleria, pescheria)
- Caratteristiche strutturali (superficie, posti auto)
- Contatti e posizione

---

### 🔐 **Utente Registrato**
*Tutte le funzionalità dell'anonimo +*

**✅ Gestione Carrello**
- Aggiunta prodotti al carrello con quantità personalizzate
- Calcolo automatico subtotali e totali
- Gestione stock e disponibilità per negozio
- Svuotamento automatico carrello al cambio negozio

**✅ Liste della Spesa Ricorrenti**
- Creazione liste personalizzate con ricerca prodotti
- Gestione quantità e note per ogni elemento
- Aggiunta rapida liste complete al carrello
- Visualizzazione storico liste create

**✅ Cronologia Ordini**
- Storico completo degli ordini effettuati
- Dettagli ordine con prodotti, quantità, prezzi
- Stato ordine e tracking

**✅ Forum Community**
- **Discussioni collettive**: Chat in tempo reale tra utenti
- **Condivisione ricette**: Ricette con ingredienti collegati ai prodotti
- **Recensioni negozi**: Valutazioni con stelle e commenti
- **Sistema WebSocket**: Messaggi in tempo reale

---

### 👨‍💼 **Dipendente**
*Gestione catalogo prodotti del proprio negozio*

**✅ Caricamento Nuovi Prodotti**
- Form completo per aggiunta prodotti (nome, descrizione, foto, prezzo)
- Associazione automatica al negozio del dipendente
- Gestione categorie, marche, codici a barre
- Upload immagini prodotti

**✅ Aggiornamento Disponibilità**
- Dashboard con visualizzazione stock corrente
- Aggiornamento quantità: aumento, diminuzione, impostazione diretta
- Filtri per categoria e disponibilità prodotti
- Ricerca rapida prodotti nel negozio

**✅ Gestione Inventario**
- Visualizzazione prodotti con stock basso
- Indicatori visivi per disponibilità
- Gestione prodotti esauriti

---

### 👔 **Direttore/Dirigente**
*Analisi e gestione strategica del negozio*

**✅ Analisi Statistiche Vendite**
- **Dashboard Analytics**: Grafici interattivi delle vendite
- **Trend temporali**: Visualizzazione fatturato per periodi (7/30 giorni)
- **Metriche KPI**: Fatturato mensile, ordini, prodotti attivi
- **Prodotti top**: Classifica prodotti più venduti

**✅ Gestione Negozio**
- Panoramica completa del negozio gestito
- Analisi performance vs periodo precedente

**✅ Reporting Avanzato**
- Grafici Chart.js per visualizzazione dati
- Confronti temporali e trend analysis

---

## 🛠️ Implementazione Tecnica

### **Backend (Django)**
- **Models**: Struttura dati completa per utenti, prodotti, negozi, ordini
- **Views**: Logica di business per tutte le funzionalità
- **Authentication**: Sistema di permessi per tipologie utenti
- **API**: Endpoint REST per funzionalità AJAX

### **Frontend**
- **JavaScript**: Interazioni dinamiche e ricerche in tempo reale
- **CSS**: Design responsive e moderno
- **AJAX**: Aggiornamenti senza reload pagina
- **Chart.js**: Grafici per analytics direttore

### **Database**
- **SQLite**: Database relazionale con foreign keys
- **Migrations**: Gestione schema database
- **Relations**: Modelli collegati per integrità dati

### **Features Avanzate**
- **WebSocket**: Chat forum in tempo reale
- **File Upload**: Gestione immagini prodotti
- **Geolocalizzazione**: Ricerca negozi per zona
- **Responsive Design**: Ottimizzato per tutti i device

---

## 🎯 Funzionalità Distintive

1. **Sistema Multiutente**: 4 tipologie utenti con permessi specifici
2. **Gestione Negozi**: Prodotti specifici per negozio + prodotti comuni
3. **Carrello Intelligente**: Svuotamento automatico al cambio negozio
4. **Forum Interattivo**: Community con ricette e recensioni
5. **Analytics Avanzate**: Dashboard dirigenti con grafici dinamici
6. **Ricerca Avanzata**: Filtri multipli e ricerca real-time 

---

## 📊 Stato Implementazione

| Funzionalità | Anonimo | Registrato | Dipendente | Dirigente | Status |
|-------------|---------|------------|------------|-----------|--------|
| Ricerca Prodotti | ✅ | ✅ | ❌ | ❌ | **Completa** |
| Volantino | ✅ | ✅ | ❌ | ❌ | **Completa** |
| Info Negozi | ✅ | ✅ | ❌ | ❌ | **Completa** |
| Carrello | ❌ | ✅ | ❌ | ❌ | **Completa** |
| Liste Spesa | ❌ | ✅ | ❌ | ❌ | **Completa** |
| Cronologia | ❌ | ✅ | ❌ | ❌ | **Completa** |
| Forum | ❌ | ✅ | ❌ | ❌ | **Completa** |
| Gestione Prodotti | ❌ | ❌ | ✅ | ❌ | **Completa** |
| Aggiorna Stock | ❌ | ❌ | ✅ | ❌ | **Completa** |
| Analytics | ❌ | ❌ | ❌ | ✅ | **Completa** |

## 🚀 Risultato

**Tutte le funzionalità prestabilite sono state implementate con successo**. La web app BlowSquared è completa e funzionante, con un sistema robusto che gestisce tutti i casi d'uso previsti per ciascuna tipologia di utente.

---

## 🗂️ Struttura del Progetto

```
BlowSquared/
├── manage.py
├── requirements.txt
├── static/          # CSS, JS, immagini
├── media/           # Upload immagini prodotti
├── templates/       # Template base
└── BlowSquared/     # App principale
    ├── settings.py
    ├── urls.py
    ├── utenti/      # Gestione utenti e profili
    ├── negozi/      # Gestione punti vendita
    ├── prodotti/    # Catalogo prodotti
    ├── carrello/    # Sistema carrello e ordini
    ├── dipendenti/  # Dashboard dipendenti
    ├── dirigenti/   # Analytics dirigenti
    ├── forum/       # Community e forum
    ├── volantino/   # Volantino interattivo
    └── tests/       # Suite di test completa
```

## 📚 Come Iniziare

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Accesso Admin**
   ```bash
   python manage.py createsuperuser
   ```

3. **Test Suite**
   ```bash
   python manage.py test tests
   ```
