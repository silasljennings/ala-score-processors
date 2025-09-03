import pytz
from datetime import datetime
from typing import Dict, List


# US Time zone definitions and state mappings
TIMEZONE_MAPPINGS = {
    "eastern": {
        "timezone": "America/New_York",
        "states": ["ct", "de", "dc", "fl", "ga", "me", "md", "ma", "nh", "nj", "ny", "nc", "oh", "pa", "ri", "sc", "vt", "va", "wv"]
    },
    "central": {
        "timezone": "America/Chicago", 
        "states": ["al", "ar", "fl", "ia", "il", "in", "ky", "la", "mi", "mn", "ms", "mo", "tn", "tx", "wi"]
    },
    "mountain": {
        "timezone": "America/Denver",
        "states": ["az", "co", "id", "ks", "mt", "ne", "nm", "nd", "ok", "sd", "ut", "wy"]
    },
    "pacific": {
        "timezone": "America/Los_Angeles",
        "states": ["ca", "nv", "or", "wa"]
    },
    "alaska": {
        "timezone": "America/Anchorage",
        "states": ["ak"]
    },
    "hawaii": {
        "timezone": "Pacific/Honolulu",
        "states": ["hi"]
    }
}


# Football game time windows (5PM - 11:30PM local time for each timezone)
# Converted to UTC schedules based on timezone offsets
FOOTBALL_SCRAPE_SCHEDULES = {
    # Eastern Time (UTC-5 EST, UTC-4 EDT)
    # 5PM-11:30PM ET = 21:00-03:30 UTC (EST) or 21:00-03:30 UTC (EDT)
    "eastern": [
        {
            "name": "football_scrape_eastern_1",
            "cron": "*/3 21-23 * * 3,4,5",  # Every 3 min, 9PM-11PM UTC Thu,Fri,Sat
            "description": "Eastern timezone scraping 5PM-7PM local"
        },
        {
            "name": "football_scrape_eastern_2", 
            "cron": "0-30/3 0-3 * * 4,5,6",  # Every 3 min 0-30 past hour, midnight-3AM UTC Fri,Sat,Sun
            "description": "Eastern timezone scraping 7PM-11:30PM local (next day UTC)"
        }
    ],
    
    # Central Time (UTC-6 CST, UTC-5 CDT)
    # 5PM-11:30PM CT = 22:00-04:30 UTC (CST) or 21:00-03:30 UTC (CDT)
    "central": [
        {
            "name": "football_scrape_central_1",
            "cron": "*/3 22-23 * * 3,4,5",  # Every 3 min, 10PM-11PM UTC Thu,Fri,Sat
            "description": "Central timezone scraping 5PM-6PM local"
        },
        {
            "name": "football_scrape_central_2",
            "cron": "0-30/3 0-4 * * 4,5,6",  # Every 3 min 0-30 past hour, midnight-4AM UTC Fri,Sat,Sun
            "description": "Central timezone scraping 6PM-11:30PM local (next day UTC)"
        }
    ],
    
    # Mountain Time (UTC-7 MST, UTC-6 MDT)
    # 5PM-11:30PM MT = 23:00-05:30 UTC (MST) or 22:00-04:30 UTC (MDT)
    "mountain": [
        {
            "name": "football_scrape_mountain_1",
            "cron": "*/3 23 * * 3,4,5",  # Every 3 min, 11PM UTC Thu,Fri,Sat
            "description": "Mountain timezone scraping 5PM local"
        },
        {
            "name": "football_scrape_mountain_2",
            "cron": "0-30/3 0-5 * * 4,5,6",  # Every 3 min 0-30 past hour, midnight-5AM UTC Fri,Sat,Sun
            "description": "Mountain timezone scraping 6PM-11:30PM local (next day UTC)"
        }
    ],
    
    # Pacific Time (UTC-8 PST, UTC-7 PDT)
    # 5PM-11:30PM PT = 0:00-6:30 UTC next day (PST) or 23:00-05:30 UTC (PDT)
    "pacific": [
        {
            "name": "football_scrape_pacific_1",
            "cron": "0-30/3 0-6 * * 4,5,6",  # Every 3 min 0-30 past hour, midnight-6AM UTC Fri,Sat,Sun
            "description": "Pacific timezone scraping 5PM-11:30PM local (next day UTC)"
        }
    ],
    
    # Alaska Time (UTC-9 AKST, UTC-8 AKDT)
    # 5PM-11:30PM AKT = 1:00-7:30 UTC next day (AKST) or 0:00-6:30 UTC (AKDT) 
    "alaska": [
        {
            "name": "football_scrape_alaska_1",
            "cron": "0-30/3 1-7 * * 4,5,6",  # Every 3 min 0-30 past hour, 1AM-7AM UTC Fri,Sat,Sun
            "description": "Alaska timezone scraping 5PM-11:30PM local (next day UTC)"
        }
    ],
    
    # Hawaii Time (UTC-10 HST - no daylight saving)
    # 5PM-11:30PM HT = 3:00-9:30 UTC next day
    "hawaii": [
        {
            "name": "football_scrape_hawaii_1", 
            "cron": "0-30/3 3-9 * * 4,5,6",  # Every 3 min 0-30 past hour, 3AM-9AM UTC Fri,Sat,Sun
            "description": "Hawaii timezone scraping 5PM-11:30PM local (next day UTC)"
        }
    ]
}


