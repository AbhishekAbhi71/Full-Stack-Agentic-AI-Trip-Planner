from datetime import datetime
from typing import Optional

def normalize_date(raw_date: Optional[str]) -> Optional[str]:
    if not raw_date:
        return None
    raw_date = raw_date.strip()
    date_formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d %B %Y",
        "%d %b %Y",
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None