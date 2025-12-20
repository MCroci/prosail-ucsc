"""
Script di test per verificare che tutte le dipendenze siano installate
"""
import sys

def test_imports():
    """Test che tutte le dipendenze siano installate"""
    modules = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'plotly': 'Plotly',
        'scipy': 'SciPy',
        'prosail': 'PROSAIL'
    }
    
    failed = []
    print("🔍 Verifica dipendenze...\n")
    
    for module, name in modules.items():
        try:
            __import__(module)
            print(f"✅ {name:15} - OK")
        except ImportError as e:
            print(f"❌ {name:15} - NON TROVATO")
            print(f"   Errore: {str(e)[:50]}")
            failed.append(module)
    
    print("\n" + "="*50)
    
    if failed:
        print(f"\n⚠️  Moduli mancanti: {', '.join(failed)}")
        print("\n📦 Soluzione:")
        if 'prosail' in failed:
            print("   1. Installa prosail:")
            print("      conda install -c jgomezdans prosail")
            print("      oppure")
            print("      pip install prosail")
        print("   2. Installa altre dipendenze:")
        print("      pip install -r requirements.txt")
        sys.exit(1)
    else:
        print("\n✅ Tutte le dipendenze sono installate correttamente!")
        print("\n🚀 Puoi avviare l'app con:")
        print("   streamlit run app.py")
        return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n" + "="*50)
        print("✅ Pronto per il deploy!")
        print("📖 Leggi DEPLOY.md per le istruzioni")

