import streamlit as st
from utils_ai import esegui_ricerca_jw
from storico import salva, barra_storico

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
    
    APP_PWD = st.secrets.get("APP_PASSWORD", "1234")
    
    if st.button("Accedi", type="primary"):
        if pwd == APP_PWD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password errata. Riprova.")
    st.stop()

# --- BARRA LATERALE (STORICO & LOGOUT) ---
with st.sidebar:
    st.write("⚙️ **Account**")
    if st.button("🔒 Esci (Logout)", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    st.markdown("---")

# Gestione dello storico nella sidebar
voce_scelta = barra_storico()

# 2. Interfaccia Principale dell'App
st.title("📖 ricercavicjw")
st.caption("Assistente di ricerca e analisi basato sui contenuti ufficiali Watch Tower")

if voce_scelta:
    st.info(f"📜 **Storico ({voce_scelta['data']})**")
    st.markdown(f"**Domanda:** {voce_scelta['domanda']}")
    st.markdown("---")
    st.markdown(voce_scelta["risposta"])
    st.markdown("---")

OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

# Inizializza la variabile per il testo della ricerca
if "testo_ricerca" not in st.session_state:
    st.session_state.testo_ricerca = ""

# Funzione per pulire la casella di testo
def pulisci_testo():
    st.session_state.testo_ricerca = ""

# Area per inserire la domanda (pulsanti verticali comodi per il pollice)
user_query = st.text_area(
    "Inserisci l'argomento, il passo biblico o il testo da analizzare:",
    height=150,
    placeholder="Es: Cerca testi sull'incoraggiamento oppure incolla un paragrafo da analizzare...",
    key="testo_ricerca"
)

btn_avvia = st.button("🔍 Avvia Ricerca", type="primary", use_container_width=True)
btn_clear = st.button("🗑️ Clear", type="secondary", use_container_width=True, on_click=pulisci_testo)

# Esecuzione della ricerca
if btn_avvia:
    if user_query.strip():
        with st.spinner("Ricerca ed elaborazione in corso sui modelli..."):
            risposta = esegui_ricerca_jw(user_query, OPENROUTER_KEY)
            salva(user_query, risposta)
            
        st.markdown("### 📋 Risultato")
        st.markdown(risposta)
    else:
        st.warning("Per favore, inserisci un testo prima di avviare la ricerca.")
        
