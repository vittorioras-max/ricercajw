import streamlit as st
import json
import os
from utils_ai import esegui_ricerca_jw
from storico import salva

st.set_page_config(
    page_title="ricercavic",
    page_icon="📖",
    layout="centered"
)

# --- 1. GESTIONE AUTENTICAZIONE SICURA CON PERSISTENZA ---
# Recupera la password esclusivamente dai Secrets di Streamlit
APP_PWD = st.secrets.get("APP_PASSWORD", "")

if "authenticated" not in st.session_state:
    if st.query_params.get("auth") == "true":
        st.session_state.authenticated = True
    else:
        st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Accesso a ricercavicjw")
    pwd = st.text_input("Inserisci la password di accesso:", type="password")
    
    if st.button("Accedi", type="primary"):
        if APP_PWD and pwd == APP_PWD:
            st.session_state.authenticated = True
            st.query_params["auth"] = "true"  # Mantiene la sessione attiva al refresh
            st.rerun()
        else:
            st.error("Password errata o non configurata nei Secrets.")
    st.stop()

# --- 2. FUNZIONI PER LO STORICO ---
def carica_storico():
    if os.path.exists("storico.json"):
        try:
            with open("storico.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salva_storico_completo(dati):
    with open("storico.json", "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=4)

storico_corrente = carica_storico()

# --- 3. BARRA LATERALE ---
voce_scelta = None

with st.sidebar:
    # 1. LE TUE RICERCHE (CON CANCELLAZIONE SINGOLA)
    st.write("📜 **Le tue ricerche**")
    pwd_operazioni = st.text_input("Password per eliminare:", type="password", key="pwd_operazioni")
    
    if storico_corrente:
        for idx, item in enumerate(storico_corrente):
            col_btn, col_del = st.columns([5, 1])
            
            with col_btn:
                etichetta = f"{item.get('data', '')} · {item.get('domanda', '')[:18]}..."
                if st.button(etichetta, key=f"storico_btn_{idx}", use_container_width=True):
                    voce_scelta = item
                    st.session_state["voce_selezionata"] = item

            with col_del:
                if st.button("❌", key=f"del_single_{idx}", help="Elimina questa ricerca"):
                    if pwd_operazioni == APP_PWD and APP_PWD != "":
                        storico_corrente.pop(idx)
                        salva_storico_completo(storico_corrente)
                        if "voce_selezionata" in st.session_state and st.session_state["voce_selezionata"] == item:
                            del st.session_state["voce_selezionata"]
                        st.success("Ricerca eliminata!")
                        st.rerun()
                    else:
                        st.error("Password errata!")
    else:
        st.caption("Nessuna ricerca salvata.")

    st.markdown("---")

    # 2. BACKUP
    st.write("💾 **Backup dello Storico**")
    if storico_corrente:
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

    # 3. LOGOUT
    st.write("⚙️ **Account**")
    if st.button("🔒 Esci (Logout)", use_container_width=True):
        st.session_state.authenticated = False
        st.query_params.clear()  # Pulisce l'URL al logout
        st.rerun()

    st.markdown("---")

    # 4. CANCELLA INTERO STORICO
    st.write("⚠️ **Zona Pericolosa**")
    if st.button("🗑️ Cancella TUTTO lo storico", use_container_width=True):
        if pwd_operazioni == APP_PWD and APP_PWD != "":
            salva_storico_completo([])
            if "voce_selezionata" in st.session_state:
                del st.session_state["voce_selezionata"]
            st.success("Tutto lo storico è stato cancellato!")
            st.rerun()
        else:
            st.error("Inserisci la password corretta in alto per confermare!")

# Mantiene la selezione attiva in memoria
if "voce_selezionata" in st.session_state and not voce_scelta:
    voce_scelta = st.session_state["voce_selezionata"]

# --- 4. INTERFACCIA PRINCIPALE ---
st.title("📖 ricercavicjw")
st.caption("Assistente di ricerca e analisi basato sui contenuti ufficiali Watch Tower")

if voce_scelta:
    st.info(f"📜 **Storico ({voce_scelta.get('data', '')})**")
    st.markdown(f"**Domanda:** {voce_scelta.get('domanda', '')}")
    st.markdown("---")
    
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

if btn_avvia:
    if user_query.strip():
        with st.spinner("Ricerca ed elaborazione in corso sui modelli..."):
            risposta = esegui_ricerca_jw(user_query, OPENROUTER_KEY)
            salva(user_query, risposta)
            
        st.markdown("### 📋 Risultato")
        
        if st.button("📝 Copia", key="nuovo_copia", use_container_width=True):
            st.success("Testo pronto qui sotto:")
            st.code(risposta, language="markdown")
            
        st.markdown("---")
        st.markdown(risposta)
    else:
        st.warning("Per favore, inserisci un testo prima di avviare la ricerca.")
