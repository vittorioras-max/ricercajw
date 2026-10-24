import streamlit as st
import json
import os
from utils_ai import esegui_ricerca_jw
from storico import salva

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

# --- 2. FUNZIONI DI GESTIONE STORICO (SICURE) ---
def carica_storico():
    if os.path.exists("storico.json"):
        try:
            with open("storico.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

# --- 3. BARRA LATERALE (ACCOUNT, BACKUP, CANCELLAZIONE PROTETTA E STORICO) ---
with st.sidebar:
    st.write("⚙️ **Account**")
    if st.button("🔒 Esci (Logout)", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    st.markdown("---")
    st.write("💾 **Backup dello Storico**")
    storico_corrente = carica_storico()
    if storico_corrente:
        # Pulsante di backup generale per scaricare il file JSON dello storico
        st.download_button(
            label="📥 Scarica Backup",
            data=json.dumps(storico_corrente, ensure_ascii=False, indent=4),
            file_name="backup_storico_ricercavicjw.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.caption("Nessun dato da esportare.")

    st.markdown("---")
    st.write("🗑️ **Zona Pericolosa**")
    pwd_elimina = st.text_input("Password per svuotare:", type="password", key="input_pwd_elimina")
    
    if st.button("🗑️ Svuota Storico", use_container_width=True):
        APP_PWD = st.secrets.get("APP_PASSWORD", "1234")
        if pwd_elimina == APP_PWD:
            # Svuota il file azzerandone il contenuto
            with open("storico.json", "w", encoding="utf-8") as f:
                json.dump([], f)
            st.success("Storico svuotato con successo!")
            st.rerun()
        else:
            st.error("Password errata o vuota!")

    st.markdown("---")
    st.write("📜 **Le tue ricerche**")

# Gestione della selezione dello storico
voce_scelta = None
with st.sidebar:
    if storico_corrente:
        for idx, item in enumerate(storico_corrente):
            etichetta = f"{item.get('data', '')} · {item.get('domanda', '')[:22]}..."
            if st.button(etichetta, key=f"storico_btn_{idx}", use_container_width=True):
                voce_scelta = item
                st.session_state["voce_selezionata"] = item
    else:
        st.caption("Nessuna ricerca salvata.")

# Mantiene la selezione attiva in memoria
if "voce_selezionata" in st.session_state and not voce_scelta:
    voce_scelta = st.session_state["voce_selezionata"]

# --- 4. INTERFACCIA PRINCIPALE ---
st.title("📖 ricercavicjw")
st.caption("Assistente di ricerca e analisi basato sui contenuti ufficiali Watch Tower")

# Se l'utente seleziona una ricerca dallo storico
if voce_scelta:
    st.info(f"📜 **Storico ({voce_scelta.get('data', '')})**")
    st.markdown(f"**Domanda:** {voce_scelta.get('domanda', '')}")
    st.markdown("---")
    
    # Pulsante Copia per lo storico
    if st.button("📝 Copia", key="storico_copia", use_container_width=True):
        st.success("Testo pronto qui sotto:")
        st.code(voce_scelta.get('risposta', ''), language="markdown")
        
    st.markdown("---")
    st.markdown(voce_scelta.get('risposta', ''))
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
        
        # Pulsante Copia per la nuova ricerca
        if st.button("📝 Copia", key="nuovo_copia", use_container_width=True):
            st.success("Testo pronto qui sotto:")
            st.code(risposta, language="markdown")
            
        st.markdown("---")
        st.markdown(risposta)
    else:
        st.warning("Per favore, inserisci un testo prima di avviare la ricerca.")
