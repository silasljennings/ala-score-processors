from datetime import datetime
import pytz

# New York timezone for consistent date/time handling
NY_TZ = pytz.timezone("America/New_York")


# Get current datetime in New York timezone
def now_in_ny() -> datetime:
    """Get current datetime in New York timezone"""
    return datetime.now(NY_TZ)


# Format current date as MM/DD/YYYY string in New York timezone
def today_mdy_ny() -> str:
    """Get today's date in M/D/YYYY format in New York timezone"""
    d = now_in_ny()
    return f"{d.month}/{d.day}/{d.year}"


# Check if current time is within scraping window (Thu-Sat, 6PM-11PM NY time)
def within_run_window_ny() -> bool:
    """Check if current time is within allowed scraping window (Thu-Sat 6PM-11PM NY)"""
    d = now_in_ny()
    dow = d.weekday()  # 0=Mon, 3=Thu
    hr = d.hour
    return (dow in [3, 4, 5]) and 18 <= hr <= 23