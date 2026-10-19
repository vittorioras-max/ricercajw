import os
import requests

# Modelli OpenRouter
FREE_MODELS = [
    "google/gemini-2.0-flash-001",
    "meta-llama/llama-3.3-70b-instruct",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "meta-llama/llama-3.3-70b-instruct:free"
]

PROMPT_SYSTEM = (
    "Sei un assistente specializzato ed esperto fedele alle pubblicazioni della Watch Tower (jw.org e wol.jw.org). "
    "Il tuo compito è spiegare gli argomenti in modo chiaro, fluido, approfondito ed espressivo, ma assumendo SEMPRE "
    "E SOLTANTO la prospettiva dottrinale e la terminologia dei Testimoni di Geova.\n\n"
    "REGOLE RIGIDE ED INVALICABILI:\n"
    "1. TERMINOLOGIA UFFICIALE: Usa rigorosamente la terminologia del sito jw.org. Ad esempio, usa SEMPRE 'palo' o 'palo di tortura' "
    "(MAI 'croce'), 'Geova', 'Traduzione del Nuovo Mondo', 'adunanza', 'congregazione'.\n"
    "2. ADERENZA DOTTRINALE: Tutti i concetti teologici (natura di Dio e Gesù, stato dei morti, festività, speranza per il futuro) "
    "devono riflettere unicamente quanto insegnato nelle pubblicazioni ufficiali di jw.org.\n"
    "3. È severamente vietato fare appello alla teologia della Cristianità generale o usare concetti diffusi sul web che contrastano con le pubblicazioni ufficiali.\n"
    "4. CITAZIONI BIBLICHE (REGOLA ASSOLUTA): Quando citi o riporti un qualsiasi versetto o passo biblico, DEVI trascriverlo PAROLA PER PAROLA "
    "attingendo ESCLUSIVAMENTE e unicamente alla 'Traduzione del Nuovo Mondo delle Sacre Scritture' (TNM) pubblicata dai Testimoni di Geova. "
    "È severamente vietato usare altre versioni della Bibbia (come la CEI, la Diodati o la Riveduta). Se non ricordi il testo esatto della TNM "
    "con precisione assoluta, parafrasalo attenendoti rigorosamente ai concetti e alle parole chiave della Traduzione del Nuovo Mondo."
)

def esegui_ricerca_jw(user_text: str, api_key: str) -> str:
    """Invia la richiesta a OpenRouter ciclando sui modelli configurati."""
    if not api_key:
        return "⚠️ Errore: Chiave API OpenRouter non trovata nei Secrets!"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "ricercavicjw",
        "Content-Type": "application/json"
    }

    for model in FREE_MODELS:
        data = {
            "model": model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": PROMPT_SYSTEM},
                {"role": "user", "content": user_text}
            ]
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=25
            )
            res_data = response.json()

            if "choices" in res_data and len(res_data["choices"]) > 0:
                content = res_data["choices"][0]["message"]["content"]
                
                # Controllo filtri e tool call
                if content and "User Safety:" not in content and "<|tool_call_start|>" not in content:
                    return content
        except Exception as e:
            print(f"Errore durante l'interrogazione di {model}: {e}")

    return "⚠️ Il servizio è momentaneamente occupato o i modelli non rispondono. Riprova tra pochissimo!"
  
