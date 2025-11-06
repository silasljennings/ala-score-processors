from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.data_helpers import clean_team_name
from utils.url_helpers import parse_date_from_url, parse_compound_sport


# Parse HTML and extract game data from MaxPreps scores page
def scrape(html: str, page_url: str, state_code: str, sport: str) -> list[dict]:
    """Parse MaxPreps HTML and extract game scores and metadata"""
    # Parse gender information from sport name
    base_sport, gender_suffix = parse_compound_sport(sport)
    # Convert gender suffix to database format
    gender = "Female" if gender_suffix == "girls" else "Male"
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
        game_url = urljoin(page_url, game_href) if game_href else None

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
                    "sport": base_sport.upper(),
                    "gender": gender,
                }
            )
    return out