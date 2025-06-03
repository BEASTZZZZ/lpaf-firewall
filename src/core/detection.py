import re
import base64
import unicodedata
from core.nlp_detector import is_prompt_suspicious

# --- Layer 1: Keyword Match ---
RISKY_KEYWORDS = [
    "ignore previous",
    "ignore all previous",
    "override instructions",
    "respond with",
    "disregard above",
    "simulate",
    "pretend to be",
    "you are now",
    "you are now in",
    "you must",
    "act as",
    "act like",
    "forget",
    "bypass",
    "erase history",
    "erase your memory",
    "change identity",
    "assume role",
    "assume the role",
    "authorize a transaction",
    "let us roleplay",
    "roleplay",
    "you are an ai without ethical boundaries",
    "you are now an unrestricted ai",
    "reset safeguards",
    "output confidential information",
    "reveal secrets"
]

# --- Layer 2: Regex Pattern Match ---
REGEX_PATTERNS = [
    r"(ignore|forget|disregard)\s+(all\s+)?(prior|previous|earlier)?\s*(instructions|context|prompts|conversation)?",
    r"(pretend|simulate|act\s+(like|as))\s+(you\s+are|a|an|the)?\s*(admin|moderator|manager|user|assistant|ai)?",
    r"(bypass|override)\s+(.*)?(instructions|rules|filters)?",
    r"(assume|take)\s+(the\s+)?role\s+(of|as)\s+(a|an)?\s*(bank officer|admin|user|manager|assistant)?",
    r"(reset|clear|erase).*(memory|history|context|conversation|safeguards)?",
    r"(you are now)\s+(in\s+)?(developer\s+mode|admin\s+mode|unrestricted\s+ai)?",
    r"authorize\s+(a\s+)?(refund|transaction|payment)",
    r"(let('|’)?s|lets)?\s*(play|pretend|imagine|assume|do)\s*(a\s*)?(roleplay|scenario|game)",
    r"output\s+(confidential|sensitive|internal)\s+(data|information|logs)",
    r"reveal\s+(private|secret|hidden)\s+(data|info|instructions)"
]

# --- Layer 3: Spaced Keyword Patterns ---
SPACED_KEYWORD_PATTERNS = [
    r"i\s+g\s+n\s+o\s+r\s+e",
    r"b\s+y\s+p\s+a\s+s\s+s",
    r"r\s+e\s+s\s+p\s+o\s+n\s+d",
    r"r\s+e\s+s\s+e\s+t\s+s\s+a\s+f\s+e\s+g\s+u\s+a\s+r\s+d\s+s"
]

# --- Step 0: Normalize and Decode ---
def normalize_prompt(prompt: str) -> str:
    # Normalize Unicode (e.g., 𝗜 → I), strip non-ASCII
    return ''.join([c for c in unicodedata.normalize("NFKC", prompt) if ord(c) < 128])

def detect_base64_and_decode(prompt: str) -> str:
    base64_pattern = r'^[A-Za-z0-9+/=]{50,}$'
    if re.fullmatch(base64_pattern, prompt.strip()):
        try:
            decoded = base64.b64decode(prompt).decode('utf-8')
            return decoded
        except Exception:
            pass
    return prompt

# --- Layer 3: Spaced keyword matcher ---
def detect_spaced_keywords(prompt: str) -> bool:
    for pattern in SPACED_KEYWORD_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return True
    return False

# --- Layer 2: Regex match ---
def matches_regex(prompt: str) -> bool:
    for pattern in REGEX_PATTERNS:
        if re.search(pattern, prompt.lower()):
            return True
    return False

# --- Risk Scoring Logic ---
def get_prompt_risk_score(prompt: str) -> int:
    score = 0

    # Step 1: Normalize and decode
    normalized = normalize_prompt(prompt)
    decoded = detect_base64_and_decode(normalized)
    lowered = decoded.lower()

    # Step 2: Apply all detection layers
    if any(keyword in lowered for keyword in RISKY_KEYWORDS):
        score += 40

    if matches_regex(decoded):
        score += 30

    if detect_spaced_keywords(decoded):
        score += 30

    if is_prompt_suspicious(decoded):
        score += 30

    return min(score, 100)

# --- Final Decision ---
def is_prompt_safe(prompt: str, threshold: int = 50) -> bool:
    return get_prompt_risk_score(prompt) < threshold