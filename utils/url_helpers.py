import httpx
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
import re


# Sports that require gender in MaxPreps URL path
GENDER_REQUIRED_SPORTS = {
    ("basketball", "girls"),
    ("volleyball", "boys")
}



# Build MaxPreps scores URL for given state, date, and sport with optional gender support
def build_scores_url(state_code: str, mdy: str, sport: str, gender: str = None) -> str:
    """Build MaxPreps scores URL with optional gender support

    Args:
        state_code: State abbreviation (e.g., 'ca', 'al')
        mdy: Date in M/D/YYYY format
        sport: Base sport name (e.g., 'basketball', 'volleyball', 'football')
        gender: Optional gender ("boys" or "girls")

    URL patterns:
        - Default: https://www.maxpreps.com/{state}/{sport}/scores/
        - With gender: https://www.maxpreps.com/{state}/{sport}/{gender}/scores/

    Examples:
        build_scores_url('ca', '11/6/2025', 'basketball', 'girls')  # Girls basketball
        build_scores_url('ca', '11/6/2025', 'volleyball', 'boys')   # Boys volleyball
        build_scores_url('ca', '11/6/2025', 'football')             # Default (boys)
    """
    if gender:  # gender would be "boys" or "girls"
        url_path = f"{state_code}/{sport.lower()}/{gender}/scores/"
    else:
        url_path = f"{state_code}/{sport.lower()}/scores/"

    return f"https://www.maxpreps.com/{url_path}?date={httpx.QueryParams({'date': mdy})}"


# Helper function to parse compound sport names for URL building
def parse_compound_sport(sport: str) -> tuple[str, str]:
    """Parse compound sport names into base sport and gender for URL building

    Only returns gender if that specific sport+gender combination requires
    gender in the MaxPreps URL path.

    Args:
        sport: Sport name (e.g., 'basketball-girls', 'volleyball-boys', 'football')

    Returns:
        Tuple of (base_sport, gender) where gender is 'boys'/'girls' or None

    Examples:
        'basketball-girls' -> ('basketball', 'girls')  # Requires gender in URL
        'basketball-boys' -> ('basketball', None)      # Does not require gender in URL
        'volleyball-boys' -> ('volleyball', 'boys')   # Requires gender in URL
        'volleyball-girls' -> ('volleyball', None)    # Does not require gender in URL
        'football' -> ('football', None)
    """
    sport_lower = sport.lower()

    if sport_lower.endswith('-girls'):
        base_sport = sport_lower[:-6]  # Remove '-girls'
        # Only return gender if this sport+gender combination requires it in URL
        if (base_sport, 'girls') in GENDER_REQUIRED_SPORTS:
            return base_sport, 'girls'
        else:
            return base_sport, None
    elif sport_lower.endswith('-boys'):
        base_sport = sport_lower[:-5]  # Remove '-boys'
        # Only return gender if this sport+gender combination requires it in URL
        if (base_sport, 'boys') in GENDER_REQUIRED_SPORTS:
            return base_sport, 'boys'
        else:
            return base_sport, None
    else:
        return sport_lower, None


# Convenience function to build URL from compound sport names
def build_scores_url_from_sport(state_code: str, mdy: str, sport: str) -> str:
    """Build MaxPreps URL from compound sport name (e.g., 'basketball-girls')

    This function parses compound sport names and calls build_scores_url with
    the appropriate base sport and gender parameters.
    """
    base_sport, gender = parse_compound_sport(sport)
    return build_scores_url(state_code, mdy, base_sport, gender)


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
