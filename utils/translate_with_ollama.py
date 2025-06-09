import json
import re
import requests
from typing import Dict, Any, Optional # Removed Tuple
import traceback

# --- NEW: Language Detection Library ---
try:
    from langdetect import detect, DetectorFactory, LangDetectException
    from langdetect.lang_detect_exception import LangDetectException as LangDetectError # Alias
    DetectorFactory.seed = 0 
    LANGDETECT_AVAILABLE = True
    print("Successfully imported langdetect.")
except ImportError:
    print("WARNING: 'langdetect' library not found. Language identification will be less reliable or slower if it falls back to LLM. Install with: pip install langdetect")
    LANGDETECT_AVAILABLE = False
    class LangDetectError(Exception): pass # Dummy class

# --- Configuration Constants from your original module ---
OLLAMA_API = "http://10.9.52.21:11435/api/generate" 
# Using IDENTIFICATION_MODEL only as a fallback if langdetect isn't there
# or if you choose to implement an LLM fallback within identify_language.
# For now, we'll make translation always use TRANSLATION_MODEL.
IDENTIFICATION_MODEL = "gemma3:12b-it-qat" # This model is now less critical if langdetect works
TRANSLATION_MODEL = "gemma3:12b-it-qat"    # Or "gemma3:12b"

TEMPERATURE_IDENTIFY = 0.0 # Less relevant now
TEMPERATURE_TRANSLATE = 0.1

# Your original INDIAN_LANGUAGES map (used for naming if langdetect returns a code)
INDIAN_LANGUAGES = {
    "en": "English", 
    "hi": "Hindi", "bn": "Bengali", "te": "Telugu", "mr": "Marathi",
    "ta": "Tamil", "ur": "Urdu", "gu": "Gujarati", "kn": "Kannada",
    "ml": "Malayalam", "pa": "Punjabi", "or": "Odia", "as": "Assamese",
    "sa": "Sanskrit", "sd": "Sindhi", "ks": "Kashmiri", "ne": "Nepali",
    "doi": "Dogri", "kok": "Konkani", "mai": "Maithili", "bho": "Bhojpuri",
    "mni": "Manipuri", "sat": "Santali",
    "unknown": "Unknown"
}

# --- Custom Exception ---
class OllamaError(Exception):
    """Custom exception for Ollama API errors."""
    pass

# --- Core Functions ---

def _query_ollama( # Your original _query_ollama
    prompt: str,
    model: str,
    system_prompt: str = "",
    temperature: float = 0.1
) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "options": {"num_ctx": 18192} 
    }
    if system_prompt:
        payload["system"] = system_prompt
    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        if 'response' in result and isinstance(result['response'], str):
            return result['response'].strip()
        elif 'message' in result and isinstance(result.get('message'), dict) and 'content' in result['message']:
            return result['message']['content'].strip()
        elif isinstance(result, dict) and 'error' in result:
            raise OllamaError(f"Ollama API error: {result['error']}")
        else:
            raise OllamaError(f"Unexpected response from Ollama: {str(result)[:200]}")
    except requests.exceptions.Timeout as e:
         raise OllamaError(f"Timeout connecting to Ollama API at {OLLAMA_API}: {e}")
    except requests.exceptions.ConnectionError as e:
         raise OllamaError(f"Connection refused connecting to Ollama API at {OLLAMA_API}. Is 'ollama serve' running? Error: {e}")
    except requests.exceptions.RequestException as e:
        raise OllamaError(f"Ollama API request failed: {e}")
    except json.JSONDecodeError as e:
        raise OllamaError(f"Failed to decode JSON response from Ollama: {e}. Response: {response.text[:200]}")
    except Exception as e:
        raise OllamaError(f"Unexpected error during Ollama query: {e}")


