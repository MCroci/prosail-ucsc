# 🧪 Test Locale dell'App PROSAIL

Questa guida ti aiuta a testare l'applicazione localmente prima di deployarla online.

## ✅ Prerequisiti

1. **Python 3.8+** installato
   ```bash
   python --version
   # Dovrebbe mostrare Python 3.8 o superiore
   ```

2. **Git** (opzionale, per clonare il repository)

## 📦 Installazione

### Passo 1: Clona/Naviga nella directory del progetto

Se hai già il codice:
```bash
cd prosail-ucsc
```

Se devi clonarlo:
```bash
git clone https://github.com/tuo-username/prosail-ucsc.git
cd prosail-ucsc
```

### Passo 2: Crea un ambiente virtuale (Consigliato)

**Su Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Su macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Dopo l'attivazione, dovresti vedere `(venv)` all'inizio della riga di comando.

### Passo 3: Installa le dipendenze

#### Opzione A: Usando pip (più semplice)

```bash
pip install -r requirements.txt
```

⚠️ **Nota importante:** La libreria `prosail` potrebbe richiedere compilazione C/C++.

#### Opzione B: Usando conda (consigliato per prosail)

Se hai Anaconda/Miniconda installato:

```bash
# Crea un ambiente conda
conda create -n prosail-app python=3.9
conda activate prosail-app

# Installa prosail da conda-forge
conda install -c jgomezdans prosail

# Installa le altre dipendenze
pip install -r requirements.txt
```

### Passo 4: Verifica l'installazione

Verifica che tutte le librerie siano installate:

```bash
python -c "import streamlit; print('Streamlit OK')"
python -c "import pandas; print('Pandas OK')"
python -c "import numpy; print('NumPy OK')"
python -c "import plotly; print('Plotly OK')"
python -c "import scipy; print('SciPy OK')"
python -c "import prosail; print('PROSAIL OK')"
```

Se tutti i comandi mostrano "OK", sei pronto!

## 🚀 Esecuzione dell'App

### Avvia l'applicazione

```bash
streamlit run app.py
```

Dovresti vedere un output simile a:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Apri nel browser

L'app si aprirà automaticamente nel browser, oppure vai manualmente a:
```
http://localhost:8501
```

## ✅ Checklist di Test

Controlla che tutto funzioni:

### 1. ✅ L'app si avvia senza errori
- [ ] Nessun errore nella console
- [ ] La pagina si carica nel browser

### 2. ✅ Interfaccia utente
- [ ] Vedo i slider nella sidebar
- [ ] Vedo i menu a tendina (sensore, VI)
- [ ] Il layout è corretto

### 3. ✅ Calcoli PROSPECT
- [ ] Cambio i parametri fogliari (N, Cm, Cw, Cab)
- [ ] Il grafico "Leaf Reflectance - PROSPECT" si aggiorna
- [ ] Vedo una curva di riflettanza verde

### 4. ✅ Calcoli PROSAIL
- [ ] Cambio i parametri della canopy (LAI, ALA)
- [ ] Il grafico "Canopy Reflectance - SAIL" si aggiorna
- [ ] Vedo la curva rossa e i punti verdi (bande sensore)

### 5. ✅ Sensori satellitari
- [ ] Cambio il sensore (Sentinel2a, Landsat8, etc.)
- [ ] I punti sul grafico cambiano posizione
- [ ] Il numero di punti corrisponde alle bande del sensore

### 6. ✅ Indici di vegetazione
- [ ] Cambio l'indice (NDVI, NDRE, GNDVI)
- [ ] I grafici LAI e Chlorophyll si aggiornano
- [ ] Vedo una relazione tra VI e LAI/Cab

### 7. ✅ Performance
- [ ] I calcoli non sono troppo lenti (< 10 secondi)
- [ ] L'app risponde ai cambiamenti dei parametri
- [ ] Non ci sono errori quando cambio rapidamente i parametri

## 🐛 Risoluzione Problemi Comuni

### Problema: "ModuleNotFoundError: No module named 'prosail'"

**Soluzione:**
```bash
# Prova con conda (consigliato)
conda install -c jgomezdans prosail

# Oppure con pip (potrebbe richiedere compilazione)
pip install prosail
```

### Problema: "ModuleNotFoundError: No module named 'streamlit'"

**Soluzione:**
```bash
pip install -r requirements.txt
```

### Problema: Errore durante la compilazione di prosail

**Soluzione:**
- Usa conda invece di pip
- Installa gcc/g++ (su Linux/Mac)
- Su Windows, considera di usare WSL o conda

### Problema: L'app è troppo lenta

**Possibili cause:**
- I range dei parametri sono troppo ampi (troppi calcoli)
- La cache non funziona correttamente
- Hardware limitato

**Soluzione:**
- Riduci i range dei parametri di default in `app.py`
- Verifica che `@st.cache_data` sia presente sulle funzioni

### Problema: I grafici non si aggiornano

**Soluzione:**
- Ricarica la pagina (F5)
- Controlla la console per errori JavaScript
- Verifica che plotly sia installato: `pip install plotly`

## 📊 Test Automatico (Opzionale)

Puoi creare uno script di test semplice:

```python
# test_app.py
import sys

def test_imports():
    """Test che tutte le dipendenze siano installate"""
    modules = ['streamlit', 'pandas', 'numpy', 'plotly', 'scipy', 'prosail']
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - NON TROVATO")
            failed.append(module)
    
    if failed:
        print(f"\n⚠️ Moduli mancanti: {', '.join(failed)}")
        print("Installa con: pip install -r requirements.txt")
        sys.exit(1)
    else:
        print("\n✅ Tutti i moduli sono installati correttamente!")

if __name__ == "__main__":
    test_imports()
```

Esegui con:
```bash
python test_app.py
```

## 🎯 Quando l'app funziona localmente

Se tutti i test passano, sei pronto per:

1. ✅ Commit del codice su GitHub
2. ✅ Deploy su Streamlit Cloud (vedi DEPLOY.md)
3. ✅ Condividere l'URL con altri utenti

## 📝 Note Finali

- **Performance:** I calcoli PROSAIL possono essere lenti con molti parametri. Questo è normale.
- **Browser:** L'app funziona meglio su Chrome, Firefox, o Edge moderni
- **Cache:** Streamlit usa cache per velocizzare i calcoli. Se cambi il codice, ricarica la pagina.

