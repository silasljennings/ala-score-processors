# main.py - FastAPI application entry point for MaxPreps sports score scraper
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
from api.routes import scrape_handler, finalize_handler
from scheduler.cron_scheduler import scheduler
from scheduler.advanced_scheduler import advanced_scheduler
from scheduler.tasks import (
    scheduled_scrape_task, 
    scheduled_football_scrape,
    scheduled_finalize_task,
    scheduled_football_finalize
)
from scheduler.timezone_tasks import (
    manual_timezone_scrape,
    manual_timezone_finalize,
    get_available_timezones
)
from config.seasonal_schedules import (
    get_current_season,
    get_available_seasons,
    get_season_info
)


# Request models for API endpoints
class ScrapeRequest(BaseModel):
    states: Optional[List[str]] = None
    sport: Optional[str] = None
    date: Optional[str] = None
    force: Optional[bool] = False

class FinalizeRequest(BaseModel):
    states: Optional[List[str]] = None
    sport: Optional[str] = None


# Request wrapper to convert Pydantic models to FastAPI Request-like objects
class RequestWrapper:
    def __init__(self, body_data: dict, headers: dict = None):
        self.body_data = body_data
        self.query_params = {}
        self.headers = headers or {}
    
    async def json(self):
        return self.body_data


# Background task lifecycle manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with background scheduler"""
    # Check if scheduler should be enabled
    enable_scheduler = os.environ.get("ENABLE_SCHEDULER", "false").lower() == "true"
    use_timezone_schedules = os.environ.get("USE_TIMEZONE_SCHEDULES", "false").lower() == "true"
    
    if enable_scheduler:
        if use_timezone_schedules:
            # Use advanced timezone-aware scheduling (matches your SQL schedules)
            sport_filter = os.environ.get("SPORT_SCHEDULES", "seasonal").lower()
            
            if sport_filter == "football":
                advanced_scheduler.setup_football_schedules()
            elif sport_filter == "volleyball":
                advanced_scheduler.setup_volleyball_schedules()
            elif sport_filter == "all":
                advanced_scheduler.setup_all_sports_schedules()
            elif sport_filter == "seasonal" or sport_filter in get_available_seasons():
                # Use seasonal scheduling (auto-detect or specific season)
                season = None if sport_filter == "seasonal" else sport_filter
                advanced_scheduler.setup_seasonal_schedules(season)
            else:
                # Default to seasonal if unknown value
                print(f"Unknown SPORT_SCHEDULES value '{sport_filter}', defaulting to seasonal")
                advanced_scheduler.setup_seasonal_schedules()
                
            scheduler_task = asyncio.create_task(advanced_scheduler.start())
        else:
            # Use simple scheduling (original basic schedules)
            setup_scheduled_tasks()
            scheduler_task = asyncio.create_task(scheduler.start())
        
        yield
        
        # Cleanup: stop scheduler
        if use_timezone_schedules:
            advanced_scheduler.stop()
        else:
            scheduler.stop()
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
    else:
        yield


# Configure scheduled tasks based on environment
def setup_scheduled_tasks():
    """Setup cron-like scheduled tasks"""
    # Default scraping schedule (Thu-Sat at 8PM Eastern)
    default_schedule = os.environ.get("SCRAPE_SCHEDULE", "0 20 * * 3,4,5")  # 8PM Thu,Fri,Sat
    scheduler.schedule(default_schedule, scheduled_scrape_task, "default_scrape")
    
    # Football specific schedule (Friday nights at 9PM Eastern)
    football_schedule = os.environ.get("FOOTBALL_SCHEDULE", "0 21 * * 4")  # 9PM Friday
    scheduler.schedule(football_schedule, scheduled_football_scrape, "football_scrape")
    
    # Default finalization schedule (runs after scraping, e.g., 10PM Thu-Sat)
    finalize_schedule = os.environ.get("FINALIZE_SCHEDULE", "0 22 * * 3,4,5")  # 10PM Thu,Fri,Sat
    scheduler.schedule(finalize_schedule, scheduled_finalize_task, "default_finalize")
    
    # Football finalization schedule (Saturday morning to finalize Friday games)
    football_finalize_schedule = os.environ.get("FOOTBALL_FINALIZE_SCHEDULE", "0 8 * * 5")  # 8AM Saturday
    scheduler.schedule(football_finalize_schedule, scheduled_football_finalize, "football_finalize")
    
    print(f"Configured scheduled tasks:")
    print(f"  - Default scrape: {default_schedule}")
    print(f"  - Football scrape: {football_schedule}")
    print(f"  - Default finalize: {finalize_schedule}")
    print(f"  - Football finalize: {football_finalize_schedule}")


