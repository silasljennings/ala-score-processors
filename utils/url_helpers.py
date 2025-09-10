import httpx
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
import re



# Build MaxPreps scores URL for given state, date, and sport
def build_scores_url(state_code: str, mdy: str, sport: str) -> str:
    """Build MaxPreps scores URL for specific state, date (M/D/YYYY), and sport"""
    return f"https://www.maxpreps.com/{state_code}/{sport.lower()}/scores/?date={httpx.QueryParams({'date': mdy})}"


# Extract date from URL query parameters and convert to ISO format
def parse_date_from_url(url: str | None) -> str:
    """Parse date from MaxPreps URL; fallback to today's date if missing"""
    if not url:
        return datetime.utcnow().strftime("%Y-%m-%d")

    try:
        parsed = urlparse(url)

        # First try query param ?date=MM/DD/YYYY
        date_param = parse_qs(parsed.query).get("date", [None])[0]
        if date_param:
            raw = unquote(date_param)  # decode %2F
            m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", raw)
            if m:
                return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"

        # Fallback: path like /9-10-2025/
        m2 = re.search(r"/(\d{1,2})-(\d{1,2})-(\d{4})/", parsed.path)
        if m2:
            return f"{m2.group(3)}-{int(m2.group(1)):02d}-{int(m2.group(2)):02d}"
    except Exception:
        pass

    # Final fallback: use today's date
    return datetime.utcnow().strftime("%Y-%m-%d")
