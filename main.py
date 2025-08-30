import os
import uuid
import asyncio
import httpx
from fastapi import FastAPI, Request
from bs4 import BeautifulSoup
from supabase import create_client, Client
from datetime import datetime
from typing import List, Dict, Any

# ---------- Supabase ----------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
TABLE = "ala_max_prep_scores"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ---------- Config ----------
DEFAULT_STATES = os.getenv("STATES", "al").split(",")
CONCURRENCY = int(os.getenv("SCRAPE_CONCURRENCY", 2))
BATCH_PAUSE_MS = int(os.getenv("SCRAPE_BATCH_PAUSE_MS", 150))
RETRIES = int(os.getenv("SCRAPE_RETRIES", 2))

# ---------- FastAPI ----------
app = FastAPI()


# ---------- Helpers ----------
def today_mdy() -> str:
    now = datetime.now()
    return f"{now.month}/{now.day}/{now.year}"


def build_scores_url(state_code: str, mdy: str, sport: str) -> str:
    return f"https://www.maxpreps.com/{state_code}/{sport.lower()}/scores/?date={mdy}"


def parse_date_from_url(u: str) -> str | None:
    if not u:
        return None
    try:
        if "date=" in u:
            date_str = u.split("date=")[-1].split("&")[0]
            mm, dd, yyyy = date_str.split("/")
            return f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"
    except Exception:
        return None
    return None


async def fetch_with_retry(url: str, retries: int, ctx: str = "") -> str:
    attempt = 0
    base_delay = 0.25
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            try:
                res = await client.get(
                    url,
                    headers={
                        "user-agent": "Mozilla/5.0 (compatible; CloudRunScraper/1.0)",
                        "accept-language": "en-US,en;q=0.9",
                    },
                )
                if res.status_code == 200:
                    return res.text
                if attempt >= retries or res.status_code not in [429, 500, 502, 503, 504]:
                    raise Exception(f"[{ctx}] fetch failed {res.status_code} {url}")
            except Exception as e:
                if attempt >= retries:
                    raise e
            delay = base_delay * (2**attempt)
            await asyncio.sleep(delay)
            attempt += 1


def scrape(html: str, page_url: str, state_code: str, sport: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    boxes = soup.select("li.c .contest-box-item")
    results = []

    for box in boxes:
        li = box.find_parent("li")
        contest_id = li.get("data-contest-id") if li else None
        if not contest_id:
            continue

        teams_attr = li.get("data-teams")
        a = box.select_one("a.c-c")
        game_href = a.get("href") if a else None
        game_url = httpx.URL(game_href, base=page_url).human_repr() if game_href else None

        contest_state = box.get("data-contest-state")
        is_live = box.get("data-contest-live") == "1"
        details = (box.select_one(".details").get_text(strip=True) if box.select_one(".details") else None)

        teams = []
        for t in box.select("ul.teams > li"):
            name = t.select_one(".name").get_text(strip=True) if t.select_one(".name") else ""
            score_text = t.select_one(".score").get_text(strip=True) if t.select_one(".score") else ""
            score = int(score_text) if score_text.isdigit() else None
            teams.append({
                "name": name,
                "score": score,
                "isWinner": "winner" in t.get("class", []),
                "resultCode": t.get("data-result"),
            })

        if len(teams) >= 2:
            t1, t2 = teams[0], teams[1]
            results.append({
                "state_code": state_code,
                "contest_id": contest_id,
                "page_url": page_url,
                "game_url": game_url,
                "game_date": parse_date_from_url(game_url or page_url),
                "contest_state": contest_state,
                "is_live": is_live,
                "details": details,
                "teams_attr": teams_attr,
                "team1_name": t1["name"],
                "team1_score": t1["score"],
                "team1_is_winner": t1["isWinner"],
                "team1_result_code": t1["resultCode"],
                "team2_name": t2["name"],
                "team2_score": t2["score"],
                "team2_is_winner": t2["isWinner"],
                "team2_result_code": t2["resultCode"],
                "scraped_at": datetime.utcnow().isoformat(),
                "sport": sport.upper(),
            })
    return results


async def chunked_upsert(req_id: str, rows: List[Dict], chunk_size=500) -> int:
    total = 0
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i : i + chunk_size]
        data, count = supabase.table(TABLE).upsert(chunk, on_conflict="contest_id").execute()
        total += count if count else 0
        print(f"[{req_id}] upsert chunk {i}-{i+len(chunk)-1} ok={count}")
    return total


# ---------- Endpoint ----------
@app.post("/scrape")
async def scrape_handler(req: Request):
    req_id = str(uuid.uuid4())
    body = await req.json()

    states = []
    if isinstance(body.get("states"), str):
        states = [s.strip().lower() for s in body["states"].split(",") if s.strip()]
    elif isinstance(body.get("states"), list):
        states = [s.lower() for s in body["states"] if s]
    else:
        states = DEFAULT_STATES

    sport = (body.get("sport") or "football").lower()
    date_override = body.get("date")
    date_str = date_override or today_mdy()

    rows = []
    meta = []

    for i in range(0, len(states), CONCURRENCY):
        batch = states[i : i + CONCURRENCY]
        tasks = []
        for state_code in batch:
            url = build_scores_url(state_code, date_str, sport)
            tasks.append(fetch_with_retry(url, RETRIES, f"{req_id}/{state_code}"))

        pages = await asyncio.gather(*tasks, return_exceptions=True)
        for state_code, page in zip(batch, pages):
            if isinstance(page, Exception):
                meta.append({"state": state_code, "error": str(page)})
                continue
            r = scrape(page, build_scores_url(state_code, date_str, sport), state_code, sport)
            rows.extend(r)
            meta.append({"state": state_code, "count": len(r)})

        if i + CONCURRENCY < len(states):
            await asyncio.sleep(BATCH_PAUSE_MS / 1000)

    if not rows:
        return {"ok": True, "sport": sport, "date": date_str, "meta": meta, "inserted": 0}

    deduped = {r["contest_id"]: r for r in rows}.values()
    inserted = await chunked_upsert(req_id, list(deduped))

    return {
        "ok": True,
        "sport": sport,
        "date": date_str,
        "inserted": inserted,
        "meta": meta,
        "sample": list(deduped)[:2],
    }

