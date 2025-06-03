import spacy

# Load spaCy's English NLP model
nlp = spacy.load("en_core_web_sm")

# Define suspicious command verbs attackers might use
SUSPICIOUS_VERBS = {
    "ignore", "override", "pretend", "respond", "simulate", "disregard", "act", "bypass"
}

def is_prompt_suspicious(prompt: str) -> bool:
    """
    Analyzes the prompt for suspicious verb usage using NLP.
    Returns True if it contains potentially dangerous instructions.
    """
    doc = nlp(prompt)

    for token in doc:
        if token.lemma_ in SUSPICIOUS_VERBS and token.tag_ in {"VB", "VBP"}:
            return True

    return False