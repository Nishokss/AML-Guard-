import re
from datetime import datetime

def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", str(value).lower()).strip()

def current_month() -> str:
    return datetime.now().strftime("%Y-%m")

def safe_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