def identify_language(text: str) -> Dict[str, str]: # MODIFIED to use langdetect
    """
    Identify the language of the input text using langdetect.
    Falls back to a simple 'unknown' if langdetect is not available or fails.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return {"code": "none", "name": "No Text Provided", "source": "input_check"}

    if LANGDETECT_AVAILABLE:
        try:
            # langdetect works best on text with some length.
            # Minimal cleaning for langdetect:
            text_snippet = text[:2000] # Use a reasonable snippet
            if not text_snippet.strip():
                 return {"code": "none", "name": "No discernible text for ID", "source": "langdetect_empty_snippet"}

            lang_code = detect(text_snippet)
            lang_name = INDIAN_LANGUAGES.get(lang_code, f"Other ({lang_code})") # Get name from your map

            # If langdetect returns a language not in our explicit map, we might still
            # consider it for translation but label it carefully.
            # For simplicity, if it's not 'en' and it's a valid code, we'll use it.
            # If it's something langdetect returns but not in your map (e.g. 'fr', 'de'),
            # it will be named "Other (fr)". The translation prompt will just say "from Other (fr)".
            return {"code": lang_code, "name": lang_name, "source": "langdetect"}
        except LangDetectError: # Specifically catch langdetect's exception
            print(f"Langdetect could not reliably identify language for snippet: '{text_snippet[:100]}...'. Marking as unknown.")
            return {"code": "unknown", "name": "Unknown (langdetect error)", "source": "langdetect_error"}
        except Exception as e:
            print(f"Unexpected error during langdetect: {e}")
            return {"code": "unknown", "name": "Unknown (identification error)", "source": "langdetect_exception"}
    else:
        # Fallback if langdetect is not available
        # You could implement your original LLM-based identification here as a fallback
        # For now, just returning unknown.
        print("Langdetect not available. Language identification skipped (marked as unknown).")
        return {"code": "unknown", "name": "Unknown (langdetect unavailable)", "source": "no_identifier"}


def translate_to_english(text: str, source_lang_info: Dict[str, str]) -> str: # Your original translate_to_english
    """
    Translate the input text to English using Ollama. (Using your original prompt structure)
    """
    if not text.strip():
        return "" 

    source_lang_code = source_lang_info.get("code", "unknown")
    source_lang_name = source_lang_info.get("name", "the detected language")

    if source_lang_code == "en": # Already English
        return text
    if source_lang_code == "none":
        return "[No text to translate]"

    # Your original translation prompt structure
    source_description = source_lang_name if source_lang_code != "unknown" else "the source language (which was not confidently identified)"
    
    system_prompt = f"""You are an expert professional translator.
Your primary goal is to translate the following text from {source_description} into **grammatically correct, natural, and fluent English.**

**Crucially, you must strive for the highest degree of accuracy, ensuring that the full meaning, intent, nuances, and tone of the original text are meticulously preserved.**
- Pay close attention to context to ensure the most appropriate word choices.
- If the source text contains idioms or culturally specific phrases, translate them with equivalent expressions in English where possible, or rephrase to convey the intended meaning accurately if a direct equivalent does not exist.
- Maintain the original text's register (e.g., formal, informal, technical).
- Avoid omissions or additions to the content.

