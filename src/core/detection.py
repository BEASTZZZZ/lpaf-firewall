# src/core/detection.py

RISKY_KEYWORDS = [
    "ignore previous",
    "ignore all previous",
    "override instructions",
    "respond with",
    "disregard above",
    "simulate",
    "pretend to be",
    "you are now",
    "you must",
    "act as",
    "disregard earlier"
]

def is_prompt_safe(prompt: str) -> bool:
    """
    Checks if the prompt contains any known risky patterns.
    Returns False if any risky keyword is found.
    """
    lowered = prompt.lower()
    return not any(keyword in lowered for keyword in RISKY_KEYWORDS)