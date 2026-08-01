import os
from pathlib import Path
from dotenv import load_dotenv

# Path resolution
CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not GEMINI_API_KEY:
    raise ValueError(f"❌ GEMINI_API_KEY is missing inside {ENV_PATH}")

if not RAPIDAPI_KEY:
    raise ValueError(f"❌ RAPIDAPI_KEY is missing inside {ENV_PATH}")

CLEANED_GEMINI_KEY = GEMINI_API_KEY.strip().replace('"', "").replace("'", "")
CLEANED_RAPIDAPI_KEY = RAPIDAPI_KEY.strip().replace('"', "").replace("'", "")

os.environ["GEMINI_API_KEY"] = CLEANED_GEMINI_KEY
os.environ["GOOGLE_API_KEY"] = CLEANED_GEMINI_KEY