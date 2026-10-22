import base64
import json
from datetime import datetime

import requests
import streamlit as st

FILE_LOCALE = "storico.json"      # copia locale (si perde al riavvio dell'app)
PERCORSO_REPO = "storico.json"    # file salvato nel repository GitHub
MAX_VOCI = 100                    # ultime 100 ricerche (limite dimensione file GitHub)


# ---------- Configurazione GitHub (da Secrets di Streamlit) ----------
def _config():
    """Restituisce (token, repo, branch) oppure None se GitHub non è configurato."""
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]  # es. "tuoutente/ricercajw"
        branch = st.secrets.get("GITHUB_BRANCH", "storico")
        return token, repo, branch
    except Exception:
        return None


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _url(repo):
    return f"https://api.github.com/repos/{repo}/contents/{PERCORSO_REPO}"


def _leggi_github(cfg):
    """Restituisce (ok, voci, sha). ok=False se GitHub non risponde correttamente."""
    token, repo, branch = cfg
    try:
        r = requests.get(
            _url(repo), headers=_headers(token), params={"ref": branch}, timeout=15
        )
    except requests.RequestException as e:
        print(f"GitHub lettura: {e}")
        return False, [], None
    if r.status_code == 404:  # file non ancora creato
        return True, [], None
    if r.status_code != 200:
        print(f"GitHub lettura {r.status_code}: {r.text[:200]}")
        return False, [], None
    info = r.json()
    try:
        voci = json.loads(base64.b64decode(info["content"]).decode("utf-8"))
    except Exception:
        voci = []
    return True, (voci if isinstance(voci, list) else []), info.get("sha")


def _scrivi_github(cfg, voci) -> bool:
    token, repo, branch = cfg
    contenuto = base64.b64encode(
        json.dumps(voci, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("ascii")
    for _ in range(2):  # secondo tentativo se il file è cambiato nel frattempo
        ok, _, sha = _leggi_github(cfg)
        if not ok:
            return False
        corpo = {
            "message": f"storico {datetime.now():%d/%m/%Y %H:%M}",
            "content": contenuto,
            "branch": branch,
        }
        if sha:
            corpo["sha"] = sha
        try:
            r = requests.put(_url(repo), headers=_headers(token), json=corpo, timeout=20)
        except requests.RequestException as e:
            print(f"GitHub scrittura: {e}")
            return False
        if r.status_code in (200, 201):
            return True
        if r.status_code == 409:
            continue
        print(f"GitHub scrittura {r.status_code}: {r.text[:200]}")
        return False
    return False


# ---------- Copia locale ----------
def _leggi_locale() -> list:
    try:
        with open(FILE_LOCALE, "r", encoding="utf-8") as f:
            dati = json.load(f)
            return dati if isinstance(dati, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _scrivi_locale(voci: list) -> None:
    try:
        with open(FILE_LOCALE, "w", encoding="utf-8") as f:
            json.dump(voci, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Impossibile salvare la copia locale: {e}")


# ---------- Funzioni usate dall'app ----------
def carica() -> list:
    """Carica lo storico (una volta per sessione, poi dalla memoria)."""
    if "storico_cache" in st.session_state:
        return st.session_state["storico_cache"]
    cfg = _config()
    voci, sync = None, False
    if cfg:
        ok, voci_gh, _ = _leggi_github(cfg)
        if ok:
            voci, sync = voci_gh, True
    if voci is None:
        voci = _leggi_locale()
    st.session_state["storico_cache"] = voci
    st.session_state["storico_sync"] = sync
    return voci


def _salva_tutto(voci: list) -> None:
    st.session_state["storico_cache"] = voci
    _scrivi_locale(voci)
    cfg = _config()
    if cfg is None:
        st.warning("Storico non permanente: GitHub non è configurato nei Secrets.")
    elif not st.session_state.get("storico_sync", False):
        st.warning("GitHub non raggiungibile: salvato solo in locale. Ricarica la pagina.")
    elif not _scrivi_github(cfg, voci):
        st.warning("⚠️ Salvataggio su GitHub non riuscito: scarica lo storico dal menu laterale.")


def salva(domanda: str, risposta: str) -> dict:
    """Aggiunge una ricerca in cima allo storico e la restituisce."""
    voce = {
        "data": datetime.now().strftime("%d/%m %H:%M"),
        "domanda": domanda,
        "risposta": risposta,
    }
    _salva_tutto(([voce] + carica())[:MAX_VOCI])
    return voce


def svuota() -> None:
    carica()
    _salva_tutto([])


def barra_storico():
    """Disegna lo storico nella barra laterale.
    Restituisce la voce scelta (o l'ultima ricerca) da mostrare, oppure None."""
    with st.sidebar:
        st.header("📜 Storico")
        voci = carica()
        if not voci:
            st.caption("Ancora vuoto.")
        for i, v in enumerate(voci):
            etichetta = f"{v['data']} · {v['domanda'][:35]}"
            if st.button(etichetta, key=f"storico_{i}", use_container_width=True):
                st.session_state["voce_scelta"] = v

        if voci:
            st.download_button(
                "⬇️ Scarica storico",
                data=json.dumps(voci, ensure_ascii=False, indent=2),
                file_name="storico.json",
                mime="application/json",
                use_container_width=True,
            )
            if st.button("🗑️ Svuota storico", use_container_width=True):
                svuota()
                st.session_state.pop("voce_scelta", None)
                st.rerun()

    return st.session_state.get("voce_scelta")
  
