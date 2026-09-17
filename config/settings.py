from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DB_PATH = Path(os.getenv("AML_DB_PATH", ROOT / "aml.db"))
DATA_DIR = ROOT / "data"
REGULATIONS_DIR = DATA_DIR / "regulations"
LARGE_TRANSACTION_THRESHOLD = float(os.getenv("LARGE_TRANSACTION_THRESHOLD", "1000000"))
HIGH_RISK_COUNTRIES = {"IRAN", "NORTH KOREA", "SYRIA", "MYANMAR"}
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_API_KEY = os.getenv("GROQ_API_KEY") if LLM_PROVIDER == "groq" else os.getenv("OPENAI_API_KEY")
DEMO_MODE = not bool(LLM_API_KEY)
