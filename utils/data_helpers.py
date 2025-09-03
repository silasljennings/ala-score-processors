import re


# Remove ranking numbers from team names (e.g., "(#5)" or "(5)")
def clean_team_name(raw: str = "") -> str:
    """Remove ranking numbers in parentheses from team names"""
    return re.sub(r"\(\s*#?\d+\s*\)\s*", "", raw).strip()


# Convert date string to M/D/YYYY format
def to_mdy(input_str: str | None) -> str | None:
    """Convert date string to M/D/YYYY format from various input formats"""
    if not input_str:
        return None
    
    # Handle M/D/YYYY format
    mdy = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", input_str)
    if mdy:
        return f"{int(mdy[1])}/{int(mdy[2])}/{mdy[3]}"
    
    # Handle YYYY-MM-DD or YYYY/MM/DD format
    iso = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", input_str)
    if iso:
        return f"{int(iso[2])}/{int(iso[3])}/{iso[1]}"
    
    return None