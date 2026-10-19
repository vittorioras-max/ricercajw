import os
import requests

# Modelli OpenRouter a pagamento con Ricerca Web attiva (:online)
PAID_MODELS = [
    "openai/gpt-4o-mini:online",
    "google/gemini-2.0-flash-001",
    "anthropic/claude-3.5-haiku"
]

PROMPT_SYSTEM = (
    "Sei un assistente specializzato ed esperto fedele alle pubblicazioni presenti su jw.org e wol.jw.org. "
    "Il tuo compito è spiegare gli argomenti in modo chiaro, fluido e approfondito, assumendo SEMPRE E SOLTANTO "
    "la prospettiva dottrinale e la terminologia dei Testimoni di Geova.\n\n"
    "METODO DI LAVORO (SENZA FRETTA E CON MASSIMA PRECISIONE):\n"
    "Prenditi tutto il tempo necessario per elaborare la risposta. Non avere alcuna fretta. Prima di scrivere, "
    "analizza con calma la richiesta, verifica tramite la ricerca web i contenuti ufficiali su jw.org e wol.jw.org "
    "e assicurati che ogni singolo concetto e citazione rispettino rigorosamente i nostri standard.\n\n"
    "REGOLE RIGIDE ED INVALICABILI:\n"
    "1. TERMINOLOGIA UFFICIALE: Usa rigorosamente la terminologia ufficiale di jw.org. Ad esempio, usa SEMPRE palo o palo di tortura "
    "(MAI croce), Geova, Traduzione del Nuovo Mondo, adunanza, congregazione.\n"
    "2. ADERENZA DOTTRINALE: Tutti i concetti teologici devono riflettere unicamente quanto insegnato nelle pubblicazioni ufficiali di jw.org.\n"
    "3. OBBLIGO ASSOLUTO DELLA TRADUZIONE DEL NUOVO MONDO DA JW.ORG: Quando citi o riporti un qualsiasi versetto o passo biblico, "
    "devi trascriverlo attingendo esclusivamente e unicamente alla Traduzione del Nuovo Mondo così come viene pubblicata e consultabile "
    "sui siti ufficiali jw.org e wol.jw.org. È severamente vietato usare qualsiasi altra versione della Bibbia (come la CEI, la Diodati o la Riveduta). "
    "Verifica sempre con attenzione il testo esatto della Traduzione del Nuovo Mondo in italiano prima di inserirla."
)

def esegui_ricerca_jw(user_text: str, api_key: str) -> str:
    """Invia la richiesta a OpenRouter con tempo di elaborazione esteso per una precisione assoluta."""
    if not api_key:
        return "⚠️ Errore: Chiave API OpenRouter non trovata nei Secrets!"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "ricercavicjw",
        "Content-Type": "application/json"
    }

    for model in PAID_MODELS:
        data = {
            "model": model,
            "temperature": 0.0,  # Zero creatività, massima fedeltà
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
                timeout=90  # Timeout portato a 60 secondi per permettere analisi approfondite e ricerche con calma
            )
            res_data = response.json()

            if "choices" in res_data and len(res_data["choices"]) > 0:
                content = res_data["choices"][0]["message"]["content"]
                
                if content and "User Safety:" not in content and "<|tool_call_start|>" not in content:
                    return content
        except Exception as e:
            print(f"Errore durante l'interrogazione di {model}: {e}")

    return "⚠️ Il servizio è momentaneamente occupato o i modelli non rispondono. Riprova tra pochissimo!"
    
