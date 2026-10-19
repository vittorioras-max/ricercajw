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
    "REGOLE RIGIDE ED INVALICABILI:\n"
    "1. TERMINOLOGIA UFFICIALE: Usa rigorosamente la terminologia ufficiale di jw.org. Ad esempio, usa SEMPRE palo o palo di tortura "
    "(MAI croce), Geova, Traduzione del Nuovo Mondo, adunanza, congregazione.\n"
    "2. ADERENZA DOTTRINALE: Tutti i concetti teologici devono riflettere unicamente quanto insegnato nelle pubblicazioni ufficiali di jw.org.\n"
    "3. OBBLIGO ASSOLUTO DELLA TRADUZIONE DEL NUOVO MONDO DA JW.ORG: Quando citi o riporti un qualsiasi versetto o passo biblico, "
    "devi trascriverlo attingendo esclusivamente e unicamente alla Traduzione del Nuovo Mondo così come viene pubblicata e consultabile "
    "sui siti ufficiali jw.org e wol.jw.org. È severamente vietato usare qualsiasi altra versione della Bibbia (come la CEI, la Diodati o la Riveduta). "
    "Sfrutta la ricerca web per verificare sul sito ufficiale jw.org il testo esatto della Traduzione del Nuovo Mondo in italiano. "
    "Se non possiedi la trascrizione letterale identica della TNM per quel determinato versetto, NON usare virgolette per citazioni dirette, "
    "ma spiega il significato del versetto parafrasandolo fedelmente secondo la terminologia ufficiale dei Testimoni di Geova."
)

def esegui_ricerca_jw(user_text: str, api_key: str) -> str:
    """Invia la richiesta a OpenRouter ciclando sui modelli configurati con ricerca web attiva."""
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
            "temperature": 0.0,  # Massima precisione ed aderenza al testo
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
                timeout=30  # Timeout leggermente più alto per consentire la ricerca web
            )
            res_data = response.json()

            if "choices" in res_data and len(res_data["choices"]) > 0:
                content = res_data["choices"][0]["message"]["content"]
                
                if content and "User Safety:" not in content and "<|tool_call_start|>" not in content:
                    return content
        except Exception as e:
            print(f"Errore durante l'interrogazione di {model}: {e}")

    return "⚠️ Il servizio è momentaneamente occupato o i modelli non rispondono. Riprova tra pochissimo!"
    
