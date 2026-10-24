import streamlit as st
import streamlit.components.v1 as components
from utils_ai import esegui_ricerca_jw
from storico import salva, barra_storico

st.set_page_config(
    page_title="ricercavicjw",
    page_icon="📖",
    layout="centered"
)

# --- 1. FUNZIONE PER I PULSANTI AFFIANCATI (AUDIO E COPIA) ---
def pulsanti_azioni(testo, id_unico):
    """Mostra i pulsanti emoji 🔊 e 📝 affiancati sulla stessa riga"""
    
    # Pulisci il testo per evitare errori nei comandi JavaScript
    testo_pulito = testo.replace("`", "").replace('"', '\\"').replace("\n", " ").replace("'", "\\'")
    
    # HTML unito con Flexbox per mantenere le icone vicine sulla stessa riga
    html_pulsanti = f"""
        <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 10px;">
            <!-- Pulsante Audio -->
            <button onclick="
                window.speechSynthesis.cancel();
                let msg = new SpeechSynthesisUtterance('{testo_pulito}');
                msg.lang = 'it-IT';
                window.currentUtterance = msg;
                window.speechSynthesis.speak(msg);
            " style="font-size:26px; background:none; border:none; cursor:pointer; padding:0;" title="Leggi">
                🔊
            </button>
            
            <!-- Pulsante Copia -->
            <button onclick="
                const el = document.createElement('textarea');
                el.value = `{testo}`;
                document.body.appendChild(el);
                el.select();
                document.execCommand('copy');
                document.body.removeChild(el);
                alert('Testo copiato negli appunti!');
            " style="font-size:26px; background:none; border:none; cursor:pointer; padding:0;" title="Copia">
                📝
            </button>
        </div>
    """
    components.html(html_pulsanti, height=45)

# --- 2. GESTIONE AUTENTICAZIONE ---
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

# --- 3. BARRA LATERALE (LOGOUT E STORICO) ---
with st.sidebar:
    st.write("⚙️ **Account**")
    if st.button("🔒 Esci (Logout)", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown("---")

voce_scelta = barra_storico()

# --- 4. INTERFACCIA PRINCIPALE ---
st.title("📖 ricercavicjw")
st.caption("Assistente di ricerca e analisi basato sui contenuti ufficiali Watch Tower")

# Se l'utente seleziona una ricerca dallo storico
if voce_scelta:
    st.info(f"📜 **Storico ({voce_scelta['data']})**")
    st.markdown(f"**Domanda:** {voce_scelta['domanda']}")
    st.markdown("---")
    
    # Mostra i pulsanti affiancati sopra la risposta dello storico
    pulsanti_azioni(voce_scelta["risposta"], "storico")
    
    st.markdown(voce_scelta["risposta"])
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
        
        # Mostra i pulsanti affiancati sopra la nuova risposta
        pulsanti_azioni(risposta, "nuovo")
        
        st.markdown(risposta)
    else:
        st.warning("Per favore, inserisci un testo prima di avviare la ricerca.")
        
