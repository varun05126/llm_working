import json
import logging
import re
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GROQ_ENDPOINT = 'https://api.groq.com/openai/v1/chat/completions'
DEFAULT_MODEL = getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile') or 'llama-3.3-70b-versatile'
REQUEST_TIMEOUT = 18  # seconds


def clean_json_text(text: str) -> str:
    """Extract and parse pure JSON from LLM text containing backticks or prose."""
    if not text:
        return ''
    text = text.strip()
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        text = match.group(1).strip()
    return text


def query_groq(messages: list, response_format_json: bool = True, temperature: float = 0.2, retries: int = 1) -> dict | None:
    """
    Call Groq API with robust timeouts, retries, and strict JSON parsing.
    Returns parsed JSON dict (if response_format_json=True) or response text/None.
    Never raises an uncaught exception.
    """
    api_key = getattr(settings, 'GROQ_API_KEY', '') or ''
    if not api_key:
        logger.warning("GROQ_API_KEY is not configured. Falling back to deterministic engine.")
        return None

    model = getattr(settings, 'GROQ_MODEL', DEFAULT_MODEL) or DEFAULT_MODEL
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    payload = {
        'model': model,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': 3500,
    }

    if response_format_json:
        payload['response_format'] = {'type': 'json_object'}

    for attempt in range(retries + 1):
        try:
            response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                if not response_format_json:
                    return {'raw_text': content}
                
                cleaned = clean_json_text(content)
                parsed = json.loads(cleaned)
                return parsed
            else:
                logger.warning(f"Groq API returned status {response.status_code}: {response.text[:200]}")
        except json.JSONDecodeError as jde:
            logger.warning(f"Groq returned malformed JSON on attempt {attempt + 1}: {jde}")
            if attempt < retries:
                # Add a repair prompt for retry
                messages.append({
                    'role': 'user',
                    'content': 'Your previous output was not valid JSON. Please output only strict, valid JSON matching the exact schema requested with no markdown text.'
                })
        except requests.exceptions.Timeout:
            logger.warning(f"Groq API timed out after {REQUEST_TIMEOUT}s on attempt {attempt + 1}")
        except Exception as e:
            logger.error(f"Groq API request error on attempt {attempt + 1}: {e}")

    return None
