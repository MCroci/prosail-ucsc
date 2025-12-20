"""
Wrapper per eseguire Streamlit su Vercel
⚠️ ATTENZIONE: Questo NON funziona bene con Streamlit su Vercel
Streamlit richiede un server continuo, Vercel è serverless.
"""

# Questa è solo una dimostrazione - NON raccomandato
# Streamlit non funziona correttamente in ambiente serverless

from vercel import vercel

@vercel()
def handler(request):
    # Streamlit richiede un server web continuo
    # Vercel esegue funzioni serverless che terminano dopo ogni richiesta
    # Questo NON funzionerà correttamente
    return {
        'statusCode': 200,
        'body': 'Streamlit non può essere eseguito su Vercel. Usa Streamlit Cloud invece.'
    }

