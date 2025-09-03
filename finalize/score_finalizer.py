import os
from database.supabase_client import get_supabase_client, TABLE


# Finalize scores by updating contest states based on score availability
async def finalize_scores(states: list[str], sport: str, req_id: str = None) -> dict:
    """
    Finalize scores by updating contest_state for in-progress games
    - Games with no scores -> 'score-not-reported'  
    - Games with partial/full scores -> 'needs-verification'
    """
    if not req_id:
        req_id = os.urandom(4).hex()
    
    supabase = get_supabase_client()
    
    print(f"[{req_id}] Parsed params -> states={','.join(states)} sport={sport}")
    
    if not states or not sport:
        print(f"[{req_id}] Missing states or sport param")
        return {"error": "states and sport required"}
    
    # Fetch rows that need finalization
    print(f"[{req_id}] Querying rows from {TABLE}...")
    
    try:
        response = supabase.table(TABLE).select(
            "id, state_code, sport, contest_state, team1_score, team2_score"
        ).in_(
            "state_code", states
        ).eq(
            "sport", sport.upper()
        ).neq(
            "contest_state", "boxscore"
        ).neq(
            "contest_state", "pregame" 
        ).execute()
        
        rows = response.data or []
    except Exception as e:
        print(f"[{req_id}] Fetch error: {e}")
        raise Exception(f"Database fetch error: {e}")
    print(f"[{req_id}] Rows fetched: {len(rows)}")
    
    if not rows:
        print(f"[{req_id}] No rows matched criteria")
        return {
            "ok": True,
            "rows": 0,
            "rowsNeedingVerification": 0,
            "rowsMissingScore": 0,
            "rowsSuccessfullyUpdated": 0
        }
    
    # Build updates for contest-in-progress games
    updates = []
    rows_needing_verification = 0
    rows_missing_score = 0
    
    for row in rows:
        if row["contest_state"] == "contest-in-progress":
            new_state = None
            
            # Both scores are null - no score reported
            if row["team1_score"] is None and row["team2_score"] is None:
                new_state = "score-not-reported"
                rows_missing_score += 1
            # At least one score is present - needs verification
            elif row["team1_score"] is not None or row["team2_score"] is not None:
                new_state = "needs-verification"
                rows_needing_verification += 1
            
            if new_state:
                updates.append({
                    "id": row["id"],
                    "contest_state": new_state,
                    "is_live": False,
                    "details": "Final"
                })
                print(f"[{req_id}] Row {row['id']} contest_state updated from contest-in-progress → {new_state}")
    
    print(f"[{req_id}] Total rows needing update: {len(updates)}")
    print(f"[{req_id}] rowsNeedingVerification={rows_needing_verification}, rowsMissingScore={rows_missing_score}")
    
    # Perform upsert if there are updates
    rows_successfully_updated = 0
    if updates:
        try:
            update_response = supabase.table(TABLE).upsert(
                updates, 
                on_conflict="id",
                ignore_duplicates=False
            ).execute()
            
            rows_successfully_updated = len(update_response.data or [])
            print(f"[{req_id}] Upsert successful: {rows_successfully_updated} rows updated")
        except Exception as e:
            print(f"[{req_id}] Upsert error: {e}")
            raise Exception(f"Database update error: {e}")
    
    # Return response
    print(f"[{req_id}] Finalize complete. sport={sport} states={','.join(states)} rows={len(rows)} updated={rows_successfully_updated}")
    
    return {
        "ok": True,
        "sport": sport,
        "states": states,
        "rows": len(rows),
        "rowsNeedingVerification": rows_needing_verification,
        "rowsMissingScore": rows_missing_score,
        "rowsSuccessfullyUpdated": rows_successfully_updated
    }