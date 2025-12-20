# 🚀 Guida al Deploy Online - PROSAIL App

Questa guida spiega come pubblicare l'applicazione PROSAIL online.

## ❌ Vercel - NON Compatibile

**⚠️ IMPORTANTE:** Vercel **NON è compatibile** con applicazioni Streamlit perché:

- ❌ Vercel è per applicazioni **serverless** (Next.js, API routes, siti statici)
- ❌ Streamlit richiede un **server Python continuo** sempre in esecuzione
- ❌ Le funzioni serverless di Vercel terminano dopo ogni richiesta
- ❌ Streamlit mantiene stato tra le richieste (non serverless)

**Soluzione:** Usa invece **Streamlit Cloud**, **Render**, o **Heroku** (vedi opzioni sotto).

---

## 📋 Opzioni di Deploy (COMPATIBILI)

> **Nota:** Se stai cercando Vercel, leggi [VERCEL_ALTERNATIVES.md](VERCEL_ALTERNATIVES.md) per capire perché non è compatibile e quali sono le alternative migliori.

### 1. 🌟 Streamlit Cloud (CONSIGLIATO - Gratuito e Semplice)

**Streamlit Cloud** è la soluzione più semplice per applicazioni Streamlit.

#### Prerequisiti:
- Account GitHub
- Repository GitHub con il codice

#### Passaggi:

1. **Assicurati che il codice sia su GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Vai su Streamlit Cloud:**
   - Visita: https://share.streamlit.io/
   - Oppure: https://streamlit.io/cloud

3. **Accedi con GitHub:**
   - Clicca "Sign in with GitHub"
   - Autorizza Streamlit Cloud

4. **Deploy l'app:**
   - Clicca "New app"
   - Seleziona il repository: `prosail-ucsc`
   - Seleziona il branch: `main` (o `master`)
   - **Main file path:** `app.py`
   - Clicca "Deploy"

5. **Nota importante per prosail:**
   
   ⚠️ La libreria `prosail` potrebbe non essere disponibile direttamente su PyPI standard.
   
   Se il deploy fallisce per prosail, hai due opzioni:
   
   **Opzione A:** Usa conda-forge (se supportato)
   
   **Opzione B:** Crea un file `.streamlit/config.toml` con:
   ```toml
   [server]
   headless = true
   ```
   
   E aggiorna `requirements.txt` per includere un fallback o installazione alternativa.

#### Vantaggi:
- ✅ Gratuito
- ✅ Deploy automatico ad ogni push
- ✅ URL pubblico (es: `https://your-app.streamlit.app`)
- ✅ Facile da usare

---

### 2. 🐳 Render (Alternativa Gratuita)

Render offre hosting gratuito per applicazioni Python.

#### Passaggi:

1. **Crea un file `render.yaml` nella root:**
   ```yaml
   services:
     - type: web
       name: prosail-app
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
       envVars:
         - key: PYTHON_VERSION
           value: 3.9.0
   ```

2. **Vai su Render:**
   - Visita: https://render.com
   - Accedi con GitHub
   - Connetti il repository
   - Seleziona "New Web Service"
   - Render dovrebbe rilevare automaticamente il file `render.yaml`

#### Vantaggi:
- ✅ Gratuito (con limitazioni)
- ✅ Supporta Python e dipendenze scientifiche
- ✅ Deploy automatico

---

### 3. 🚀 Heroku (Richiede Setup)

Heroku supporta applicazioni Python con buildpack personalizzati.

#### Passaggi:

1. **Crea un file `Procfile` nella root:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Crea un file `setup.sh` (se prosail richiede build):**
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   " > ~/.streamlit/config.toml
   ```

3. **Installa Heroku CLI:**
   - Scarica da: https://devcenter.heroku.com/articles/heroku-cli

4. **Deploy:**
   ```bash
   heroku login
   heroku create prosail-app
   git push heroku main
   ```

⚠️ **Nota:** prosail potrebbe richiedere buildpack personalizzati se ha dipendenze C/C++.

---

### 4. 🐋 Docker + Cloud Provider

Per massimo controllo, puoi usare Docker.

#### Crea un `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if prosail needs them
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Poi puoi deployare su:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**

---

### 5. 🖥️ VPS (Virtual Private Server)

Se hai un VPS (es: DigitalOcean, Linode, AWS EC2):

```bash
# Sul server
git clone https://github.com/tuo-username/prosail-ucsc.git
cd prosail-ucsc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Installa prosail (potrebbe richiedere conda o build)
conda install -c jgomezdans prosail
# oppure
pip install prosail

# Esegui con screen/tmux o systemd
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Usa nginx come reverse proxy per HTTPS.

---

## 🎯 Raccomandazione

**Per iniziare rapidamente:** Usa **Streamlit Cloud**

**Se Streamlit Cloud non supporta prosail:** Prova **Render** o **Heroku**

**Per produzione enterprise:** Usa **Docker + Cloud Provider**

---

## 📝 Checklist Pre-Deploy

Prima di deployare, assicurati di:

- [ ] Tutti i file necessari sono nel repository
- [ ] `requirements.txt` è aggiornato
- [ ] `app.py` e `sensor_bands.py` sono presenti
- [ ] Nessuna informazione sensibile nel codice
- [ ] Il codice funziona localmente
- [ ] Hai testato `streamlit run app.py` in locale

---

## 🔧 Risoluzione Problemi

### Problema: prosail non si installa

**Soluzione:** 
- Verifica che prosail sia disponibile su PyPI o conda-forge
- Se non disponibile, potrebbe essere necessario un build custom
- Considera di usare un ambiente Docker con conda

### Problema: App lenta online

**Soluzione:**
- I calcoli PROSAIL sono computazionalmente costosi
- Usa `@st.cache_data` (già implementato)
- Considera di ridurre i range dei parametri di default

### Problema: Port non configurato

**Soluzione:**
- Assicurati che il servizio usi la porta corretta
- Streamlit Cloud: automatico
- Altri servizi: usa `--server.port $PORT`

---

## 📞 Supporto

Per problemi con prosail: https://github.com/jgomezdans/prosail/issues

Per problemi con Streamlit: https://discuss.streamlit.io/