# Volleyball game time windows (3PM - 11PM local time daily)
# Converted to UTC schedules based on timezone offsets
VOLLEYBALL_SCRAPE_SCHEDULES = {
    # Eastern Time (UTC-5 EST, UTC-4 EDT)
    # 3PM-11PM ET = 19:00-03:00 UTC (EST) or 19:00-03:00 UTC (EDT)
    "eastern": [
        {
            "name": "volleyball_scrape_eastern_1",
            "cron": "*/15 19-23 * * *",  # Every 15 min, 7PM-11PM UTC daily
            "description": "Eastern timezone volleyball scraping 3PM-7PM local"
        },
        {
            "name": "volleyball_scrape_eastern_2", 
            "cron": "*/15 0-3 * * *",  # Every 15 min, midnight-3AM UTC daily
            "description": "Eastern timezone volleyball scraping 8PM-11PM local (next day UTC)"
        }
    ],
    
    # Central Time (UTC-6 CST, UTC-5 CDT)
    # 3PM-11PM CT = 20:00-04:00 UTC (CST) or 20:00-04:00 UTC (CDT)
    "central": [
        {
            "name": "volleyball_scrape_central_1",
            "cron": "*/15 20-23 * * *",  # Every 15 min, 8PM-11PM UTC daily
            "description": "Central timezone volleyball scraping 3PM-6PM local"
        },
        {
            "name": "volleyball_scrape_central_2",
            "cron": "*/15 0-4 * * *",  # Every 15 min, midnight-4AM UTC daily
            "description": "Central timezone volleyball scraping 7PM-11PM local (next day UTC)"
        }
    ],
    
    # Mountain Time (UTC-7 MST, UTC-6 MDT)
    # 3PM-11PM MT = 21:00-05:00 UTC (MST) or 21:00-05:00 UTC (MDT)
    "mountain": [
        {
            "name": "volleyball_scrape_mountain_1",
            "cron": "*/15 21-23 * * *",  # Every 15 min, 9PM-11PM UTC daily
            "description": "Mountain timezone volleyball scraping 3PM-5PM local"
        },
        {
            "name": "volleyball_scrape_mountain_2",
            "cron": "*/15 0-5 * * *",  # Every 15 min, midnight-5AM UTC daily
            "description": "Mountain timezone volleyball scraping 6PM-11PM local (next day UTC)"
        }
    ],
    
    # Pacific Time (UTC-8 PST, UTC-7 PDT)
    # 3PM-11PM PT = 22:00-06:00 UTC next day (PST) or 22:00-06:00 UTC (PDT)
    "pacific": [
        {
            "name": "volleyball_scrape_pacific_1",
            "cron": "*/15 22-23 * * *",  # Every 15 min, 10PM-11PM UTC daily
            "description": "Pacific timezone volleyball scraping 3PM-4PM local"
        },
        {
            "name": "volleyball_scrape_pacific_2",
            "cron": "*/15 0-6 * * *",  # Every 15 min, midnight-6AM UTC daily
            "description": "Pacific timezone volleyball scraping 5PM-11PM local (next day UTC)"
        }
    ],
    
    # Alaska Time (UTC-9 AKST, UTC-8 AKDT)
    # 3PM-11PM AKT = 23:00-07:00 UTC next day (AKST) or 23:00-07:00 UTC (AKDT) 
    "alaska": [
        {
            "name": "volleyball_scrape_alaska_1",
            "cron": "*/15 23 * * *",  # Every 15 min, 11PM UTC daily
            "description": "Alaska timezone volleyball scraping 3PM local"
        },
        {
            "name": "volleyball_scrape_alaska_2",
            "cron": "*/15 0-7 * * *",  # Every 15 min, midnight-7AM UTC daily
            "description": "Alaska timezone volleyball scraping 4PM-11PM local (next day UTC)"
        }
    ],
    
    # Hawaii Time (UTC-10 HST - no daylight saving)
    # 3PM-11PM HT = 1:00-9:00 UTC next day
    "hawaii": [
        {
            "name": "volleyball_scrape_hawaii_1", 
            "cron": "*/15 1-9 * * *",  # Every 15 min, 1AM-9AM UTC daily
            "description": "Hawaii timezone volleyball scraping 3PM-11PM local (next day UTC)"
        }
    ]
}


