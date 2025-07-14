# 🧪 **SUITE DI TEST BLOWSQUARED**

Documentazione completa per i test automatizzati di BlowSquared.

## 📋 **PANORAMICA**

La suite di test è organizzata in moduli specifici per testare tutte le funzionalità critiche dell'applicazione:

- **test_base.py**: Configurazione base e utilities comuni
- **test_carrello.py**: Test completi del sistema carrello
- **test_negozio_cambio.py**: Test della logica di cambio negozio
- **test_security.py**: Test sicurezza e permessi utenti
- **test_performance.py**: Test di performance e stress test

## 🚀 **ESECUZIONE RAPIDA**

### Tutti i test
```bash
python manage.py test tests
```

### Test specifici
```bash
# Solo test carrello
python manage.py test tests.test_carrello

# Solo test cambio negozio
python manage.py test tests.test_negozio_cambio

# Solo test sicurezza
python manage.py test tests.test_security
```

### Modalità interattiva
```bash
python tests/test_runner.py interactive
```

## 📊 **OPZIONI AVANZATE**

### Output verboso
```bash
python manage.py test tests --verbosity=2
```

### Ferma al primo errore
```bash
python manage.py test tests --failfast
```

### Mantieni database di test
```bash
python manage.py test tests --keepdb
```

### Test paralleli
```bash
python manage.py test tests --parallel
```

## 🎯 **TEST COVERAGE**

### Funzionalità Testate

#### **Sistema Carrello**
- ✅ Creazione e gestione carrello
- ✅ Aggiunta/rimozione prodotti
- ✅ Calcolo subtotali e quantità
- ✅ Svuotamento carrello
- ✅ Validazione disponibilità prodotti
- ✅ Permessi e accessi

#### **Cambio Negozio**
- ✅ Cambio senza carrello
- ✅ Cambio con carrello vuoto
- ✅ Conferma svuotamento carrello
- ✅ Rifiuto cambio negozio
- ✅ Stessa selezione negozio

#### **Sicurezza e Permessi**
- ✅ Accesso utenti normali
- ✅ Restrizioni dipendenti/dirigenti
- ✅ Controllo autenticazione
- ✅ Validazione associazioni negozio

#### **Performance**
- ✅ Operazioni multiple carrello
- ✅ Calcoli con molti elementi
- ✅ Stress test concorrenza
- ✅ Gestione memoria

## 🔧 **SETUP TEST ENVIRONMENT**

### Database di Test
Django crea automaticamente un database di test isolato. Configurazione in `settings.py`:

```python
# Test database (creato automaticamente)
DATABASES['default']['TEST'] = {
    'NAME': 'test_blowsquared',
}
```

### Dati di Test
Ogni test class eredita da `BaseTestCase` che setup:
- Utenti (normale, dipendente, dirigente)
- Negozi (2 supermercati)
- Prodotti e categorie
- Associazioni e permessi

## 📈 **METRICHE E REPORTING**

### Coverage Report
```bash
# Installa coverage
pip install coverage

# Esegui test con coverage
coverage run --source='.' manage.py test tests
coverage report
coverage html  # Genera report HTML
```

### Performance Benchmarks
I test di performance validano:
- Aggiunta multipla carrello: < 5 secondi
- Calcolo subtotale: < 1 secondo  
- Svuotamento carrello grande: < 2 secondi

## 🛠️ **PERSONALIZZAZIONE**

### Aggiungere Nuovi Test

1. **Crea nuovo modulo test**:
```python
# tests/test_nuovo_modulo.py
from tests.test_base import BaseTestCase

class NuovoModuloTest(BaseTestCase):
    def test_nuova_funzionalita(self):
        # Il tuo test qui
        pass
```

2. **Aggiungi al test runner**:
```python
# tests/test_runner.py
test_suites = {
    # ...esistenti...
    '5': ('tests.test_nuovo_modulo', 'Test Nuovo Modulo'),
}
```

### Configurazione CI/CD
```yaml
# .github/workflows/tests.yml
name: Django Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python manage.py test tests --verbosity=2
```

## 🚨 **TROUBLESHOOTING**

### Errori Comuni

#### **Database locked**
```bash
# Rimuovi database di test esistente
rm db.sqlite3
python manage.py test tests
```

#### **Import errors**
```bash
# Verifica PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python manage.py test tests
```

#### **Permission denied**
```bash
# Controlla permessi file
chmod +x tests/test_runner.py
```

### Debug Test
```python
# Aggiungi debug output
import logging
logging.basicConfig(level=logging.DEBUG)

# Nel test
def test_debug_example(self):
    print(f"Debug: {self.utente_normale.username}")
    self.assertTrue(True)
```

## 📚 **BEST PRACTICES**

### Naming Convention
- Test classes: `NomeModuloTest`
- Test methods: `test_comportamento_specifico`
- Setup data: nomi descrittivi (`utente_normale`, `negozio1`)

### Test Isolation
- Ogni test è indipendente
- Database ripulito tra test
- Setup/teardown automatici

### Assertions Utili
```python
# Django specific
self.assertContains(response, 'testo')
self.assertRedirects(response, url)
self.assertTemplateUsed(response, 'template.html')

# Custom business logic
self.assertEqual(carrello.numero_articoli, 5)
self.assertTrue(user.is_authenticated)
self.assertIn('success', response.json())
```

## 💡 **PROSSIMI SVILUPPI**

### Test Mancanti
- [ ] Test integrazione pagamenti
- [ ] Test notifiche email
- [ ] Test backup/restore
- [ ] Test API REST (se implementata)

### Miglioramenti
- [ ] Mock servizi esterni
- [ ] Test frontend JavaScript
- [ ] Load testing con Locust
- [ ] Security testing

---

**🎯 Obiettivo**: Mantenere coverage > 80% e tutti i test verdi! 
**📞 Support**: Per domande sui test, consulta questo README o i commenti nel codice.
