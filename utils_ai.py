import os
import requests

# Modelli OpenRouter a pagamento (senza scraping diretto per evitare blocchi)
PAID_MODELS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-3.5-haiku",
    "google/gemini-2.0-flash-001"
]

PROMPT_SYSTEM = (
    "Sei un assistente specializzato ed esperto fedele alle pubblicazioni ufficiali dei Testimoni di Geova (jw.org e wol.jw.org). "
    "Il tuo compito è spiegare gli argomenti in modo chiaro e approfondito, assumendo SEMPRE E SOLTANTO "
    "la prospettiva dottrinale e la terminologia della 'Traduzione del Nuovo Mondo' (TNM).\n\n"
    "DIZIONARIO DI TRADUZIONE E CORREZIONE OBBLIGATORIA (TNM):\n"
    "- Sostituisci SEMPRE 'croce' con 'palo' o 'palo di tortura'.\n"
    "- Sostituisci SEMPRE 'Signore' o 'Dio' con 'Geova' nei passi del Vecchio e Nuovo Testamento dove la TNM usa il Nome Divino.\n"
    "- Usa SEMPRE 'adunanza' (NON 'messa' o 'funzione'), 'sorvegliante' (NON 'vescovo'), 'congregazione' (NON 'chiesa').\n\n"
    "REGOLE PER LE CITAZIONI BIBLICHE:\n"
    "1. DIVIETO DI ALTRE BIBBIE: È severamente vietato riportare versetti tratti dalla CEI, dalla Diodati o dalla Riveduta.\n"
    "2. GESTIONE DELLE CITAZIONI: Se non hai la certezza assoluta dell'esatta trascrizione parola per parola della 'Traduzione del Nuovo Mondo', "
    "NON inserire virgolette di citazione diretta. Spiega invece il concetto del versetto parafrasandolo con la terminologia corretta della TNM.\n"
    "3. ESEMPIO DI CORREZIONE: Se ricordi un versetto come 'Chi non prende la sua croce e non mi segue...', devi OBBLIGATORIAMENTE "
    "scrivere: 'E chi non accetta il suo palo di tortura e non mi segue non è degno di me (Matteo 10:38, TNM)'."
)

def esegui_ricerca_jw(user_text: str, api_key: str) -> str:
    """Invia la richiesta a OpenRouter ciclando sui modelli a pagamento con vincoli terminologici rigidi."""
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
            "temperature": 0.0,
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
                timeout=30
            )
            res_data = response.json()

            if "choices" in res_data and len(res_data["choices"]) > 0:
                content = res_data["choices"][0]["message"]["content"]
                
                if content and "User Safety:" not in content and "<|tool_call_start|>" not in content:
                    return content
        except Exception as e:
            print(f"Errore durante l'interrogazione di {model}: {e}")

    return "⚠️ Il servizio è momentaneamente occupato o i modelli non rispondono. Riprova tra pochissimo!"
    