# Football finalization schedules (12:30AM local time after game days)
# Runs Friday, Saturday, Sunday mornings (after Thu, Fri, Sat games)
FOOTBALL_FINALIZE_SCHEDULES = {
    # Eastern: 12:30AM ET = 4:30AM UTC (EST) or 4:30AM UTC (EDT)
    "eastern": {
        "name": "football_finalize_eastern",
        "cron": "30 4 * * 5,6,0",  # 4:30AM UTC on Fri,Sat,Sun
        "description": "Eastern timezone finalization 12:30AM local after games"
    },
    
    # Central: 12:30AM CT = 5:30AM UTC (CST) or 5:30AM UTC (CDT) 
    "central": {
        "name": "football_finalize_central",
        "cron": "30 5 * * 5,6,0",  # 5:30AM UTC on Fri,Sat,Sun
        "description": "Central timezone finalization 12:30AM local after games"
    },
    
    # Mountain: 12:30AM MT = 6:30AM UTC (MST) or 6:30AM UTC (MDT)
    "mountain": {
        "name": "football_finalize_mountain", 
        "cron": "30 6 * * 5,6,0",  # 6:30AM UTC on Fri,Sat,Sun
        "description": "Mountain timezone finalization 12:30AM local after games"
    },
    
    # Pacific: 12:30AM PT = 7:30AM UTC (PST) or 7:30AM UTC (PDT)
    "pacific": {
        "name": "football_finalize_pacific",
        "cron": "30 7 * * 5,6,0",  # 7:30AM UTC on Fri,Sat,Sun
        "description": "Pacific timezone finalization 12:30AM local after games"
    },
    
    # Alaska: 12:30AM AKT = 8:30AM UTC (AKST) or 8:30AM UTC (AKDT)
    "alaska": {
        "name": "football_finalize_alaska",
        "cron": "30 8 * * 5,6,0",  # 8:30AM UTC on Fri,Sat,Sun
        "description": "Alaska timezone finalization 12:30AM local after games"
    },
    
    # Hawaii: 12:30AM HT = 10:30AM UTC (HST - no DST)
    "hawaii": {
        "name": "football_finalize_hawaii",
        "cron": "30 10 * * 5,6,0",  # 10:30AM UTC on Fri,Sat,Sun
        "description": "Hawaii timezone finalization 12:30AM local after games"
    }
}


