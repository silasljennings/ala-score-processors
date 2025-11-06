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


# Volleyball Girls game time windows (3PM - 11PM local time daily)
# Converted to UTC schedules based on timezone offsets
VOLLEYBALL_GIRLS_SCRAPE_SCHEDULES = {
    # Eastern Time (UTC-5 EST, UTC-4 EDT)
    # 3PM-11PM ET = 19:00-03:00 UTC (EST) or 19:00-03:00 UTC (EDT)
    "eastern": [
        {
            "name": "volleyball_girls_scrape_eastern_1",
            "cron": "*/15 19-23 * * *",  # Every 15 min, 7PM-11PM UTC daily
            "description": "Eastern timezone volleyball girls scraping 3PM-7PM local"
        },
        {
            "name": "volleyball_girls_scrape_eastern_2", 
            "cron": "*/15 0-3 * * *",  # Every 15 min, midnight-3AM UTC daily
            "description": "Eastern timezone volleyball girls scraping 8PM-11PM local (next day UTC)"
        }
    ],
    
    # Central Time (UTC-6 CST, UTC-5 CDT)
    # 3PM-11PM CT = 20:00-04:00 UTC (CST) or 20:00-04:00 UTC (CDT)
    "central": [
        {
            "name": "volleyball_girls_scrape_central_1",
            "cron": "*/15 20-23 * * *",  # Every 15 min, 8PM-11PM UTC daily
            "description": "Central timezone volleyball girls scraping 3PM-6PM local"
        },
        {
            "name": "volleyball_girls_scrape_central_2",
            "cron": "*/15 0-4 * * *",  # Every 15 min, midnight-4AM UTC daily
            "description": "Central timezone volleyball girls scraping 7PM-11PM local (next day UTC)"
        }
    ],
    
    # Mountain Time (UTC-7 MST, UTC-6 MDT)
    # 3PM-11PM MT = 21:00-05:00 UTC (MST) or 21:00-05:00 UTC (MDT)
    "mountain": [
        {
            "name": "volleyball_girls_scrape_mountain_1",
            "cron": "*/15 21-23 * * *",  # Every 15 min, 9PM-11PM UTC daily
            "description": "Mountain timezone volleyball girls scraping 3PM-5PM local"
        },
        {
            "name": "volleyball_girls_scrape_mountain_2",
            "cron": "*/15 0-5 * * *",  # Every 15 min, midnight-5AM UTC daily
            "description": "Mountain timezone volleyball girls scraping 6PM-11PM local (next day UTC)"
        }
    ],
    
    # Pacific Time (UTC-8 PST, UTC-7 PDT)
    # 3PM-11PM PT = 22:00-06:00 UTC next day (PST) or 22:00-06:00 UTC (PDT)
    "pacific": [
        {
            "name": "volleyball_girls_scrape_pacific_1",
            "cron": "*/15 22-23 * * *",  # Every 15 min, 10PM-11PM UTC daily
            "description": "Pacific timezone volleyball girls scraping 3PM-4PM local"
        },
        {
            "name": "volleyball_girls_scrape_pacific_2",
            "cron": "*/15 0-6 * * *",  # Every 15 min, midnight-6AM UTC daily
            "description": "Pacific timezone volleyball girls scraping 5PM-11PM local (next day UTC)"
        }
    ],
    
    # Alaska Time (UTC-9 AKST, UTC-8 AKDT)
    # 3PM-11PM AKT = 23:00-07:00 UTC next day (AKST) or 23:00-07:00 UTC (AKDT) 
    "alaska": [
        {
            "name": "volleyball_girls_scrape_alaska_1",
            "cron": "*/15 23 * * *",  # Every 15 min, 11PM UTC daily
            "description": "Alaska timezone volleyball girls scraping 3PM local"
        },
        {
            "name": "volleyball_girls_scrape_alaska_2",
            "cron": "*/15 0-7 * * *",  # Every 15 min, midnight-7AM UTC daily
            "description": "Alaska timezone volleyball girls scraping 4PM-11PM local (next day UTC)"
        }
    ],
    
    # Hawaii Time (UTC-10 HST - no daylight saving)
    # 3PM-11PM HT = 1:00-9:00 UTC next day
    "hawaii": [
        {
            "name": "volleyball_girls_scrape_hawaii_1", 
            "cron": "*/15 1-9 * * *",  # Every 15 min, 1AM-9AM UTC daily
            "description": "Hawaii timezone volleyball girls scraping 3PM-11PM local (next day UTC)"
        }
    ]
}


