import regex as re
from datetime import datetime, timedelta
from typing import Optional

def normalize_date(raw_date: Optional[str]) -> Optional[str]:
    """Normalize common date formats and a few relative-date expressions."""
    if not raw_date:
        return None
    raw_date = str(raw_date).strip()
    lowered = raw_date.lower()
    today = datetime.now().date()

    if lowered == "today":
        return today.strftime("%Y-%m-%d")
    if lowered in {"tomorrow", "tmrw"}:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    weekday_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
    }
    match = re.fullmatch(
        r"next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        lowered,
    )
    if match:
        target = weekday_map[match.group(1)]
        days_ahead = (target - today.weekday()) % 7
        days_ahead = 7 if days_ahead == 0 else days_ahead
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    formats_with_year = [
        "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y",
        "%d %B %Y", "%d %b %Y", "%B %d %Y", "%b %d %Y",
    ]
    for fmt in formats_with_year:
        try:
            return datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    formats_without_year = ["%d %b", "%d %B", "%d-%m", "%d/%m", "%b %d", "%B %d"]
    for fmt in formats_without_year:
        try:
            parsed = datetime.strptime(raw_date, fmt).date().replace(year=today.year)
            if parsed < today:
                parsed = parsed.replace(year=today.year + 1)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None