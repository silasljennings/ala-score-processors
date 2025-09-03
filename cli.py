# cli.py - Command line interface for manual task execution
import asyncio
import argparse
import sys
from scheduler.tasks import (
    scheduled_scrape_task, 
    scheduled_football_scrape, 
    scheduled_scrape_with_config,
    scheduled_finalize_task,
    scheduled_football_finalize,
    scheduled_finalize_with_config
)
from scheduler.timezone_tasks import (
    manual_timezone_scrape,
    manual_timezone_finalize,
    get_available_timezones
)


# Run scraping task from command line
async def run_scrape_task(args):
    """Execute scraping task with CLI arguments"""
    states = args.states.split(",") if args.states else None
    result = await scheduled_scrape_with_config(
        states=states,
        sport=args.sport,
        force=args.force
    )
    print(f"Scrape completed: {result}")


# Run default scheduled task
async def run_default_task(args):
    """Execute default scheduled scraping task"""
    result = await scheduled_scrape_task()
    print(f"Default task completed: {result}")


# Run football scheduled task
async def run_football_task(args):
    """Execute football scheduled scraping task"""
    result = await scheduled_football_scrape()
    print(f"Football task completed: {result}")


# Run finalize task from command line
async def run_finalize_task(args):
    """Execute finalization task with CLI arguments"""
    states = args.states.split(",") if args.states else None
    result = await scheduled_finalize_with_config(
        states=states,
        sport=args.sport
    )
    print(f"Finalize completed: {result}")


# Run default finalize task
async def run_default_finalize_task(args):
    """Execute default scheduled finalization task"""
    result = await scheduled_finalize_task()
    print(f"Default finalize task completed: {result}")


# Run football finalize task
async def run_football_finalize_task(args):
    """Execute football scheduled finalization task"""
    result = await scheduled_football_finalize()
    print(f"Football finalize task completed: {result}")


# Run timezone-specific scraping task
async def run_timezone_scrape_task(args):
    """Execute timezone-specific scraping task"""
    sport = getattr(args, 'sport', 'football')  # Default to football if not specified
    result = await manual_timezone_scrape(args.timezone, sport)
    print(f"Timezone {sport} scrape completed for {args.timezone}: {result}")


# Run timezone-specific finalization task
async def run_timezone_finalize_task(args):
    """Execute timezone-specific finalization task"""
    sport = getattr(args, 'sport', 'football')  # Default to football if not specified
    result = await manual_timezone_finalize(args.timezone, sport)
    print(f"Timezone {sport} finalize completed for {args.timezone}: {result}")


# Run volleyball scraping task for all timezones
async def run_volleyball_scrape_all_task(args):
    """Execute volleyball scraping for all timezones"""
    timezones = get_available_timezones()
    for timezone in timezones:
        try:
            result = await manual_timezone_scrape(timezone, "volleyball")
            print(f"Volleyball scrape completed for {timezone}: {result}")
        except Exception as e:
            print(f"Error scraping volleyball for {timezone}: {e}")


# Run volleyball finalization task for all timezones  
async def run_volleyball_finalize_all_task(args):
    """Execute volleyball finalization for all timezones"""
    timezones = get_available_timezones()
    for timezone in timezones:
        try:
            result = await manual_timezone_finalize(timezone, "volleyball")
            print(f"Volleyball finalize completed for {timezone}: {result}")
        except Exception as e:
            print(f"Error finalizing volleyball for {timezone}: {e}")


# Main CLI entry point
def main():
    """Main CLI entry point with argument parsing"""
    parser = argparse.ArgumentParser(description="MaxPreps Score Scraper CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Scrape command with custom options
    scrape_parser = subparsers.add_parser("scrape", help="Run custom scraping task")
    scrape_parser.add_argument("--states", help="Comma-separated list of states (e.g., al,ga,fl)")
    scrape_parser.add_argument("--sport", default="football", help="Sport to scrape (default: football)")
    scrape_parser.add_argument("--force", action="store_true", help="Force run outside time window")
    
    # Default task command
    default_parser = subparsers.add_parser("default", help="Run default scheduled task")
    
    # Football task command
    football_parser = subparsers.add_parser("football", help="Run football scheduled task")
    
    # Finalize command with custom options
    finalize_parser = subparsers.add_parser("finalize", help="Run custom finalization task")
    finalize_parser.add_argument("--states", help="Comma-separated list of states (e.g., al,ga,fl)")
    finalize_parser.add_argument("--sport", default="football", help="Sport to finalize (default: football)")
    
    # Default finalize task command
    default_finalize_parser = subparsers.add_parser("default-finalize", help="Run default scheduled finalization task")
    
    # Football finalize task command  
    football_finalize_parser = subparsers.add_parser("football-finalize", help="Run football scheduled finalization task")
    
    # Timezone scrape command
    timezone_scrape_parser = subparsers.add_parser("timezone-scrape", help="Run timezone-specific scraping")
    timezone_scrape_parser.add_argument("timezone", choices=get_available_timezones(), help="Timezone to scrape")
    timezone_scrape_parser.add_argument("--sport", default="football", choices=["football", "volleyball"], help="Sport to scrape (default: football)")
    
    # Timezone finalize command
    timezone_finalize_parser = subparsers.add_parser("timezone-finalize", help="Run timezone-specific finalization")
    timezone_finalize_parser.add_argument("timezone", choices=get_available_timezones(), help="Timezone to finalize")
    timezone_finalize_parser.add_argument("--sport", default="football", choices=["football", "volleyball"], help="Sport to finalize (default: football)")
    
    # Volleyball scrape all timezones command
    volleyball_scrape_all_parser = subparsers.add_parser("volleyball-scrape-all", help="Run volleyball scraping for all timezones")
    
    # Volleyball finalize all timezones command
    volleyball_finalize_all_parser = subparsers.add_parser("volleyball-finalize-all", help="Run volleyball finalization for all timezones")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute appropriate command
    if args.command == "scrape":
        asyncio.run(run_scrape_task(args))
    elif args.command == "default":
        asyncio.run(run_default_task(args))
    elif args.command == "football":
        asyncio.run(run_football_task(args))
    elif args.command == "finalize":
        asyncio.run(run_finalize_task(args))
    elif args.command == "default-finalize":
        asyncio.run(run_default_finalize_task(args))
    elif args.command == "football-finalize":
        asyncio.run(run_football_finalize_task(args))
    elif args.command == "timezone-scrape":
        asyncio.run(run_timezone_scrape_task(args))
    elif args.command == "timezone-finalize":
        asyncio.run(run_timezone_finalize_task(args))
    elif args.command == "volleyball-scrape-all":
        asyncio.run(run_volleyball_scrape_all_task(args))
    elif args.command == "volleyball-finalize-all":
        asyncio.run(run_volleyball_finalize_all_task(args))


if __name__ == "__main__":
    main()