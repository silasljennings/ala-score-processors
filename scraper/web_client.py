import asyncio
import httpx
from config.settings import get_scrape_retries


# Sleep for specified milliseconds asynchronously
async def sleep(ms: int) -> None:
    """Sleep for specified number of milliseconds"""
    await asyncio.sleep(ms / 1000)


# Fetch URL with exponential backoff retry logic
async def fetch_with_retry(url: str, retries: int = None, ctx: str = "") -> httpx.Response:
    """Fetch URL with retry logic for handling temporary failures"""
    if retries is None:
        retries = get_scrape_retries()
    
    attempt = 0
    base = 0.25
    
    async with httpx.AsyncClient() as client:
        while True:
            res = await client.get(
                url,
                headers={
                    "user-agent": "Mozilla/5.0 (compatible; CloudRunBot/1.0)",
                    "accept-language": "en-US,en;q=0.9",
                },
            )
            
            if res.status_code == 200:
                return res
            
            if attempt >= retries or res.status_code not in [429, 500, 502, 503, 504]:
                raise Exception(f"[{ctx}] fetch failed {res.status_code} {url}")
            
            delay = base * (2**attempt) + (0.2 * attempt)
            print(f"[{ctx}] retry {attempt+1}/{retries} in {delay:.2f}s")
            await asyncio.sleep(delay)
            attempt += 1


# Fetch single state page with rate limiting
async def fetch_state_page(url: str, ctx: str) -> str:
    """Fetch state scores page with polite rate limiting"""
    await sleep(int(200 * (0.5)))
    res = await fetch_with_retry(url, get_scrape_retries(), ctx)
    return res.text