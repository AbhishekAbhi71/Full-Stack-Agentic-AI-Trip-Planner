import os
from pathlib import Path
from dotenv import load_dotenv
current_file = Path(__file__).resolve()
base_dir = current_file.parent.parent
env_path = base_dir / ".env"

load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        f"GEMINI_API_KEY is missing inside {env_path}"
    )
    
if not RAPIDAPI_KEY:
    raise ValueError(
        f"RAPIDAPI_KEY is missing inside {env_path}"
    )

CLEANED_GEMINI_KEY = (
    GEMINI_API_KEY.strip()
    .replace('"', "")
    .replace("'", "")
)

CLEANED_RAPIDAPI_KEY = (
    RAPIDAPI_KEY.strip()
    .replace('"', "")
    .replace("'", "")
)

os.environ["GEMINI_API_KEY"] = CLEANED_GEMINI_KEY
os.environ["GOOGLE_API_KEY"] = CLEANED_GEMINI_KEY