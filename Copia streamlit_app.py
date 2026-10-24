import streamlit as st
from utils_ai import esegui_ricerca_jw
from storico import salva, barra_storico  # <-- Import per lo storico

# Configurazione della pagina
st.set_page_config(
    page_title="ricercavicjw",
    page_icon="📖",
    layout="centered"
)

# 1. Gestione Autenticazione con Password
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Accesso a ricercavicjw")
    pwd = st.text_input("Inserisci la password di accesso:", type="password")
    
    # Prende la password dai Secrets o usa "1234" di default
    APP_PWD = st.secrets.get("APP_PASSWORD", "1234")
    
    if st.button("Accedi", type="primary"):
        if pwd == APP_PWD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password errata. Riprova.")
    st.stop()

# --- BARRA LATERALE STORICO ---
# Disegna lo storico nella sidebar e gestisce la selezione di una ricerca passata
voce_scelta = barra_storico()

# 2. Interfaccia Principale dell'App
st.title("📖 ricercavicjw")
st.caption("Assistente di ricerca e analisi basato sui contenuti ufficiali Watch Tower")

# Se l'utente ha toccato una voce dallo storico nella barra laterale, la mostra qui
if voce_scelta:
    st.info(f"📜 **Storico ({voce_scelta['data']})**")
    st.markdown(f"**Domanda:** {voce_scelta['domanda']}")
    st.markdown("---")
    st.markdown(voce_scelta["risposta"])
    st.markdown("---")

# Recupera la chiave OpenRouter dai Secrets
OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

# Area per inserire la domanda o il testo da analizzare
user_query = st.text_area(
    "Inserisci l'argomento, il passo biblico o il testo da analizzare:",
    height=150,
    placeholder="Es: Cerca testi sull'incoraggiamento oppure incolla un paragrafo da analizzare..."
)

if st.button("🔍 Avvia Ricerca", type="primary", use_container_width=True):
    if user_query.strip():
        with st.spinner("Ricerca ed elaborazione in corso sui modelli..."):
            risposta = esegui_ricerca_jw(user_query, OPENROUTER_KEY)
            
            # Salva la ricerca appena completata nel ramo 'storico' su GitHub
            salva(user_query, risposta)
            
        st.markdown("### 📋 Risultato")
        st.markdown(risposta)
    else:
        st.warning("Per favore, inserisci un testo prima di avviare la ricerca.")
