"""
Test Runner e Configurazioni per BlowSquared
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def setup_test_environment():
    """Setup ambiente di test"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlowSquared.settings')
    django.setup()


def run_tests(test_labels=None, verbosity=1, interactive=True, failfast=False):
    """
    Esegue i test di BlowSquared
    
    Args:
        test_labels: Lista di test specifici da eseguire (es: ['tests.test_carrello'])
        verbosity: Livello di dettaglio output (0=minimal, 1=normal, 2=verbose)
        interactive: Se True, chiede conferma prima di distruggere il DB di test
        failfast: Se True, si ferma al primo errore
    """
    setup_test_environment()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(
        verbosity=verbosity,
        interactive=interactive,
        failfast=failfast
    )
    
    if test_labels is None:
        test_labels = ['tests']
    
    failures = test_runner.run_tests(test_labels)
    
    if failures:
        print(f"\n❌ {failures} test(s) fallito/i")
        return failures
    else:
        print(f"\n✅ Tutti i test sono passati!")
        return 0


def run_specific_tests():
    """Esegue categorie specifiche di test"""
    
    print("🧪 SUITE DI TEST BLOWSQUARED")
    print("=" * 50)
    
    test_suites = {
        '1': ('tests.test_carrello', 'Test Sistema Carrello'),
        '2': ('tests.test_negozio_cambio', 'Test Cambio Negozio'),
        '3': ('tests.test_security', 'Test Sicurezza e Permessi'),
        '4': ('tests', 'Tutti i Test'),
    }
    
    print("\nCategorie disponibili:")
    for key, (suite, description) in test_suites.items():
        print(f"  {key}. {description}")
    
    choice = input("\nScegli categoria (1-4): ").strip()
    
    if choice in test_suites:
        suite, description = test_suites[choice]
        print(f"\n🚀 Eseguendo: {description}")
        print("-" * 30)
        
        return run_tests([suite], verbosity=2, failfast=True)
    else:
        print("❌ Scelta non valida")
        return 1


if __name__ == '__main__':
    """
    Esempi di utilizzo:
    
    # Esegui tutti i test
    python manage.py test tests
    
    # Esegui solo test carrello
    python manage.py test tests.test_carrello
    
    # Esegui test con output verboso
    python manage.py test tests --verbosity=2
    
    # Fermati al primo errore
    python manage.py test tests --failfast
    """
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        exit_code = run_specific_tests()
        sys.exit(exit_code)
    else:
        print("💡 Per selezione interattiva: python tests/test_runner.py interactive")
        print("💡 Per test completi: python manage.py test tests")
        exit_code = run_tests()
        sys.exit(exit_code)