# Volleyball finalization schedules (10:30PM local time daily)
# Note: Runs every day as volleyball season can have games most days
VOLLEYBALL_FINALIZE_SCHEDULES = {
    # Eastern: 10:30PM ET = 3:30AM UTC next day (EST) or 2:30AM UTC next day (EDT)
    # Using 3:30AM UTC to be consistent with standard time
    "eastern": {
        "name": "volleyball_finalize_eastern",
        "cron": "30 3 * * 0,1,2,3,4,5,6",  # 3:30AM UTC daily (10:30PM ET previous day)
        "description": "Eastern timezone volleyball finalization 10:30PM local"
    },
    
    # Central: 10:30PM CT = 3:30AM UTC next day (CST) or 3:30AM UTC next day (CDT)
    "central": {
        "name": "volleyball_finalize_central", 
        "cron": "30 3 * * 0,1,2,3,4,5,6",  # 3:30AM UTC daily (10:30PM CT previous day)
        "description": "Central timezone volleyball finalization 10:30PM local"
    },
    
    # Mountain: 10:30PM MT = 4:30AM UTC next day (MST) or 4:30AM UTC next day (MDT)
    "mountain": {
        "name": "volleyball_finalize_mountain",
        "cron": "30 4 * * 0,1,2,3,4,5,6",  # 4:30AM UTC daily (10:30PM MT previous day)
        "description": "Mountain timezone volleyball finalization 10:30PM local"
    },
    
    # Pacific: 10:30PM PT = 5:30AM UTC next day (PST) or 5:30AM UTC next day (PDT)
    "pacific": {
        "name": "volleyball_finalize_pacific",
        "cron": "30 5 * * 0,1,2,3,4,5,6",  # 5:30AM UTC daily (10:30PM PT previous day)
        "description": "Pacific timezone volleyball finalization 10:30PM local"
    },
    
    # Alaska: 10:30PM AKT = 6:30AM UTC next day (AKST) or 6:30AM UTC next day (AKDT)
    "alaska": {
        "name": "volleyball_finalize_alaska",
        "cron": "30 6 * * 0,1,2,3,4,5,6",  # 6:30AM UTC daily (10:30PM AKT previous day)
        "description": "Alaska timezone volleyball finalization 10:30PM local"
    },
    
    # Hawaii: 10:30PM HT = 8:30AM UTC next day (HST - no DST)
    "hawaii": {
        "name": "volleyball_finalize_hawaii",
        "cron": "30 8 * * 0,1,2,3,4,5,6",  # 8:30AM UTC daily (10:30PM HT previous day)
        "description": "Hawaii timezone volleyball finalization 10:30PM local"
    }
}


# Get all states for a given timezone
def get_states_for_timezone(timezone_name: str) -> List[str]:
    """Get list of states for a given timezone"""
    return TIMEZONE_MAPPINGS.get(timezone_name, {}).get("states", [])


# Get timezone object for a timezone name
def get_timezone(timezone_name: str) -> pytz.BaseTzInfo:
    """Get pytz timezone object for a timezone name"""
    tz_info = TIMEZONE_MAPPINGS.get(timezone_name, {})
    return pytz.timezone(tz_info.get("timezone", "UTC"))


# Check if daylight saving time is currently active for a timezone
def is_daylight_saving(timezone_name: str) -> bool:
    """Check if daylight saving time is currently active for a timezone"""
    if timezone_name == "hawaii":  # Hawaii doesn't observe DST
        return False
    
    tz = get_timezone(timezone_name)
    now = datetime.now(tz)
    return bool(now.dst())


# Get current UTC offset for a timezone (accounting for DST)
def get_utc_offset(timezone_name: str) -> int:
    """Get current UTC offset in hours for a timezone (negative for behind UTC)"""
    tz = get_timezone(timezone_name)
    now = datetime.now(tz)
    offset_seconds = now.utcoffset().total_seconds()
    return int(offset_seconds / 3600)