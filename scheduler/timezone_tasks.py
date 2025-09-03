from scheduler.tasks import scheduled_scrape_with_config, scheduled_finalize_with_config
from config.timezone_schedules import TIMEZONE_MAPPINGS, get_states_for_timezone


# Manual timezone scraping function (for CLI/API use)
async def manual_timezone_scrape(timezone_name: str, sport: str = "football"):
    """Manually execute scraping for a specific timezone and sport"""
    states = get_states_for_timezone(timezone_name)
    if not states:
        raise ValueError(f"Unknown timezone: {timezone_name}")
    
    return await scheduled_scrape_with_config(
        states=states,
        sport=sport, 
        force=True
    )


# Manual timezone finalization function (for CLI/API use)
async def manual_timezone_finalize(timezone_name: str, sport: str = "football"):
    """Manually execute finalization for a specific timezone and sport"""
    states = get_states_for_timezone(timezone_name)
    if not states:
        raise ValueError(f"Unknown timezone: {timezone_name}")
        
    return await scheduled_finalize_with_config(
        states=states,
        sport=sport
    )


# Get all available timezone names
def get_available_timezones():
    """Get list of all available timezone names"""
    return list(TIMEZONE_MAPPINGS.keys())