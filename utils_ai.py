import requests
from urllib.parse import urlparse

# Modelli OpenRouter a pagamento, provati in sequenza.
# Controlla lo slug esatto di ogni modello su openrouter.ai/models
PAID_MODELS = [
    "anthropic/claude-haiku-5.5",
    "google/gemini-2.0-flash-001",
    "openai/gpt-4o-mini",
]

# Ricerca web limitata a JW.org
DOMINI_JW = ["jw.org", "wol.jw.org"]
MAX_RISULTATI = 4  # più risultati = risposte più complete, ma costo maggiore

PROMPT_SYSTEM = (
    "Sei un assistente specializzato ed esperto fedele alle pubblicazioni ufficiali dei Testimoni di Geova (jw.org e wol.jw.org). "
    "Il tuo compito è spiegare gli argomenti in modo chiaro e approfondito, assumendo SEMPRE E SOLTANTO "
    "la prospettiva dottrinale e la terminologia della 'Traduzione del Nuovo Mondo' (TNM).\n\n"
    "RICERCA:\n"
    "- Basa la risposta sui risultati della ricerca web provenienti da jw.org e wol.jw.org.\n"
    "- Per un riferimento biblico, cerca il versetto esatto nella Bibbia per lo studio su wol.jw.org.\n"
    "- Se nei risultati non trovi l'informazione, dillo chiaramente invece di inventare.\n\n"
    "DIZIONARIO DI TRADUZIONE E CORREZIONE OBBLIGATORIA (TNM):\n"
    "- Sostituisci SEMPRE 'croce' con 'palo' o 'palo di tortura'.\n"
    "- Sostituisci SEMPRE 'Signore' o 'Dio' con 'Geova' nei passi del Vecchio e Nuovo Testamento dove la TNM usa il Nome Divino.\n"
    "- Usa SEMPRE 'adunanza' (NON 'messa' o 'funzione'), 'sorvegliante' (NON 'vescovo'), 'congregazione' (NON 'chiesa').\n\n"
    "REGOLE PER LE CITAZIONI BIBLICHE:\n"
    "1. DIVIETO DI ALTRE BIBBIE: È severamente vietato riportare versetti tratti dalla CEI, dalla Diodati o dalla Riveduta.\n"
    "2. GESTIONE DELLE CITAZIONI: Riporta un versetto tra virgolette SOLO se il testo esatto della 'Traduzione del Nuovo Mondo' "
    "compare nei risultati della ricerca. Se non hai la certezza assoluta della trascrizione parola per parola, "
    "NON usare virgolette di citazione diretta: spiega il concetto parafrasandolo con la terminologia corretta della TNM "
    "e indica il riferimento (es. Matteo 10:38, TNM).\n"
    "3. TERMINOLOGIA: Usa sempre 'palo di tortura' al posto di 'croce' anche quando parafrasi."
)


def _e_dominio_jw(url: str) -> bool:
    """True se l'indirizzo appartiene a jw.org o a un suo sottodominio."""
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return False
    return host == "jw.org" or host.endswith(".jw.org")


def _estrai_fonti(message: dict) -> list:
    """Legge le fonti (annotations) restituite da OpenRouter e tiene solo quelle JW.org."""
    fonti = []
    for ann in message.get("annotations") or []:
        info = ann.get("url_citation") or {}
        url = info.get("url", "")
        if url and _e_dominio_jw(url) and url not in [f[1] for f in fonti]:
            fonti.append((info.get("title") or url, url))
    return fonti


def esegui_ricerca_jw(user_text: str, api_key: str) -> str:
    """Invia la richiesta a OpenRouter con ricerca web limitata a JW.org,
    provando in sequenza i modelli a pagamento."""
    if not api_key:
        return "⚠️ Errore: Chiave API OpenRouter non trovata nei Secrets!"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "ricercavicjw",
        "Content-Type": "application/json",
    }

    for model in PAID_MODELS:
        data = {
            "model": model,
            "temperature": 0.0,
            "messages": [
                {"role": "system", "content": PROMPT_SYSTEM},
                {"role": "user", "content": user_text},
            ],
            "plugins": [
                {
                    "id": "web",
                    "max_results": MAX_RISULTATI,
                    "include_domains": DOMINI_JW,
                }
            ],
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60,  # la ricerca web richiede più tempo
            )
            res_data = response.json()

            if response.status_code != 200:
                print(f"Errore {response.status_code} con {model}: {res_data}")
                continue

            if "choices" in res_data and len(res_data["choices"]) > 0:
                message = res_data["choices"][0]["message"]
                content = message.get("content")

                if (
                    content
                    and "User Safety:" not in content
                    and "<|tool_call_start|>" not in content
                ):
                    fonti = _estrai_fonti(message)
                    if fonti:
                        elenco = "\n".join(f"- [{t}]({u})" for t, u in fonti)
                        content += f"\n\n**Fonti JW.org:**\n{elenco}"
                    else:
                        content += (
                            "\n\n⚠️ Nessuna fonte JW.org restituita dalla ricerca: "
                            "verifica il testo su wol.jw.org."
                        )
                    return content
        except Exception as e:
            print(f"Errore durante l'interrogazione di {model}: {e}")

    return "⚠️ Il servizio è momentaneamente occupato o i modelli non rispondono. Riprova tra pochissimo!"
  