# Volleyball Boys game time windows (3PM - 11PM local time daily)
# Converted to UTC schedules based on timezone offsets
VOLLEYBALL_BOYS_SCRAPE_SCHEDULES = {
    # Eastern Time (UTC-5 EST, UTC-4 EDT)
    # 3PM-11PM ET = 19:00-03:00 UTC (EST) or 19:00-03:00 UTC (EDT)
    "eastern": [
        {
            "name": "volleyball_boys_scrape_eastern_1",
            "cron": "*/15 19-23 * * *",  # Every 15 min, 7PM-11PM UTC daily
            "description": "Eastern timezone volleyball boys scraping 3PM-7PM local"
        },
        {
            "name": "volleyball_boys_scrape_eastern_2",
            "cron": "*/15 0-3 * * *",  # Every 15 min, midnight-3AM UTC daily
            "description": "Eastern timezone volleyball boys scraping 8PM-11PM local (next day UTC)"
        }
    ],

    # Central Time (UTC-6 CST, UTC-5 CDT)
    # 3PM-11PM CT = 20:00-04:00 UTC (CST) or 20:00-04:00 UTC (CDT)
    "central": [
        {
            "name": "volleyball_boys_scrape_central_1",
            "cron": "*/15 20-23 * * *",  # Every 15 min, 8PM-11PM UTC daily
            "description": "Central timezone volleyball boys scraping 3PM-6PM local"
        },
        {
            "name": "volleyball_boys_scrape_central_2",
            "cron": "*/15 0-4 * * *",  # Every 15 min, midnight-4AM UTC daily
            "description": "Central timezone volleyball boys scraping 7PM-11PM local (next day UTC)"
        }
    ],

    # Mountain Time (UTC-7 MST, UTC-6 MDT)
    # 3PM-11PM MT = 21:00-05:00 UTC (MST) or 21:00-05:00 UTC (MDT)
    "mountain": [
        {
            "name": "volleyball_boys_scrape_mountain_1",
            "cron": "*/15 21-23 * * *",  # Every 15 min, 9PM-11PM UTC daily
            "description": "Mountain timezone volleyball boys scraping 3PM-5PM local"
        },
        {
            "name": "volleyball_boys_scrape_mountain_2",
            "cron": "*/15 0-5 * * *",  # Every 15 min, midnight-5AM UTC daily
            "description": "Mountain timezone volleyball boys scraping 6PM-11PM local (next day UTC)"
        }
    ],

    # Pacific Time (UTC-8 PST, UTC-7 PDT)
    # 3PM-11PM PT = 22:00-06:00 UTC next day (PST) or 22:00-06:00 UTC (PDT)
    "pacific": [
        {
            "name": "volleyball_boys_scrape_pacific_1",
            "cron": "*/15 22-23 * * *",  # Every 15 min, 10PM-11PM UTC daily
            "description": "Pacific timezone volleyball boys scraping 3PM-4PM local"
        },
        {
            "name": "volleyball_boys_scrape_pacific_2",
            "cron": "*/15 0-6 * * *",  # Every 15 min, midnight-6AM UTC daily
            "description": "Pacific timezone volleyball boys scraping 5PM-11PM local (next day UTC)"
        }
    ],

    # Alaska Time (UTC-9 AKST, UTC-8 AKDT)
    # 3PM-11PM AKT = 23:00-07:00 UTC next day (AKST) or 23:00-07:00 UTC (AKDT)
    "alaska": [
        {
            "name": "volleyball_boys_scrape_alaska_1",
            "cron": "*/15 23 * * *",  # Every 15 min, 11PM UTC daily
            "description": "Alaska timezone volleyball boys scraping 3PM local"
        },
        {
            "name": "volleyball_boys_scrape_alaska_2",
            "cron": "*/15 0-7 * * *",  # Every 15 min, midnight-7AM UTC daily
            "description": "Alaska timezone volleyball boys scraping 4PM-11PM local (next day UTC)"
        }
    ],

    # Hawaii Time (UTC-10 HST - no daylight saving)
    # 3PM-11PM HT = 1:00-9:00 UTC next day
    "hawaii": [
        {
            "name": "volleyball_boys_scrape_hawaii_1",
            "cron": "*/15 1-9 * * *",  # Every 15 min, 1AM-9AM UTC daily
            "description": "Hawaii timezone volleyball boys scraping 3PM-11PM local (next day UTC)"
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


# Volleyball Girls finalization schedules (10:30PM local time daily)
# Note: Runs every day as volleyball season can have games most days
VOLLEYBALL_GIRLS_FINALIZE_SCHEDULES = {
    # Eastern: 10:30PM ET = 3:30AM UTC next day (EST) or 2:30AM UTC next day (EDT)
    # Using 3:30AM UTC to be consistent with standard time
    "eastern": {
        "name": "volleyball_girls_finalize_eastern",
        "cron": "30 3 * * 0,1,2,3,4,5,6",  # 3:30AM UTC daily (10:30PM ET previous day)
        "description": "Eastern timezone volleyball girls finalization 10:30PM local"
    },
    
    # Central: 10:30PM CT = 3:30AM UTC next day (CST) or 3:30AM UTC next day (CDT)
    "central": {
        "name": "volleyball_girls_finalize_central", 
        "cron": "30 3 * * 0,1,2,3,4,5,6",  # 3:30AM UTC daily (10:30PM CT previous day)
        "description": "Central timezone volleyball girls finalization 10:30PM local"
    },
    
    # Mountain: 10:30PM MT = 4:30AM UTC next day (MST) or 4:30AM UTC next day (MDT)
    "mountain": {
        "name": "volleyball_girls_finalize_mountain",
        "cron": "30 4 * * 0,1,2,3,4,5,6",  # 4:30AM UTC daily (10:30PM MT previous day)
        "description": "Mountain timezone volleyball girls finalization 10:30PM local"
    },
    
    # Pacific: 10:30PM PT = 5:30AM UTC next day (PST) or 5:30AM UTC next day (PDT)
    "pacific": {
        "name": "volleyball_girls_finalize_pacific",
        "cron": "30 5 * * 0,1,2,3,4,5,6",  # 5:30AM UTC daily (10:30PM PT previous day)
        "description": "Pacific timezone volleyball girls finalization 10:30PM local"
    },
    
    # Alaska: 10:30PM AKT = 6:30AM UTC next day (AKST) or 6:30AM UTC next day (AKDT)
    "alaska": {
        "name": "volleyball_girls_finalize_alaska",
        "cron": "30 6 * * 0,1,2,3,4,5,6",  # 6:30AM UTC daily (10:30PM AKT previous day)
        "description": "Alaska timezone volleyball girls finalization 10:30PM local"
    },
    
    # Hawaii: 10:30PM HT = 8:30AM UTC next day (HST - no DST)
    "hawaii": {
        "name": "volleyball_girls_finalize_hawaii",
        "cron": "30 8 * * 0,1,2,3,4,5,6",  # 8:30AM UTC daily (10:30PM HT previous day)
        "description": "Hawaii timezone volleyball girls finalization 10:30PM local"
    }
}


# Volleyball Boys finalization schedules (10:30PM local time daily)
# Note: Runs every day as volleyball season can have games most days
VOLLEYBALL_BOYS_FINALIZE_SCHEDULES = {
    # Eastern: 10:30PM ET = 3:30AM UTC next day (EST) or 2:30AM UTC next day (EDT)
    # Using 3:30AM UTC to be consistent with standard time
    "eastern": {
        "name": "volleyball_boys_finalize_eastern",
        "cron": "30 3 * * 0,1,2,3,4,5,6",  # 3:30AM UTC daily (10:30PM ET previous day)
        "description": "Eastern timezone volleyball boys finalization 10:30PM local"
    },

    # Central: 10:30PM CT = 3:30AM UTC next day (CST) or 3:30AM UTC next day (CDT)
    "central": {
        "name": "volleyball_boys_finalize_central",
        "cron": "30 3 * * 0,1,2,3,4,5,6",  # 3:30AM UTC daily (10:30PM CT previous day)
        "description": "Central timezone volleyball boys finalization 10:30PM local"
    },

    # Mountain: 10:30PM MT = 4:30AM UTC next day (MST) or 4:30AM UTC next day (MDT)
    "mountain": {
        "name": "volleyball_boys_finalize_mountain",
        "cron": "30 4 * * 0,1,2,3,4,5,6",  # 4:30AM UTC daily (10:30PM MT previous day)
        "description": "Mountain timezone volleyball boys finalization 10:30PM local"
    },

    # Pacific: 10:30PM PT = 5:30AM UTC next day (PST) or 5:30AM UTC next day (PDT)
    "pacific": {
        "name": "volleyball_boys_finalize_pacific",
        "cron": "30 5 * * 0,1,2,3,4,5,6",  # 5:30AM UTC daily (10:30PM PT previous day)
        "description": "Pacific timezone volleyball boys finalization 10:30PM local"
    },

    # Alaska: 10:30PM AKT = 6:30AM UTC next day (AKST) or 6:30AM UTC next day (AKDT)
    "alaska": {
        "name": "volleyball_boys_finalize_alaska",
        "cron": "30 6 * * 0,1,2,3,4,5,6",  # 6:30AM UTC daily (10:30PM AKT previous day)
        "description": "Alaska timezone volleyball boys finalization 10:30PM local"
    },

    # Hawaii: 10:30PM HT = 8:30AM UTC next day (HST - no DST)
    "hawaii": {
        "name": "volleyball_boys_finalize_hawaii",
        "cron": "30 8 * * 0,1,2,3,4,5,6",  # 8:30AM UTC daily (10:30PM HT previous day)
        "description": "Hawaii timezone volleyball boys finalization 10:30PM local"
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


# Basketball Boys game time windows (6PM - 9PM local time on Tue, Thu, Fri, Sat)
# Converted to UTC schedules based on timezone offsets
BASKETBALL_BOYS_SCRAPE_SCHEDULES = {
    # Eastern Time (UTC-5 EST, UTC-4 EDT)
    # 6PM-9PM ET = 22:00-01:00 UTC (EST) or 22:00-01:00 UTC (EDT)
    "eastern": [
        {
            "name": "basketball_boys_scrape_eastern_1",
            "cron": "*/10 22-23 * * 1,3,4,5",  # Every 10 min, 10PM-11PM UTC Tue,Thu,Fri,Sat
            "description": "Eastern timezone basketball boys scraping 6PM-7PM local"
        },
        {
            "name": "basketball_boys_scrape_eastern_2",
            "cron": "*/10 0-1 * * 2,4,5,6",  # Every 10 min, midnight-1AM UTC Wed,Fri,Sat,Sun
            "description": "Eastern timezone basketball boys scraping 8PM-9PM local (next day UTC)"
        }
    ],

    # Central Time (UTC-6 CST, UTC-5 CDT)
    # 6PM-9PM CT = 23:00-02:00 UTC (CST) or 23:00-02:00 UTC (CDT)
    "central": [
        {
            "name": "basketball_boys_scrape_central_1",
            "cron": "*/10 23 * * 1,3,4,5",  # Every 10 min, 11PM UTC Tue,Thu,Fri,Sat
            "description": "Central timezone basketball boys scraping 6PM local"
        },
        {
            "name": "basketball_boys_scrape_central_2",
            "cron": "*/10 0-2 * * 2,4,5,6",  # Every 10 min, midnight-2AM UTC Wed,Fri,Sat,Sun
            "description": "Central timezone basketball boys scraping 7PM-9PM local (next day UTC)"
        }
    ],

    # Mountain Time (UTC-7 MST, UTC-6 MDT)
    # 6PM-9PM MT = 0:00-3:00 UTC next day (MST) or 0:00-3:00 UTC next day (MDT)
    "mountain": [
        {
            "name": "basketball_boys_scrape_mountain_1",
            "cron": "*/10 0-3 * * 2,4,5,6",  # Every 10 min, midnight-3AM UTC Wed,Fri,Sat,Sun
            "description": "Mountain timezone basketball boys scraping 6PM-9PM local (next day UTC)"
        }
    ],

    # Pacific Time (UTC-8 PST, UTC-7 PDT)
    # 6PM-9PM PT = 1:00-4:00 UTC next day (PST) or 1:00-4:00 UTC next day (PDT)
    "pacific": [
        {
            "name": "basketball_boys_scrape_pacific_1",
            "cron": "*/10 1-4 * * 2,4,5,6",  # Every 10 min, 1AM-4AM UTC Wed,Fri,Sat,Sun
            "description": "Pacific timezone basketball boys scraping 6PM-9PM local (next day UTC)"
        }
    ],

    # Alaska Time (UTC-9 AKST, UTC-8 AKDT)
    # 6PM-9PM AKT = 2:00-5:00 UTC next day (AKST) or 2:00-5:00 UTC next day (AKDT)
    "alaska": [
        {
            "name": "basketball_boys_scrape_alaska_1",
            "cron": "*/10 2-5 * * 2,4,5,6",  # Every 10 min, 2AM-5AM UTC Wed,Fri,Sat,Sun
            "description": "Alaska timezone basketball boys scraping 6PM-9PM local (next day UTC)"
        }
    ],

    # Hawaii Time (UTC-10 HST - no daylight saving)
    # 6PM-9PM HT = 4:00-7:00 UTC next day
    "hawaii": [
        {
            "name": "basketball_boys_scrape_hawaii_1",
            "cron": "*/10 4-7 * * 2,4,5,6",  # Every 10 min, 4AM-7AM UTC Wed,Fri,Sat,Sun
            "description": "Hawaii timezone basketball boys scraping 6PM-9PM local (next day UTC)"
        }
    ]
}


# Basketball Girls game time windows (6PM - 9PM local time on Tue, Thu, Fri, Sat)
# Converted to UTC schedules based on timezone offsets
BASKETBALL_GIRLS_SCRAPE_SCHEDULES = {
    # Eastern Time (UTC-5 EST, UTC-4 EDT)
    # 6PM-9PM ET = 22:00-01:00 UTC (EST) or 22:00-01:00 UTC (EDT)
    "eastern": [
        {
            "name": "basketball_girls_scrape_eastern_1",
            "cron": "*/10 22-23 * * 1,3,4,5",  # Every 10 min, 10PM-11PM UTC Tue,Thu,Fri,Sat
            "description": "Eastern timezone basketball girls scraping 6PM-7PM local"
        },
        {
            "name": "basketball_girls_scrape_eastern_2",
            "cron": "*/10 0-1 * * 2,4,5,6",  # Every 10 min, midnight-1AM UTC Wed,Fri,Sat,Sun
            "description": "Eastern timezone basketball girls scraping 8PM-9PM local (next day UTC)"
        }
    ],

    # Central Time (UTC-6 CST, UTC-5 CDT)
    # 6PM-9PM CT = 23:00-02:00 UTC (CST) or 23:00-02:00 UTC (CDT)
    "central": [
        {
            "name": "basketball_girls_scrape_central_1",
            "cron": "*/10 23 * * 1,3,4,5",  # Every 10 min, 11PM UTC Tue,Thu,Fri,Sat
            "description": "Central timezone basketball girls scraping 6PM local"
        },
        {
            "name": "basketball_girls_scrape_central_2",
            "cron": "*/10 0-2 * * 2,4,5,6",  # Every 10 min, midnight-2AM UTC Wed,Fri,Sat,Sun
            "description": "Central timezone basketball girls scraping 7PM-9PM local (next day UTC)"
        }
    ],

    # Mountain Time (UTC-7 MST, UTC-6 MDT)
    # 6PM-9PM MT = 0:00-3:00 UTC next day (MST) or 0:00-3:00 UTC next day (MDT)
    "mountain": [
        {
            "name": "basketball_girls_scrape_mountain_1",
            "cron": "*/10 0-3 * * 2,4,5,6",  # Every 10 min, midnight-3AM UTC Wed,Fri,Sat,Sun
            "description": "Mountain timezone basketball girls scraping 6PM-9PM local (next day UTC)"
        }
    ],

    # Pacific Time (UTC-8 PST, UTC-7 PDT)
    # 6PM-9PM PT = 1:00-4:00 UTC next day (PST) or 1:00-4:00 UTC next day (PDT)
    "pacific": [
        {
            "name": "basketball_girls_scrape_pacific_1",
            "cron": "*/10 1-4 * * 2,4,5,6",  # Every 10 min, 1AM-4AM UTC Wed,Fri,Sat,Sun
            "description": "Pacific timezone basketball girls scraping 6PM-9PM local (next day UTC)"
        }
    ],

    # Alaska Time (UTC-9 AKST, UTC-8 AKDT)
    # 6PM-9PM AKT = 2:00-5:00 UTC next day (AKST) or 2:00-5:00 UTC next day (AKDT)
    "alaska": [
        {
            "name": "basketball_girls_scrape_alaska_1",
            "cron": "*/10 2-5 * * 2,4,5,6",  # Every 10 min, 2AM-5AM UTC Wed,Fri,Sat,Sun
            "description": "Alaska timezone basketball girls scraping 6PM-9PM local (next day UTC)"
        }
    ],

    # Hawaii Time (UTC-10 HST - no daylight saving)
    # 6PM-9PM HT = 4:00-7:00 UTC next day
    "hawaii": [
        {
            "name": "basketball_girls_scrape_hawaii_1",
            "cron": "*/10 4-7 * * 2,4,5,6",  # Every 10 min, 4AM-7AM UTC Wed,Fri,Sat,Sun
            "description": "Hawaii timezone basketball girls scraping 6PM-9PM local (next day UTC)"
        }
    ]
}


# Basketball Boys finalization schedules (11PM local time on game days)
# Runs Wednesday, Friday, Saturday, Sunday mornings (after Tue, Thu, Fri, Sat games)
BASKETBALL_BOYS_FINALIZE_SCHEDULES = {
    # Eastern: 11PM ET = 4AM UTC next day (EST) or 3AM UTC next day (EDT)
    "eastern": {
        "name": "basketball_boys_finalize_eastern",
        "cron": "0 4 * * 2,4,5,6",  # 4AM UTC on Wed,Fri,Sat,Sun
        "description": "Eastern timezone basketball boys finalization 11PM local after games"
    },

    # Central: 11PM CT = 5AM UTC next day (CST) or 4AM UTC next day (CDT)
    "central": {
        "name": "basketball_boys_finalize_central",
        "cron": "0 5 * * 2,4,5,6",  # 5AM UTC on Wed,Fri,Sat,Sun
        "description": "Central timezone basketball boys finalization 11PM local after games"
    },

    # Mountain: 11PM MT = 6AM UTC next day (MST) or 5AM UTC next day (MDT)
    "mountain": {
        "name": "basketball_boys_finalize_mountain",
        "cron": "0 6 * * 2,4,5,6",  # 6AM UTC on Wed,Fri,Sat,Sun
        "description": "Mountain timezone basketball boys finalization 11PM local after games"
    },

    # Pacific: 11PM PT = 7AM UTC next day (PST) or 6AM UTC next day (PDT)
    "pacific": {
        "name": "basketball_boys_finalize_pacific",
        "cron": "0 7 * * 2,4,5,6",  # 7AM UTC on Wed,Fri,Sat,Sun
        "description": "Pacific timezone basketball boys finalization 11PM local after games"
    },

    # Alaska: 11PM AKT = 8AM UTC next day (AKST) or 7AM UTC next day (AKDT)
    "alaska": {
        "name": "basketball_boys_finalize_alaska",
        "cron": "0 8 * * 2,4,5,6",  # 8AM UTC on Wed,Fri,Sat,Sun
        "description": "Alaska timezone basketball boys finalization 11PM local after games"
    },

    # Hawaii: 11PM HT = 9AM UTC next day (HST - no DST)
    "hawaii": {
        "name": "basketball_boys_finalize_hawaii",
        "cron": "0 9 * * 2,4,5,6",  # 9AM UTC on Wed,Fri,Sat,Sun
        "description": "Hawaii timezone basketball boys finalization 11PM local after games"
    }
}


# Basketball Girls finalization schedules (11PM local time on game days)
# Runs Wednesday, Friday, Saturday, Sunday mornings (after Tue, Thu, Fri, Sat games)
BASKETBALL_GIRLS_FINALIZE_SCHEDULES = {
    # Eastern: 11PM ET = 4AM UTC next day (EST) or 3AM UTC next day (EDT)
    "eastern": {
        "name": "basketball_girls_finalize_eastern",
        "cron": "0 4 * * 2,4,5,6",  # 4AM UTC on Wed,Fri,Sat,Sun
        "description": "Eastern timezone basketball girls finalization 11PM local after games"
    },

    # Central: 11PM CT = 5AM UTC next day (CST) or 4AM UTC next day (CDT)
    "central": {
        "name": "basketball_girls_finalize_central",
        "cron": "0 5 * * 2,4,5,6",  # 5AM UTC on Wed,Fri,Sat,Sun
        "description": "Central timezone basketball girls finalization 11PM local after games"
    },

    # Mountain: 11PM MT = 6AM UTC next day (MST) or 5AM UTC next day (MDT)
    "mountain": {
        "name": "basketball_girls_finalize_mountain",
        "cron": "0 6 * * 2,4,5,6",  # 6AM UTC on Wed,Fri,Sat,Sun
        "description": "Mountain timezone basketball girls finalization 11PM local after games"
    },

    # Pacific: 11PM PT = 7AM UTC next day (PST) or 6AM UTC next day (PDT)
    "pacific": {
        "name": "basketball_girls_finalize_pacific",
        "cron": "0 7 * * 2,4,5,6",  # 7AM UTC on Wed,Fri,Sat,Sun
        "description": "Pacific timezone basketball girls finalization 11PM local after games"
    },

    # Alaska: 11PM AKT = 8AM UTC next day (AKST) or 7AM UTC next day (AKDT)
    "alaska": {
        "name": "basketball_girls_finalize_alaska",
        "cron": "0 8 * * 2,4,5,6",  # 8AM UTC on Wed,Fri,Sat,Sun
        "description": "Alaska timezone basketball girls finalization 11PM local after games"
    },

    # Hawaii: 11PM HT = 9AM UTC next day (HST - no DST)
    "hawaii": {
        "name": "basketball_girls_finalize_hawaii",
        "cron": "0 9 * * 2,4,5,6",  # 9AM UTC on Wed,Fri,Sat,Sun
        "description": "Hawaii timezone basketball girls finalization 11PM local after games"
    }
}


# Get current UTC offset for a timezone (accounting for DST)
def get_utc_offset(timezone_name: str) -> int:
    """Get current UTC offset in hours for a timezone (negative for behind UTC)"""
    tz = get_timezone(timezone_name)
    now = datetime.now(tz)
    offset_seconds = now.utcoffset().total_seconds()
    return int(offset_seconds / 3600)