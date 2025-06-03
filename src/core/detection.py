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
    "reveal secrets",
    "tell me how to hack",
    "how to hack",
    "hack a server",
    "bypass login",
    "exploit vulnerability",
    "gain unauthorized access",
    "disable security",
    "ddos",
    "phish",
    "inject code",
    "sql injection",
    "backdoor"
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
    r"reveal\s+(private|secret|hidden)\s+(data|info|instructions)",
    r"(how\s+to\s+)?(hack|ddos|phish|exploit|steal|bypass|disable|backdoor|inject)\s+(a\s+)?(server|system|account|login|database|api)?",
    r"(gain|get|obtain)\s+(unauthorized\s+)?(access|entry)\s+(to\s+)?(.*)?",
    r"(disable|evade|bypass)\s+(firewall|security|authentication|authorization)"
]

# --- Layer 3: Spaced Keyword Patterns ---
SPACED_KEYWORD_PATTERNS = [
    r"i\s+g\s+n\s+o\s+r\s+e",
    r"b\s+y\s+p\s+a\s+s\s+s",
    r"r\s+e\s+s\s+p\s+o\s+n\s+d",
    r"r\s+e\s+s\s+e\s+t\s+s\s+a\s+f\s+e\s+g\s+u\s+a\s+r\s+d\s+s",
    r"h\s+a\s+c\s+k",
    r"d\s+d\s+o\s+s",
    r"p\s+h\s+i\s+s\s+h",
    r"s\s+q\s+l\s+i\s+n\s+j\s+e\s+c\s+t\s+i\s+o\s+n"
]

# --- Step 0: Unicode Normalize and Collapse Stylized Text ---
def normalize_prompt(prompt: str) -> str:
    # Normalize Unicode characters (e.g., 𝗜 → I, 𝘪 → i, 𝓘 → I)
    nfkc = unicodedata.normalize("NFKC", prompt)

    # Remove remaining non-ASCII characters (safety cleanup)
    ascii_clean = ''.join(c for c in nfkc if ord(c) < 128)

    # Collapse multiple spaces
    return re.sub(r'\s+', ' ', ascii_clean).strip()

# --- Step 1: Detect Base64 and Decode if Possible ---
def detect_base64_and_decode(prompt: str) -> str:
    base64_pattern = r'^[A-Za-z0-9+/=]{50,}$'
    if re.fullmatch(base64_pattern, prompt.strip()):
        try:
            decoded = base64.b64decode(prompt).decode('utf-8')
            return decoded
        except Exception:
            pass
    return prompt

# --- Step 2: Join Spaced Letters to Reconstruct Intent ---
def remove_spaces_between_letters(prompt: str) -> str:
    words = prompt.split()
    output = []
    buffer = []

    def is_letter_sequence(seq):
        return all(len(c) == 1 and c.isalpha() for c in seq)

    for word in words:
        buffer.append(word)
        if is_letter_sequence(buffer):
            continue
        elif len(buffer) > 1:
            joined = ''.join(buffer[:-1])
            if is_letter_sequence(buffer[:-1]):
                output.append(joined)
                buffer = [buffer[-1]]
            else:
                output.extend(buffer[:-1])
                buffer = [buffer[-1]]

    if buffer:
        if is_letter_sequence(buffer):
            output.append(''.join(buffer))
        else:
            output.extend(buffer)

    return ' '.join(output)

# --- Layer 3: Spaced Keyword Matcher ---
def detect_spaced_keywords(prompt: str) -> bool:
    for pattern in SPACED_KEYWORD_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return True
    return False

# --- Layer 2: Regex Match ---
def matches_regex(prompt: str) -> bool:
    for pattern in REGEX_PATTERNS:
        if re.search(pattern, prompt.lower()):
            return True
    return False

# --- Risk Scoring Logic ---
def get_prompt_risk_score(prompt: str) -> int:
    score = 0

    # Step 1: Normalize → Decode → De-obfuscate
    normalized = normalize_prompt(prompt)
    decoded = detect_base64_and_decode(normalized)
    unspaced = remove_spaces_between_letters(decoded)
    lowered = unspaced.lower()

    # Step 2: Run detection layers
    if any(keyword in lowered for keyword in RISKY_KEYWORDS):
        score += 40

    if matches_regex(lowered):
        score += 30

    if detect_spaced_keywords(decoded):  # work on original prompt with spacing
        score += 30

    if is_prompt_suspicious(lowered):  # from NLP or ML logic
        score += 30

    return min(score, 100)

# --- Final Decision ---
def is_prompt_safe(prompt: str, threshold: int = 50) -> bool:
    return get_prompt_risk_score(prompt) < threshold