If the input text is already in English, return it as is.
Respond ONLY with the English translation. Do not add any extra commentary, greetings, or explanations."""
    
    prompt = f"Translate this to English:\n\n{text}"

    try:
        # Using the configured TRANSLATION_MODEL
        translated_text = _query_ollama(prompt, model=TRANSLATION_MODEL, system_prompt=system_prompt, temperature=TEMPERATURE_TRANSLATE)
        return translated_text
    except Exception as e:
        raise OllamaError(f"Translation query (from {source_lang_name}) failed: {e}")


# --- Main Processing Function for Streamlit App ---
def process_input(text: str, force_translation: bool = False) -> Dict[str, Any]:
    """
    Processes input text: identifies language (with langdetect) and translates to English (with LLM).
    """
    result = {
        "original_text": text,
        "detected_language": {"code": "unknown", "name": "Unknown (Not Processed)", "source": "initial"},
        "translation": None,
        "error": None,
        "note": None
    }

    if not text or not isinstance(text, str) or not text.strip():
        result["error"] = "Input text is empty or invalid."
        result["translation"] = "[No text provided for processing]"
        result["detected_language"] = {"code": "none", "name": "No Text Provided", "source": "input_check"}
        return result

    try:
        # 1. Identify Language using the modified identify_language (which uses langdetect)
        lang_info = identify_language(text)
        result["detected_language"] = lang_info

        if lang_info["code"] == "unknown":
             result["note"] = f"Source language identification: {lang_info['name']}. Translation will be attempted."
        elif lang_info["code"] == "none":
            result["translation"] = "[No discernible text for translation]"
            return result # Early exit if no text for ID

        # 2. Translate to English if needed
        if lang_info["code"] == "en" and not force_translation:
            result["translation"] = text 
            if not result["note"]: result["note"] = "Input text identified as English by langdetect. No LLM translation performed."
        else: # Not English, or forced translation, or unknown (and not 'none')
            print(f"Attempting translation from '{lang_info.get('name', 'unknown')}' to English...")
            result["translation"] = translate_to_english(text, lang_info) # Uses your original translation prompt logic
            if not result["note"] and lang_info["code"] != "unknown": # Add note if not already set by 'unknown' case
                result["note"] = f"Translation attempted from {lang_info.get('name', 'identified source')}."
            elif lang_info["code"] == "unknown" and result["translation"] and not result["translation"].startswith("["):
                result["note"] = (result["note"] or "") + " Translation performed assuming non-English source."


    except OllamaError as e:
        error_message = f"Ollama processing failed: {e}"
        result["error"] = error_message
        result["translation"] = f"[LLM Processing Error: {e}]"
        # If lang ID source was langdetect, it's likely a translation LLM error
        if result["detected_language"]["source"] == "langdetect_error" or result["detected_language"]["source"] == "langdetect_exception":
            pass # lang_info already reflects this
        elif "translation query failed" in str(e).lower(): # Error specifically from translation
            pass # Keep detected lang
        else: # General Ollama error, might be during a fallback ID if implemented, or other config issue
            result["detected_language"] = {"code": "error", "name": "Ollama Comms Error", "source":"ollama_error"}
            
    except Exception as e:
        error_message = f"Unexpected error during processing: {e}\n{traceback.format_exc()}"
        result["error"] = error_message
        result["translation"] = f"[Unexpected System Error: {e}]"
        result["detected_language"] = {"code": "error", "name": "System Processing Error", "source":"system_error"}

    # Final check: ensure translation field is populated if no error
    if result["translation"] is None and result["error"] is None:
        if result["detected_language"]["code"] == "en" and not force_translation:
            result["translation"] = text # Should have been caught above
        else:
            result["translation"] = "[Translation yielded no result or was not attempted]"
            if result["note"] is None: result["note"] = "Translation process completed but yielded no result."
            else: result["note"] += " Translation yielded empty result."
            
    return result


# --- Standalone Test ---
if __name__ == "__main__":
    print("--- Running translation_with_ollama.py (langdetect + Original LLM Translation Prompt) ---")

    test_texts = {
        "Hindi": "यह हिंदी में एक परीक्षण वाक्य है। सीमाओं का विवरण उत्तर में एक्स का घर है।",
        "Telugu": "ఇది తెలుగులో ఒక పరీక్ష వాక్యం. సరిహద్దుల వివరాలు ఉత్తరాన X ఇల్లు ఉంది.",
        "English": "This is a test sentence in English. The property is bounded on the North by X's house.",
        "Tamil": "இது தமிழில் ஒரு சோதனை வாக்கியம். வடக்கு எல்லையில் X என்பவரின் வீடு உள்ளது.",
        "French": "Ceci est une phrase de test en français.", # Test a non-Indian, non-English
        "Empty": "   "
    }

    for lang_name_key, text_content in test_texts.items():
        print(f"\n--- Testing {lang_name_key} ---")
        print(f"Original: {text_content}")
        res = process_input(text_content)
        print(f"Processed: {json.dumps(res, indent=2, ensure_ascii=False)}")

    print("\n--- Forcing translation for English text ---")
    res_en_forced = process_input(test_texts["English"], force_translation=True)
    print(f"Processed (English Forced): {json.dumps(res_en_forced, indent=2, ensure_ascii=False)}")

    print("\n--- Standalone test mode finished ---")