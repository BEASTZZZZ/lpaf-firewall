# src/utils/logger.py
import logging
from datetime import datetime

# Setup logger
logging.basicConfig(
    filename="lpaf.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_prompt(prompt: str, status: str):
    """
    Log prompt status to lpaf.log
    :param prompt: User input
    :param status: 'safe' or 'blocked'
    """
    msg = f"Prompt: {prompt.strip()} | Status: {status.upper()}"
    if status == "blocked":
        logging.warning(msg)
    else:
        logging.info(msg)