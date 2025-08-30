# main.py
import os
import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from supabase import create_client

# ---------- Supabase ----------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
TABLE = "ala_max_prep_scores"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ---------- Config ----------
STATES_ENV = [
    s.strip().lower()
    for s in (os.environ.get("STATES") or "al").split(",")
    if s.strip()
]
CONCURRENCY = int(os.environ.get("SCRAPE_CONCURRENCY") or 2)
BATCH_PAUSE_MS = int(os.environ.get("SCRAPE_BATCH_PAUSE_MS") or 150)
RETRIES = int(os.environ.get("SCRAPE_RETRIES") or 2)

# ---------- Time helpers ----------
from datetime import datetime
import pytz

NY_TZ = pytz.timezone("America/New_York")


def now_in_ny():
    return datetime.now(NY_TZ)


def today_mdy_ny():
    d = now_in_ny()
    return f"{d.month}/{d.day}/{d.year}"


def within_run_window_ny():
    d = now_in_ny()
    dow = d.weekday()  # 0=Mon, 3=Thu
    hr = d.hour
    return (dow in [3, 4, 5]) and 18 <= hr <= 23


# ---------- URL builders & parsing ----------
def build_scores_url(state_code: str, mdy: str, sport: str) -> str:
    return f"https://www.maxpreps.com/{state_code}/{sport.lower()}/scores/?date={httpx.QueryParams({'date': mdy})}"


def parse_date_from_url(u: str | None) -> str | None:
    if not u:
        return None
    try:
        # ?date=mm/dd/yyyy
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(u)
        q = parse_qs(parsed.query).get("date", [None])[0]
        if q:
            m, d, y = q.split("/")
            return f"{y}-{int(m):02d}-{int(d):02d}"
    except Exception:
        pass
    return None


# ---------- Helpers ----------
def clean_team_name(raw: str = "") -> str:
    import re

    return re.sub(r"\(\s*#?\d+\s*\)\s*", "", raw).strip()


def to_mdy(input_str: str | None) -> str | None:
    if not input_str:
        return None
    import re

    mdy = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", input_str)
    if mdy:
        return f"{int(mdy[1])}/{int(mdy[2])}/{mdy[3]}"
    iso = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", input_str)
    if iso:
        return f"{int(iso[2])}/{int(iso[3])}/{iso[1]}"
    return None


# ---------- Scraper ----------
def scrape(html: str, page_url: str, state_code: str, sport: str):
    doc = BeautifulSoup(html, "html.parser")
    boxes = doc.select("li.c .contest-box-item")
    out = []

    for box in boxes:
        li = box.find_parent("li")
        contest_id = li.get("data-contest-id") if li else None
        if not contest_id:
            continue

        teams_attr = li.get("data-teams")
        a = box.select_one("a.c-c")
        game_href = a.get("href") if a else None
        game_url = urljoin(page_url, game_href) if game_href else None  # ✅ FIXED

        contest_state = box.get("data-contest-state")
        is_live = box.get("data-contest-live") == "1"
        details = (box.select_one(".details").get_text(strip=True)) if box.select_one(".details") else None

        team_lis = box.select("ul.teams > li")
        teams = []
        for t in team_lis:
            name = clean_team_name(t.select_one(".name").get_text(strip=True))
            score_txt = t.select_one(".score").get_text(strip=True) if t.select_one(".score") else ""
            score = int(score_txt) if score_txt.isdigit() else None
            class_attr = (t.get("class") or [])
            if isinstance(class_attr, str):
                class_attr = class_attr.split()
            teams.append(
                {
                    "name": name,
                    "score": score,
                    "isWinner": "winner" in class_attr,
                    "resultCode": t.get("data-result"),
                }
            )

        if len(teams) >= 2:
            t1, t2 = teams[:2]
            out.append(
                {
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
                }
            )
    return out


# ---------- polite fetch ----------
async def sleep(ms: int):
    await asyncio.sleep(ms / 1000)


async def fetch_with_retry(url: str, retries: int = RETRIES, ctx: str = ""):
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


async def fetch_state_page(url, ctx):
    await sleep(int(200 * (0.5)))
    res = await fetch_with_retry(url, RETRIES, ctx)
    return res.text


# ---------- dedupe + upsert ----------
def dedupe_by_contest_id(rows):
    seen = set()
    out = []
    for r in rows:
        if not r.get("contest_id"):
            continue
        if r["contest_id"] not in seen:
            seen.add(r["contest_id"])
            out.append(r)
    return out


async def chunked_upsert(req_id, rows, chunk_size=500):
    total = 0
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i : i + chunk_size]
        resp = supabase.table(TABLE).upsert(chunk, on_conflict="contest_id").execute()
        if getattr(resp, "error", None):
            print(f"[{req_id}] upsert error: {resp.error}")
            continue
        total += len(resp.data or [])
        print(f"[{req_id}] upsert {i}-{i+len(chunk)-1} ok={len(resp.data or [])}")
    return total


# ---------- FastAPI App ----------
app = FastAPI()


@app.post("/scrape")
async def scrape_handler(request: Request):
    req_id = os.urandom(4).hex()
    try:
        body = await request.json()
    except Exception:
        body = {}

    states = []
    if isinstance(body.get("states"), str) and body["states"]:
        states = [s.strip().lower() for s in body["states"].split(",") if s.strip()]
    elif isinstance(body.get("states"), list) and body["states"]:
        states = [str(s).lower() for s in body["states"]]
    else:
        states = STATES_ENV

    sport = (
        body.get("sport")
        or request.query_params.get("sport")
        or os.environ.get("SPORT")
        or "football"
    ).lower()

    date_override = body.get("date") or request.query_params.get("date")
    date_override_mdy = to_mdy(date_override) if date_override else None
    force = body.get("force") or request.query_params.get("force") == "1" or bool(
        date_override_mdy
    )

    if not within_run_window_ny() and not force:
        return JSONResponse({"ok": True, "skipped": "outside window"})

    date_str = date_override_mdy or today_mdy_ny()

    rows, meta = [], []

    for i in range(0, len(states), CONCURRENCY):
        batch = states[i : i + CONCURRENCY]
        tasks = []
        for idx, state_code in enumerate(batch):
            await sleep(idx * 15)
            url = build_scores_url(state_code, date_str, sport)
            tasks.append(fetch_state_page(url, f"{req_id}/{state_code}"))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for state_code, html in zip(batch, results):
            if isinstance(html, Exception):
                meta.append({"state_code": state_code, "error": str(html)})
            else:
                r = scrape(html, build_scores_url(state_code, date_str, sport), state_code, sport)
                rows.extend(r)
                meta.append({"state_code": state_code, "count": len(r)})

        if i + CONCURRENCY < len(states):
            await sleep(BATCH_PAUSE_MS)

    if not rows:
        return JSONResponse(
            {"ok": True, "sport": sport, "date": date_str, "meta": meta, "inserted": 0}
        )

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

