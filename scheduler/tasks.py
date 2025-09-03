from api.routes import scrape_handler, finalize_handler
from fastapi import Request
from config.settings import get_states_list, get_default_sport, get_ala_score_processor_secret


# Wrapper class to simulate FastAPI Request for scheduled tasks
class MockRequest:
    def __init__(self, body_data: dict = None):
        self.body_data = body_data or {}
        self.query_params = {}
        # Add authentication header for scheduled tasks
        self.headers = {"X_ALA_KEY": get_ala_score_processor_secret() or ""}
    
    async def json(self):
        return self.body_data


# Scheduled scraping task for default configuration
async def scheduled_scrape_task():
    """Run scraping task with default configuration (for cron scheduling)"""
    mock_request = MockRequest({
        "states": get_states_list(),
        "sport": get_default_sport(),
        "force": False  # Respect time window
    })
    
    result = await scrape_handler(mock_request)
    print(f"Scheduled scrape completed: {result.body}")
    return result


# Scheduled scraping task with custom configuration
async def scheduled_scrape_with_config(states: list = None, sport: str = None, force: bool = False):
    """Run scraping task with custom configuration"""
    mock_request = MockRequest({
        "states": states or get_states_list(),
        "sport": sport or get_default_sport(),
        "force": force
    })
    
    result = await scrape_handler(mock_request)
    print(f"Custom scheduled scrape completed: {result.body}")
    return result


# Example: Football scraping on Friday nights (game days)
async def scheduled_football_scrape():
    """Scheduled task specifically for football on Friday nights"""
    return await scheduled_scrape_with_config(
        states=get_states_list(),
        sport="football",
        force=True  # Force run regardless of time window
    )


# Scheduled finalization task for default configuration
async def scheduled_finalize_task():
    """Run score finalization task with default configuration (for cron scheduling)"""
    mock_request = MockRequest({
        "states": get_states_list(),
        "sport": get_default_sport()
    })
    
    result = await finalize_handler(mock_request)
    print(f"Scheduled finalize completed: {result.body}")
    return result


# Scheduled finalization task with custom configuration
async def scheduled_finalize_with_config(states: list = None, sport: str = None):
    """Run finalization task with custom configuration"""
    mock_request = MockRequest({
        "states": states or get_states_list(),
        "sport": sport or get_default_sport()
    })
    
    result = await finalize_handler(mock_request)
    print(f"Custom scheduled finalize completed: {result.body}")
    return result


# Example: Football finalization task
async def scheduled_football_finalize():
    """Scheduled task specifically for football score finalization"""
    return await scheduled_finalize_with_config(
        states=get_states_list(),
        sport="football"
    )