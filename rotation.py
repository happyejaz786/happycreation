import os
from itertools import cycle
from dotenv import load_dotenv

load_dotenv()

# पहले वेरिएबल डिफाइन करें
api_keys = [
    value.strip()
    for key, value in os.environ.items()
    if key.startswith("GEMINI_API_KEY")
    and value.strip()
]

# अब प्रिंट करें, क्योंकि अब api_keys मौजूद है
print(f"DEBUG: Total Keys Loaded: {len(api_keys)}")

MODELS = [
    "gemini-3.1-flash-live",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
    "gemini-2.5-flash-lite"
]

_key_cycle = cycle(api_keys)

def get_next_api_key():
    if not api_keys:
        raise RuntimeError("No GEMINI_API_KEY found in .env")
    key = next(_key_cycle)
    # आप चाहें तो ये डीबग लाइन रख सकते हैं, अब ये एरर नहीं देगी
    print(f"DEBUG: Using Key ending in: {key[-4:]}") 
    return key