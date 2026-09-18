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
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
LLM_API_KEY = {
	"gemini": os.getenv("GEMINI_API_KEY"),
	"groq": os.getenv("GROQ_API_KEY"),
	"openai": os.getenv("OPENAI_API_KEY"),
}.get(LLM_PROVIDER)
LLM_MODEL = os.getenv(
	"GROQ_MODEL" if LLM_PROVIDER == "groq" else "GEMINI_MODEL",
	"openai/gpt-oss-20b" if LLM_PROVIDER == "groq" else "gemini-3.6-flash",
)
DEMO_MODE = not bool(LLM_API_KEY)
