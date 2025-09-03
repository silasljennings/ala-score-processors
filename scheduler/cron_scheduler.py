import asyncio
import os
from datetime import datetime
from typing import Callable
from utils.time_helpers import now_in_ny


class CronScheduler:
    def __init__(self):
        self.tasks = []
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
    
    # Check if current time matches cron expression
    def _matches_cron(self, cron_expr: str, current_time: datetime) -> bool:
        """Check if current time matches cron expression (minute hour day month dow)"""
        try:
            parts = cron_expr.strip().split()
            if len(parts) != 5:
                return False
            
            minute, hour, day, month, dow = parts
            
            # Simple cron matching - supports * and specific values
            def matches_field(field_value: str, current_value: int) -> bool:
                if field_value == "*":
                    return True
                if "," in field_value:
                    return str(current_value) in field_value.split(",")
                return str(current_value) == field_value
            
            return (
                matches_field(minute, current_time.minute) and
                matches_field(hour, current_time.hour) and
                matches_field(day, current_time.day) and
                matches_field(month, current_time.month) and
                matches_field(dow, current_time.weekday())  # 0=Monday
            )
        except Exception as e:
            print(f"Error parsing cron expression '{cron_expr}': {e}")
            return False
    
    # Start the scheduler loop
    async def start(self):
        """Start the scheduler background loop"""
        self.running = True
        print(f"Scheduler started with {len(self.tasks)} tasks")
        
        while self.running:
            current_time = now_in_ny()
            current_minute = current_time.strftime("%Y-%m-%d %H:%M")
            
            for task in self.tasks:
                # Only run once per minute
                if task["last_run"] == current_minute:
                    continue
                
                if self._matches_cron(task["cron"], current_time):
                    print(f"[{current_time}] Running scheduled task: {task['name']}")
                    try:
                        if asyncio.iscoroutinefunction(task["function"]):
                            await task["function"]()
                        else:
                            task["function"]()
                        task["last_run"] = current_minute
                        print(f"[{current_time}] Completed task: {task['name']}")
                    except Exception as e:
                        print(f"[{current_time}] Error in task {task['name']}: {e}")
            
            # Check every 30 seconds
            await asyncio.sleep(30)
    
    # Stop the scheduler
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        print("Scheduler stopped")


# Global scheduler instance
scheduler = CronScheduler()