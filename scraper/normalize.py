from __future__ import annotations

from datetime import datetime


def parse_date(raw: str) -> datetime | None:
    
    raw = raw.strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%d/%m/%Y")
    except ValueError:
        return None


def clean_text(raw: str) -> str:
    return " ".join(raw.split())