# Initialize FastAPI application with lifecycle management
app = FastAPI(lifespan=lifespan)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    enable_scheduler = os.environ.get("ENABLE_SCHEDULER", "false").lower() == "true"
    use_timezone_schedules = os.environ.get("USE_TIMEZONE_SCHEDULES", "false").lower() == "true"
    sport_filter = os.environ.get("SPORT_SCHEDULES", "seasonal").lower()
    
    status = {
        "status": "healthy",
        "scheduler_enabled": enable_scheduler,
        "timezone_schedules": use_timezone_schedules,
        "sport_schedules": sport_filter,
        "current_season": get_current_season(),
        "season_info": get_season_info()
    }
    
    if enable_scheduler:
        if use_timezone_schedules:
            status["scheduler_status"] = advanced_scheduler.get_status()
        else:
            status["scheduled_tasks"] = len(scheduler.tasks)
    
    return status


# Get seasonal information endpoint
@app.get("/season")
async def get_season_endpoint():
    """Get current season information"""
    current_season = get_current_season()
    return {
        "current_season": current_season,
        "season_info": get_season_info(current_season),
        "available_seasons": get_available_seasons()
    }


# Register scraping endpoint
@app.post("/scrape")
async def scrape_endpoint(request: Request):
    """Endpoint to scrape sports scores from MaxPreps and store in database"""
    return await scrape_handler(request)


# Register finalization endpoint  
@app.post("/finalize")
async def finalize_endpoint(request: Request):
    """Endpoint to finalize scraped scores by updating contest states"""
    return await finalize_handler(request)


# Manual trigger endpoint for scheduled tasks
@app.post("/trigger/{task_name}")
async def trigger_scheduled_task(task_name: str):
    """Manually trigger a scheduled task"""
    if task_name == "default_scrape":
        result = await scheduled_scrape_task()
        return {"triggered": task_name, "result": result.body}
    elif task_name == "football_scrape":
        result = await scheduled_football_scrape()
        return {"triggered": task_name, "result": result.body}
    elif task_name == "default_finalize":
        result = await scheduled_finalize_task()
        return {"triggered": task_name, "result": result.body}
    elif task_name == "football_finalize":
        result = await scheduled_football_finalize()
        return {"triggered": task_name, "result": result.body}
    else:
        available_tasks = ["default_scrape", "football_scrape", "default_finalize", "football_finalize"]
        return {"error": f"Unknown task: {task_name}", "available": available_tasks}


# Manual trigger endpoint for timezone-specific tasks
@app.post("/trigger/timezone/{action}/{timezone}")
async def trigger_timezone_task(action: str, timezone: str, sport: str = "football"):
    """Manually trigger a timezone-specific task"""
    available_timezones = get_available_timezones()
    available_sports = ["football", "volleyball"]
    
    if timezone not in available_timezones:
        return {"error": f"Unknown timezone: {timezone}", "available_timezones": available_timezones}
    
    if sport not in available_sports:
        return {"error": f"Unknown sport: {sport}", "available_sports": available_sports}
    
    try:
        if action == "scrape":
            result = await manual_timezone_scrape(timezone, sport)
            return {"triggered": f"{action}_{sport}_{timezone}", "result": result}
        elif action == "finalize":
            result = await manual_timezone_finalize(timezone, sport)
            return {"triggered": f"{action}_{sport}_{timezone}", "result": result}
        else:
            return {"error": f"Unknown action: {action}", "available_actions": ["scrape", "finalize"]}
    except Exception as e:
        return {"error": str(e)}


# Manual trigger endpoint for volleyball tasks across all timezones
@app.post("/trigger/volleyball/{action}")
async def trigger_volleyball_all_timezones(action: str):
    """Manually trigger volleyball tasks for all timezones"""
    available_timezones = get_available_timezones()
    results = {}
    
    try:
        for timezone in available_timezones:
            if action == "scrape":
                result = await manual_timezone_scrape(timezone, "volleyball")
                results[timezone] = {"status": "success", "result": result}
            elif action == "finalize":
                result = await manual_timezone_finalize(timezone, "volleyball")
                results[timezone] = {"status": "success", "result": result}
            else:
                return {"error": f"Unknown action: {action}", "available_actions": ["scrape", "finalize"]}
        
        return {"triggered": f"volleyball_{action}_all", "results": results}
    except Exception as e:
        return {"error": str(e)}