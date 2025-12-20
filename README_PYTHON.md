# PROSAIL Model - Python Version

Versione Python dell'applicazione PROSAIL per il telerilevamento in agricoltura di precisione.

## 🚀 Installazione

### Prerequisiti

1. **Python 3.8+** installato
2. **Libreria Python `prosail`** installata

### Passaggi di installazione

1. **Clona o scarica questo repository**

2. **Crea un ambiente virtuale Python** (consigliato):
   ```bash
   python -m venv venv
   
   # Su Windows
   venv\Scripts\activate
   
   # Su macOS/Linux
   source venv/bin/activate
   ```

3. **Installa la libreria `prosail`**:
   
   Opzione A - Usando conda (consigliato):
   ```bash
   conda install -c jgomezdans prosail
   ```
   
   Opzione B - Usando pip (potrebbe richiedere compilazione):
   ```bash
   pip install prosail
   ```
   
   Per maggiori informazioni: https://github.com/jgomezdans/prosail

4. **Installa le altre dipendenze Python**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurazione Windows** (se necessario):
   
   Se `rpy2` non trova R automaticamente, imposta la variabile d'ambiente `R_HOME`:
   ```bash
   # Trova il percorso di installazione di R (es. C:\Program Files\R\R-4.3.1)
   setx R_HOME "C:\Program Files\R\R-4.3.1"
   ```

## 🏃 Esecuzione e Test Locale

### Test rapido delle dipendenze

Prima di avviare l'app, verifica che tutto sia installato:

```bash
python test_app.py
```

Questo script controlla che tutte le librerie necessarie siano presenti.

### Avvia l'applicazione

```bash
streamlit run app.py
```

L'app si aprirà automaticamente nel browser all'indirizzo `http://localhost:8501`

### 📖 Guida completa al test

Per una guida dettagliata su come testare l'app localmente, consulta **[TEST_LOCAL.md](TEST_LOCAL.md)**

## 📦 Deploy Online

Per istruzioni dettagliate su come pubblicare l'app online, consulta il file **[DEPLOY.md](DEPLOY.md)**

### Opzioni principali:

1. **🌟 Streamlit Cloud** (CONSIGLIATO):
   - Gratuito e semplice
   - Deploy automatico da GitHub
   - Vai su: https://share.streamlit.io/
   - Connetti il repository e deploya

2. **Render**:
   - Alternativa gratuita
   - Supporta applicazioni Python
   - File `render.yaml` incluso

3. **Heroku**:
   - File `Procfile` incluso
   - Richiede Heroku CLI

4. **Docker**:
   - Per deploy avanzati
   - Funziona su AWS, Google Cloud, Azure, etc.

⚠️ **Nota importante:** La libreria `prosail` potrebbe richiedere compilazione C/C++. Se il deploy fallisce, considera di usare un ambiente con conda o Docker.

## 🛠️ Sviluppo

### Struttura file:
- `app.py` - Applicazione Streamlit principale
- `sensor_bands.py` - Definizioni delle bande dei sensori satellitari
- `requirements.txt` - Dipendenze Python
- `POSITIVE_CRAST.Rmd` - Versione originale R/Flexdashboard

### Modifiche apportate rispetto alla versione R:
- ✅ Framework: Shiny/Flexdashboard → Streamlit
- ✅ Plotting: ggplot2/plotly → plotly puro
- ✅ Data manipulation: base R → pandas/numpy
- ✅ Reactive: Shiny reactive → Streamlit re-run + caching
- ✅ PROSAIL: Usa libreria Python nativa `prosail` (no R necessario!)

## 📝 Note tecniche

- L'app usa `@st.cache_data` per cacheare i calcoli costosi di PROSAIL
- I parametri sono gestiti come range (min, max) come nella versione originale
- La visualizzazione usa Plotly per mantenere l'interattività
- Il resampling spettrale per i sensori satellitari è implementato usando funzioni Gaussiane
- La libreria `prosail` è completamente Python e non richiede R

## 🤝 Contributi

Creato da: UCSC Field Crops Group - Remote sensing team

**Michele Croci**, **Giorgio Impollonia** e **Stefano Amaducci**

