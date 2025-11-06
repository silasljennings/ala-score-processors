import os
import asyncio
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from config.settings import get_states_list, get_scrape_concurrency, get_batch_pause_ms, get_default_sport, get_ala_score_processor_secret
from utils.time_helpers import within_run_window_ny, today_mdy_ny
from utils.data_helpers import to_mdy
from utils.url_helpers import build_scores_url_from_sport
from scraper.web_client import fetch_state_page, sleep
from scraper.score_scraper import scrape
from database.supabase_client import dedupe_by_contest_id, chunked_upsert
from finalize.score_finalizer import finalize_scores


# Authentication helper function
def validate_api_key(request: Request):
    """Validate X_ALA_KEY header matches ALA_SCORE_PROCESSOR_SECRET"""
    expected_key = get_ala_score_processor_secret()
    if not expected_key:
        raise HTTPException(status_code=500, detail="Authentication secret not configured")
    
    provided_key = request.headers.get("X_ALA_KEY")
    if not provided_key:
        raise HTTPException(status_code=401, detail="X_ALA_KEY header required")
    
    if provided_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid X_ALA_KEY")


# Main scraping endpoint handler
async def scrape_handler(request: Request) -> JSONResponse:
    """Handle POST /scrape requests to scrape sports scores from MaxPreps"""
    # Validate authentication
    validate_api_key(request)
    
    req_id = os.urandom(4).hex()
    
    try:
        body = await request.json()
    except Exception:
        body = {}

    # Parse states parameter from request body or use default
    states = []
    if isinstance(body.get("states"), str) and body["states"]:
        states = [s.strip().lower() for s in body["states"].split(",") if s.strip()]
    elif isinstance(body.get("states"), list) and body["states"]:
        states = [str(s).lower() for s in body["states"]]
    else:
        states = get_states_list()

    # Parse sport parameter from request or use default
    sport = (
        body.get("sport")
        or request.query_params.get("sport")
        or get_default_sport()
    ).lower()

    # Parse date override and force flags
    date_override = body.get("date") or request.query_params.get("date")
    date_override_mdy = to_mdy(date_override) if date_override else None
    force = body.get("force") or request.query_params.get("force") == "1" or bool(
        date_override_mdy
    )

    # Check if within allowed scraping window unless forced
    if not within_run_window_ny() and not force:
        return JSONResponse({"ok": True, "skipped": "outside window"})

    date_str = date_override_mdy or today_mdy_ny()
    rows, meta = [], []

    # Process states in batches with concurrency control
    concurrency = get_scrape_concurrency()
    batch_pause_ms = get_batch_pause_ms()
    
    for i in range(0, len(states), concurrency):
        batch = states[i : i + concurrency]
        tasks = []
        
        for idx, state_code in enumerate(batch):
            await sleep(idx * 15)
            url = build_scores_url_from_sport(state_code, date_str, sport)
            tasks.append(fetch_state_page(url, f"{req_id}/{state_code}"))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for state_code, html in zip(batch, results):
            if isinstance(html, Exception):
                meta.append({"state_code": state_code, "error": str(html)})
            else:
                r = scrape(html, build_scores_url_from_sport(state_code, date_str, sport), state_code, sport)
                rows.extend(r)
                meta.append({"state_code": state_code, "count": len(r)})

        if i + concurrency < len(states):
            await sleep(batch_pause_ms)

    if not rows:
        return JSONResponse(
            {"ok": True, "sport": sport, "date": date_str, "meta": meta, "inserted": 0}
        )

    # Dedupe and insert to database
    deduped = dedupe_by_contest_id(rows)
    inserted = await chunked_upsert(req_id, deduped, 500)

    return JSONResponse(
        {
            "ok": True,
            "sport": sport,
            "date": date_str,
            "inserted": inserted,
            "skipped": len(rows) - len(deduped),
            "meta": meta,
            "sample": deduped[:2],
        }
    )


# Score finalization endpoint handler
async def finalize_handler(request: Request) -> JSONResponse:
    """Handle POST /finalize requests to finalize scraped scores"""
    # Validate authentication
    validate_api_key(request)
    
    req_id = os.urandom(4).hex()
    print(f"[{req_id}] Incoming finalize request")
    
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    print(f"[{req_id}] Request body: {body}")
    
    # Parse states parameter
    states = []
    if isinstance(body.get("states"), str) and body["states"]:
        states = [s.strip().lower() for s in body["states"].split(",") if s.strip()]
    elif isinstance(body.get("states"), list) and body["states"]:
        states = [str(s).lower() for s in body["states"]]
    else:
        states = get_states_list()
    
    # Parse sport parameter
    sport = (
        body.get("sport")
        or request.query_params.get("sport") 
        or get_default_sport()
    ).upper()
    
    if not states or not sport:
        return JSONResponse(
            {"error": "states and sport required"}, 
            status_code=400
        )
    
    try:
        # Execute finalization
        result = await finalize_scores(states, sport, req_id)
        return JSONResponse(result)
        
    except Exception as e:
        print(f"[{req_id}] Exception: {e}")
        return JSONResponse(
            {"error": str(e)}, 
            status_code=500
        )