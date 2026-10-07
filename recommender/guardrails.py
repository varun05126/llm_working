"""
SkillHer AI Guardrails Engine
Comprehensive multi-tier safety, prompt injection detection, and content moderation system.
"""
import re
import time
import requests
from django.conf import settings
from django.core.cache import cache

# Patterns associated with prompt injection, jailbreaking, and system prompt extraction
INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)',
    r'forget\s+(all\s+)?(previous|prior|above)\s+(instructions|rules)',
    r'disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|rules)',
    r'reveal\s+(the\s+)?(system\s+prompt|initial\s+prompt|secret\s+key|instructions)',
    r'print\s+(the\s+)?(system\s+prompt|initial\s+instructions)',
    r'what\s+are\s+your\s+(exact\s+)?(system\s+instructions|system\s+prompts)',
    r'you\s+are\s+now\s+in\s+(dan|developer|jailbreak|unfiltered|god)\s+mode',
    r'jailbreak',
    r'bypass\s+(all\s+)?(safety|guardrails|content\s+filters)',
    r'pretend\s+you\s+are\s+(an\s+)?unrestricted',
    r'act\s+as\s+(an\s+)?unfiltered',
    r'roleplay\s+as\s+(an\s+)?evil',
    r'<\s*system\s*>',
    r'\[\s*INST\s*\]',
    r'<<\s*SYS\s*>>',
]

# Patterns associated with toxic, harmful, or malicious behavior
MALICIOUS_PATTERNS = [
    r'\b(ddos|ransomware|keylogger|trojan|malware|botnet)\b',
    r'write\s+(an?\s+)?(exploit|payload|zero-day|sql\s+injection|xss\s+payload)',
    r'how\s+to\s+(hack|breach|crack|infiltrate)\s+(into\s+)?',
    r'create\s+(a\s+)?virus',
    r'steal\s+(credit\s+card|passwords|credentials)',
]

# Rate limiting settings: 30 requests per 60 seconds per IP
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60


def check_rate_limit(client_ip):
    """
    Simple sliding window rate limiter per client IP.
    Returns (is_allowed: bool, remaining_requests: int)
    """
    if not client_ip:
        return True, RATE_LIMIT_MAX_REQUESTS

    cache_key = f"rl_guard_{client_ip}"
    current_time = time.time()
    
    # Store timestamps list in Django cache
    timestamps = cache.get(cache_key) or []
    # Purge timestamps outside the window
    timestamps = [ts for ts in timestamps if current_time - ts < RATE_LIMIT_WINDOW_SECONDS]
    
    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        return False, 0

    timestamps.append(current_time)
    cache.set(cache_key, timestamps, timeout=RATE_LIMIT_WINDOW_SECONDS)
    return True, RATE_LIMIT_MAX_REQUESTS - len(timestamps)


def sanitize_input(text, max_length=1500):
    """
    Sanitizes user input by removing control characters and enforcing length limits.
    """
    if not text:
        return ''
    cleaned = str(text)
    # Remove null bytes and non-printable control characters
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', cleaned)
    return cleaned.strip()[:max_length]


def detect_heuristic_violations(text):
    """
    Fast zero-latency regex check for prompt injection and malicious keywords.
    Returns (is_violation: bool, reason: str)
    """
    text_lower = text.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True, 'Prompt injection or system override pattern detected.'

    for pattern in MALICIOUS_PATTERNS:
        if re.search(pattern, text_lower):
            return True, 'Restricted security or malicious exploit content pattern detected.'

    return False, ''


def check_llama_prompt_guard(text, groq_api_key=None):
    """
    Invokes Meta Llama-Prompt-Guard-2-86M on Groq to calculate injection probability.
    Returns (is_safe: bool, score: float)
    """
    key = groq_api_key or getattr(settings, 'GROQ_API_KEY', None)
    if not key:
        return True, 0.0

    try:
        res = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            json={
                'model': 'meta-llama/llama-prompt-guard-2-86m',
                'messages': [{'role': 'user', 'content': text}],
                'max_tokens': 10
            },
            timeout=3
        )
        if res.status_code == 200:
            score_str = res.json()['choices'][0]['message']['content'].strip()
            score = float(score_str)
            # Threshold: > 0.85 indicates high probability of prompt injection
            if score > 0.85:
                return False, score
            return True, score
    except Exception:
        # Fail safe
        pass

    return True, 0.0


def validate_input_guardrails(text, client_ip=None, groq_api_key=None):
    """
    Comprehensive input guardrail evaluation.
    Returns (is_valid: bool, deflection_message: str, details: dict)
    """
    # 1. Rate Limiting Check
    if client_ip:
        allowed, remaining = check_rate_limit(client_ip)
        if not allowed:
            return False, "Rate limit exceeded. Please wait a moment before sending another request.", {'code': 'RATE_LIMITED'}

    # 2. Length check
    if len(text) > 2000:
        return False, "Input exceeds maximum permissible length (2,000 characters). Please provide a concise message.", {'code': 'LENGTH_EXCEEDED'}

    # 3. Fast Heuristic Check
    violation, reason = detect_heuristic_violations(text)
    if violation:
        return False, (
            "I am Aria, your SkillHer AI Career Mentor, dedicated exclusively to technical learning, career roadmaps, "
            "and professional mentorship. I cannot process instructions attempting to override system behavior or generate harmful material. "
            "How can I assist your career or skills development?"
        ), {'code': 'HEURISTIC_VIOLATION', 'reason': reason}

    # 4. Meta Llama-Prompt-Guard AI Evaluation
    is_safe, score = check_llama_prompt_guard(text, groq_api_key)
    if not is_safe:
        return False, (
            "I am Aria, your SkillHer AI Career Mentor. This request was flagged by our safety guardrail system. "
            "Please ask a question related to your learning path, technical skills, or career goals."
        ), {'code': 'PROMPT_GUARD_AI_VIOLATION', 'score': score}

    return True, '', {'code': 'PASSED', 'score': score}


def moderate_output(text):
    """
    Output guardrail: sanitizes and ensures no sensitive API keys, system tokens, or internal credentials leak.
    """
    if not text:
        return ''

    # Redact any Groq API keys if model accidentally echoes them
    sanitized = re.sub(r'gsk_[A-Za-z0-9_-]{20,}', '[REDACTED_API_KEY]', text)
    # Redact secret key patterns
    sanitized = re.sub(r'django-insecure-[A-Za-z0-9_-]+', '[REDACTED_SECRET]', sanitized)

    return sanitized
