from datetime import datetime, date
from typing import List, Dict
import pytz


# Seasonal sports configuration based on typical US high school sports seasons
SEASONAL_SPORTS = {
    "fall": {
        "months": [8, 9, 10, 11],  # August - November
        "sports": ["football", "volleyball"],
        "description": "Fall season - Football and Volleyball"
    },
    "late_fall": {
        "months": [11, 12],  # November - December
        "sports": ["football", "volleyball", "basketball"],
        "description": "Late Fall season - Football, Volleyball, and Basketball"
    },
    "winter": {
        "months": [12, 1, 2],  # December - February
        "sports": ["basketball"],
        "description": "Winter season - Basketball"
    },
    "late_winter": {
        "months": [2, 3],  # February - March
        "sports": ["basketball", "baseball", "soccer", "softball"],
        "description": "Late Winter season - Basketball, Baseball, Soccer, and Softball"
    },
    "spring": {
        "months": [3, 4, 5, 6],  # March - June
        "sports": ["baseball", "softball", "soccer"],
        "description": "Spring season - Baseball, Softball, and Soccer"
    }
}


# Sports that we currently have scheduling implemented for
IMPLEMENTED_SPORTS = ["football", "volleyball"]


# Get current season based on date
def get_current_season(current_date: date = None) -> str:
    """Determine current season based on date (defaults to today)"""
    if not current_date:
        # Use Eastern Time to determine season (most common timezone for US high school sports)
        et_tz = pytz.timezone("America/New_York")
        current_date = datetime.now(et_tz).date()
    
    current_month = current_date.month
    
    # Check each season to see if current month falls within it
    for season, config in SEASONAL_SPORTS.items():
        if current_month in config["months"]:
            return season
    
    # Default fallback (shouldn't happen with proper month coverage)
    return "fall"


# Get sports for a specific season
def get_sports_for_season(season: str) -> List[str]:
    """Get list of sports for a specific season"""
    if season not in SEASONAL_SPORTS:
        raise ValueError(f"Unknown season: {season}. Available: {list(SEASONAL_SPORTS.keys())}")
    
    return SEASONAL_SPORTS[season]["sports"]


# Get implemented sports for a specific season (only sports we have schedules for)
def get_implemented_sports_for_season(season: str) -> List[str]:
    """Get list of implemented sports for a specific season"""
    season_sports = get_sports_for_season(season)
    return [sport for sport in season_sports if sport in IMPLEMENTED_SPORTS]


# Get current season's implemented sports
def get_current_season_sports() -> List[str]:
    """Get implemented sports for the current season"""
    current_season = get_current_season()
    return get_implemented_sports_for_season(current_season)


# Get season information
def get_season_info(season: str = None) -> Dict:
    """Get detailed information about a season"""
    if not season:
        season = get_current_season()
    
    if season not in SEASONAL_SPORTS:
        raise ValueError(f"Unknown season: {season}")
    
    config = SEASONAL_SPORTS[season]
    implemented_sports = get_implemented_sports_for_season(season)
    unimplemented_sports = [sport for sport in config["sports"] if sport not in IMPLEMENTED_SPORTS]
    
    return {
        "season": season,
        "description": config["description"],
        "months": config["months"],
        "all_sports": config["sports"],
        "implemented_sports": implemented_sports,
        "unimplemented_sports": unimplemented_sports,
        "has_schedules": len(implemented_sports) > 0
    }


# Get all available seasons
def get_available_seasons() -> List[str]:
    """Get list of all available seasons"""
    return list(SEASONAL_SPORTS.keys())


# Get season schedule summary
def get_seasonal_schedule_summary() -> Dict:
    """Get summary of all seasonal configurations"""
    summary = {}
    
    for season in SEASONAL_SPORTS.keys():
        info = get_season_info(season)
        summary[season] = {
            "description": info["description"],
            "months": info["months"],
            "implemented_sports": info["implemented_sports"],
            "total_sports": len(info["all_sports"]),
            "implemented_count": len(info["implemented_sports"])
        }
    
    return summary


# Check if a specific sport is active in current season
def is_sport_in_season(sport: str, season: str = None) -> bool:
    """Check if a sport is active in the specified season (defaults to current)"""
    if not season:
        season = get_current_season()
    
    season_sports = get_sports_for_season(season)
    return sport.lower() in [s.lower() for s in season_sports]


# Get months when a sport is active
def get_sport_active_months(sport: str) -> List[int]:
    """Get list of months when a sport is typically active"""
    active_months = set()
    
    for season, config in SEASONAL_SPORTS.items():
        if sport.lower() in [s.lower() for s in config["sports"]]:
            active_months.update(config["months"])
    
    return sorted(list(active_months))