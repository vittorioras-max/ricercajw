import streamlit as st
from utils_ai import esegui_ricerca_jw
from storico import salva, barra_storico

st.set_page_config(
    page_title="ricercavicjw",
    page_icon="📖",
    layout="centered"
)

# --- 1. GESTIONE AUTENTICAZIONE ---
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

# --- 2. BARRA LATERALE (LOGOUT E STORICO) ---
with st.sidebar:
    st.write("⚙️ **Account**")
    if st.button("🔒 Esci (Logout)", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown("---")

voce_scelta = barra_storico()

# --- 3. INTERFACCIA PRINCIPALE ---
st.title("📖 ricercavicjw")
st.caption("Assistente di ricerca e analisi basato sui contenuti ufficiali Watch Tower")

# Se l'utente seleziona una ricerca dallo storico
if voce_scelta:
    st.info(f"📜 **Storico ({voce_scelta['data']})**")
    st.markdown(f"**Domanda:** {voce_scelta['domanda']}")
    st.markdown("---")
    
    st.markdown(voce_scelta["risposta"])
    
    # Pulsanti nativi sotto la risposta dello storico
    col_a, col_b, _ = st.columns([1, 1, 4])
    with col_a:
        if st.button("🔊 Leggi", key="storico_audio", use_container_width=True):
            st.info("💡 Usa la funzione di lettura dello schermo del tuo telefono o browser.")
    with col_b:
        if st.button("📝 Copia", key="storico_copia", use_container_width=True):
            st.write(f"Testo pronto da copiare: `{voce_scelta['risposta']}`")
            
    st.markdown("---")

OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

if "testo_ricerca" not in st.session_state:
    st.session_state.testo_ricerca = ""

def pulisci_testo():
    st.session_state.testo_ricerca = ""

user_query = st.text_area(
    "Inserisci l'argomento, il passo biblico o il testo da analizzare:",
    height=150,
    placeholder="Es: Cerca testi sull'incoraggiamento oppure incolla un paragrafo da analizzare...",
    key="testo_ricerca"
)

btn_avvia = st.button("🔍 Avvia Ricerca", type="primary", use_container_width=True)
btn_clear = st.button("🗑️ Clear", type="secondary", use_container_width=True, on_click=pulisci_testo)

# Risultato della nuova ricerca
if btn_avvia:
    if user_query.strip():
        with st.spinner("Ricerca ed elaborazione in corso sui modelli..."):
            risposta = esegui_ricerca_jw(user_query, OPENROUTER_KEY)
            salva(user_query, risposta)
            
        st.markdown("### 📋 Risultato")
        st.markdown(risposta)
        
        # Pulsanti nativi sotto la nuova risposta
        col_c, col_d, _ = st.columns([1, 1, 4])
        with col_c:
            if st.button("🔊 Leggi", key="nuovo_audio", use_container_width=True):
                st.info("💡 Usa la funzione di lettura dello schermo del tuo telefono o browser.")
        with col_d:
            if st.button("📝 Copia", key="nuovo_copia", use_container_width=True):
                st.write(f"Testo pronto da copiare: `{risposta}`")
    else:
        st.warning("Per favore, inserisci un testo prima di avviare la ricerca.")
