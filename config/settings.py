import os


# Environment configuration for the sports score scraping application
def get_supabase_url() -> str:
    """Get Supabase database URL from environment variables"""
    return os.environ.get("SUPABASE_URL")


# Get Supabase service role key for database operations
def get_supabase_service_role_key() -> str:
    """Get Supabase service role key from environment variables"""
    return os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


# Database table name for storing MaxPrep scores
TABLE = "ala_max_prep_scores"


# Parse and validate states list from environment variable
def get_states_list() -> list[str]:
    """Parse states list from STATES environment variable, defaults to Alabama"""
    states_env = os.environ.get("STATES") or "al"
    return [s.strip().lower() for s in states_env.split(",") if s.strip()]


# Get concurrency level for web scraping operations
def get_scrape_concurrency() -> int:
    """Get maximum concurrent scraping requests, defaults to 2"""
    return int(os.environ.get("SCRAPE_CONCURRENCY") or 2)


# Get pause duration between scraping batches
def get_batch_pause_ms() -> int:
    """Get pause duration in milliseconds between scraping batches, defaults to 150ms"""
    return int(os.environ.get("SCRAPE_BATCH_PAUSE_MS") or 150)


# Get retry count for failed HTTP requests
def get_scrape_retries() -> int:
    """Get number of retries for failed scraping requests, defaults to 2"""
    return int(os.environ.get("SCRAPE_RETRIES") or 2)


# Get default sport from environment variable
def get_default_sport() -> str:
    """Get default sport to scrape, defaults to football"""
    return os.environ.get("SPORT") or "football"