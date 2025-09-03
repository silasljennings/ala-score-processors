import asyncio
import os
from datetime import datetime
from typing import Callable, Dict, List
from config.timezone_schedules import (
    FOOTBALL_SCRAPE_SCHEDULES, 
    FOOTBALL_FINALIZE_SCHEDULES,
    VOLLEYBALL_SCRAPE_SCHEDULES,
    VOLLEYBALL_FINALIZE_SCHEDULES,
    get_states_for_timezone
)
from config.seasonal_schedules import (
    get_current_season,
    get_implemented_sports_for_season,
    get_season_info,
    get_available_seasons
)
from scheduler.timezone_tasks import (
    manual_timezone_scrape,
    manual_timezone_finalize,
    get_available_timezones
)


class AdvancedCronScheduler:
    def __init__(self):
        self.tasks = []
        self.timezone_tasks = {}
        self.running = False
    
    # Add a scheduled task with cron-like expression
    def schedule(self, cron_expression: str, task_func: Callable, name: str = ""):
        """Add a task to be scheduled with cron-like expression"""
        self.tasks.append({
            "cron": cron_expression,
            "function": task_func,
            "name": name or task_func.__name__,
            "last_run": None
        })
    
    # Add timezone-aware football scraping schedules
    def setup_football_schedules(self):
        """Setup all football scraping and finalization schedules for all timezones"""
        print("Setting up timezone-aware football schedules...")
        
        # Add scraping schedules for each timezone
        for timezone_name, schedules in FOOTBALL_SCRAPE_SCHEDULES.items():
            states = get_states_for_timezone(timezone_name)
            if not states:
                continue
                
            for schedule_config in schedules:
                # Create timezone-specific scraping task
                async def create_scrape_task(tz_name=timezone_name, sport="football"):
                    return await manual_timezone_scrape(tz_name, sport)
                
                create_scrape_task.__name__ = schedule_config["name"]
                
                self.schedule(
                    schedule_config["cron"],
                    create_scrape_task,
                    schedule_config["name"]
                )
                print(f"  Added scrape: {schedule_config['name']} ({schedule_config['cron']}) - {schedule_config['description']}")
        
        # Add finalization schedules for each timezone
        for timezone_name, schedule_config in FOOTBALL_FINALIZE_SCHEDULES.items():
            states = get_states_for_timezone(timezone_name)
            if not states:
                continue
                
            # Create timezone-specific finalization task
            async def create_finalize_task(tz_name=timezone_name, sport="football"):
                return await manual_timezone_finalize(tz_name, sport)
            
            create_finalize_task.__name__ = schedule_config["name"]
            
            self.schedule(
                schedule_config["cron"],
                create_finalize_task,
                schedule_config["name"]
            )
            print(f"  Added finalize: {schedule_config['name']} ({schedule_config['cron']}) - {schedule_config['description']}")
        
        print(f"Total football scheduled tasks: {len(self.tasks)}")

    # Add timezone-aware volleyball scraping schedules  
    def setup_volleyball_schedules(self):
        """Setup all volleyball scraping and finalization schedules for all timezones"""
        print("Setting up timezone-aware volleyball schedules...")
        
        # Add scraping schedules for each timezone
        for timezone_name, schedules in VOLLEYBALL_SCRAPE_SCHEDULES.items():
            states = get_states_for_timezone(timezone_name)
            if not states:
                continue
                
            for schedule_config in schedules:
                # Create timezone-specific volleyball scraping task
                async def create_volleyball_scrape_task(tz_name=timezone_name, sport="volleyball"):
                    return await manual_timezone_scrape(tz_name, sport)
                
                create_volleyball_scrape_task.__name__ = schedule_config["name"]
                
                self.schedule(
                    schedule_config["cron"],
                    create_volleyball_scrape_task,
                    schedule_config["name"]
                )
                print(f"  Added volleyball scrape: {schedule_config['name']} ({schedule_config['cron']}) - {schedule_config['description']}")
        
        # Add finalization schedules for each timezone
        for timezone_name, schedule_config in VOLLEYBALL_FINALIZE_SCHEDULES.items():
            states = get_states_for_timezone(timezone_name)
            if not states:
                continue
                
            # Create timezone-specific volleyball finalization task
            async def create_volleyball_finalize_task(tz_name=timezone_name, sport="volleyball"):
                return await manual_timezone_finalize(tz_name, sport)
            
            create_volleyball_finalize_task.__name__ = schedule_config["name"]
            
            self.schedule(
                schedule_config["cron"],
                create_volleyball_finalize_task,
                schedule_config["name"]
            )
            print(f"  Added volleyball finalize: {schedule_config['name']} ({schedule_config['cron']}) - {schedule_config['description']}")
        
        print(f"Total volleyball scheduled tasks: {len(self.tasks) - len(FOOTBALL_SCRAPE_SCHEDULES)*2 - len(FOOTBALL_FINALIZE_SCHEDULES)}")

    # Setup all sports schedules
    def setup_all_sports_schedules(self):
        """Setup schedules for all sports (football + volleyball)"""
        self.setup_football_schedules()
        self.setup_volleyball_schedules()
        print(f"Total all sports scheduled tasks: {len(self.tasks)}")

    # Setup seasonal sports schedules
    def setup_seasonal_schedules(self, season: str = None):
        """Setup schedules based on season (auto-detects current season if not specified)"""
        if not season:
            season = get_current_season()
            
        season_info = get_season_info(season)
        implemented_sports = season_info["implemented_sports"]
        
        print(f"Setting up schedules for {season} season...")
        print(f"Season: {season_info['description']}")
        print(f"Implemented sports for this season: {implemented_sports}")
        
        if season_info["unimplemented_sports"]:
            print(f"Note: These sports in season don't have schedules yet: {season_info['unimplemented_sports']}")
        
        # Setup schedules for each implemented sport in the season
        for sport in implemented_sports:
            if sport == "football":
                self.setup_football_schedules()
                print(f"✓ Added football schedules")
            elif sport == "volleyball":
                self.setup_volleyball_schedules()
                print(f"✓ Added volleyball schedules")
            # Future sports would be added here
            # elif sport == "basketball":
            #     self.setup_basketball_schedules()
            # elif sport == "baseball":
            #     self.setup_baseball_schedules()
            # etc.
        
        if not implemented_sports:
            print(f"⚠️  No implemented sports for {season} season yet")
        
        print(f"Total {season} season scheduled tasks: {len(self.tasks)}")
        return season_info

    # Get seasonal schedule information
    def get_seasonal_info(self, season: str = None):
        """Get information about seasonal scheduling"""
        if not season:
            season = get_current_season()
        return get_season_info(season)
    
    # Check if current time matches cron expression
    def _matches_cron(self, cron_expr: str, current_time: datetime) -> bool:
        """Check if current time matches cron expression (minute hour day month dow)"""
        try:
            parts = cron_expr.strip().split()
            if len(parts) != 5:
                return False
            
            minute, hour, day, month, dow = parts
            
            # Enhanced cron matching - supports *, ranges, lists, and step values
            def matches_field(field_value: str, current_value: int, max_value: int = None) -> bool:
                if field_value == "*":
                    return True
                
                # Handle step values (e.g., */3, 0-30/3)
                if "/" in field_value:
                    base, step = field_value.split("/")
                    step = int(step)
                    
                    if base == "*":
                        return current_value % step == 0
                    elif "-" in base:
                        start, end = map(int, base.split("-"))
                        return start <= current_value <= end and (current_value - start) % step == 0
                    else:
                        start = int(base)
                        return current_value >= start and (current_value - start) % step == 0
                
                # Handle ranges (e.g., 21-23)
                if "-" in field_value:
                    start, end = map(int, field_value.split("-"))
                    return start <= current_value <= end
                
                # Handle comma-separated lists (e.g., 3,4,5)
                if "," in field_value:
                    return str(current_value) in field_value.split(",")
                
                # Exact match
                return str(current_value) == field_value
            
            return (
                matches_field(minute, current_time.minute, 59) and
                matches_field(hour, current_time.hour, 23) and
                matches_field(day, current_time.day, 31) and
                matches_field(month, current_time.month, 12) and
                matches_field(dow, current_time.weekday(), 6)  # 0=Monday
            )
        except Exception as e:
            print(f"Error parsing cron expression '{cron_expr}': {e}")
            return False
    
    # Start the scheduler loop
    async def start(self):
        """Start the scheduler background loop"""
        self.running = True
        print(f"Advanced scheduler started with {len(self.tasks)} tasks")
        
        # List all scheduled tasks for debugging
        for task in self.tasks:
            print(f"  - {task['name']}: {task['cron']}")
        
        while self.running:
            current_time = datetime.utcnow()  # Use UTC for cron matching
            current_minute = current_time.strftime("%Y-%m-%d %H:%M")
            
            for task in self.tasks:
                # Only run once per minute
                if task["last_run"] == current_minute:
                    continue
                
                if self._matches_cron(task["cron"], current_time):
                    print(f"[{current_time} UTC] Running scheduled task: {task['name']}")
                    try:
                        if asyncio.iscoroutinefunction(task["function"]):
                            await task["function"]()
                        else:
                            task["function"]()
                        task["last_run"] = current_minute
                        print(f"[{current_time} UTC] Completed task: {task['name']}")
                    except Exception as e:
                        print(f"[{current_time} UTC] Error in task {task['name']}: {e}")
            
            # Check every 30 seconds
            await asyncio.sleep(30)
    
    # Stop the scheduler
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        print("Advanced scheduler stopped")
    
    # Get schedule status
    def get_status(self):
        """Get current scheduler status and task list"""
        return {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "tasks": [
                {
                    "name": task["name"],
                    "cron": task["cron"], 
                    "last_run": task["last_run"]
                }
                for task in self.tasks
            ]
        }


# Global advanced scheduler instance
advanced_scheduler = AdvancedCronScheduler()