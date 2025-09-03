from supabase import create_client
from config.settings import get_supabase_url, get_supabase_service_role_key, TABLE


# Initialize Supabase client for database operations
def get_supabase_client():
    """Create and return a Supabase client instance"""
    return create_client(get_supabase_url(), get_supabase_service_role_key())


# Remove duplicate entries based on contest_id field
def dedupe_by_contest_id(rows: list[dict]) -> list[dict]:
    """Remove duplicate rows based on contest_id, keeping the first occurrence"""
    seen = set()
    out = []
    for r in rows:
        if not r.get("contest_id"):
            continue
        if r["contest_id"] not in seen:
            seen.add(r["contest_id"])
            out.append(r)
    return out


# Insert or update rows in batches to avoid API limits
async def chunked_upsert(req_id: str, rows: list[dict], chunk_size: int = 500) -> int:
    """Upsert rows to database in chunks, returns total number of rows inserted"""
    supabase = get_supabase_client()
    total = 0
    
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i : i + chunk_size]
        try:
            resp = supabase.table(TABLE).upsert(chunk, on_conflict="contest_id").execute()
            total += len(resp.data or [])
            print(f"[{req_id}] upsert {i}-{i+len(chunk)-1} ok={len(resp.data or [])}")
        except Exception as e:
            print(f"[{req_id}] upsert error: {e}")
            continue
    
    return total