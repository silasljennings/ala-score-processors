import httpx
from urllib.parse import urlparse, parse_qs


# Build MaxPreps scores URL for given state, date, and sport
def build_scores_url(state_code: str, mdy: str, sport: str) -> str:
    """Build MaxPreps scores URL for specific state, date (M/D/YYYY), and sport"""
    return f"https://www.maxpreps.com/{state_code}/{sport.lower()}/scores/?date={httpx.QueryParams({'date': mdy})}"


# Extract date from URL query parameters and convert to ISO format
def parse_date_from_url(url: str | None) -> str | None:
    """Parse date from URL query parameter and return in YYYY-MM-DD format"""
    if not url:
        return None
    
    try:
        # Extract ?date=mm/dd/yyyy parameter
        parsed = urlparse(url)
        date_param = parse_qs(parsed.query).get("date", [None])[0]
        
        if date_param:
            m, d, y = date_param.split("/")
            return f"{y}-{int(m):02d}-{int(d):02d}"
    except Exception:
        pass
    
    return None