# src/core/detection.py

RISKY_KEYWORDS = [
    "ignore previous",
    "override instructions",
    "respond with",
    "disregard above",
    "simulate",
    "pretend to be",
    "you are now"
]

def is_prompt_safe(prompt: str) -> bool:
    """
    Check if the user prompt contains suspicious patterns.
    Returns False if risky content is found.
    """
    lowered = prompt.lower()
    for keyword in RISKY_KEYWORDS:
        if keyword in lowered:
            return False
    return True