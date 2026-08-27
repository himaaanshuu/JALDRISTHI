"""
Supabase Client for JAL-DRISHTI.
Provides a unified interface for database operations via Supabase REST API.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from supabase import create_client, Client

logger = logging.getLogger("supabase_client")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_client: Optional[Client] = None
_admin_client: Optional[Client] = None


def get_client() -> Client:
    """Get or create Supabase client singleton (anon key, subject to RLS)."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")
    return _client


def get_admin_client() -> Client:
    """Get or create Supabase admin client (service role key, bypasses RLS)."""
    global _admin_client
    if _admin_client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        _admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        logger.info("Supabase admin client initialized")
    return _admin_client


# ─── Generic CRUD ────────────────────────────────────────────────────────────

def sb_select(table: str, filters: Dict[str, Any] = None, order: str = None,
              limit: int = None, offset: int = None) -> List[Dict]:
    """Select rows from a Supabase table."""
    client = get_client()
    query = client.table(table).select("*")
    if filters:
        for col, val in filters.items():
            if isinstance(val, list) and len(val) == 2:
                query = query.filter(col, val[0], val[1])
            else:
                query = query.eq(col, val)
    if order:
        desc = order.startswith("-")
        col = order.lstrip("-")
        query = query.order(col, desc=desc)
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)
    result = query.execute()
    return result.data or []


def sb_insert(table: str, data: Dict | List[Dict]) -> List[Dict]:
    """Insert rows into a Supabase table."""
    client = get_client()
    result = client.table(table).insert(data).execute()
    return result.data or []


def sb_upsert(table: str, data: Dict | List[Dict], on_conflict: str = None) -> List[Dict]:
    """Upsert rows into a Supabase table."""
    client = get_client()
    query = client.table(table).upsert(data)
    if on_conflict:
        query = query.on_conflict(on_conflict)
    result = query.execute()
    return result.data or []


def sb_update(table: str, data: Dict, filters: Dict[str, Any]) -> List[Dict]:
    """Update rows in a Supabase table."""
    client = get_client()
    query = client.table(table).update(data)
    for col, val in filters.items():
        query = query.eq(col, val)
    result = query.execute()
    return result.data or []


def sb_delete(table: str, filters: Dict[str, Any]) -> List[Dict]:
    """Delete rows from a Supabase table."""
    client = get_client()
    query = client.table(table).delete()
    for col, val in filters.items():
        query = query.eq(col, val)
    result = query.execute()
    return result.data or []


def sb_count(table: str, filters: Dict[str, Any] = None) -> int:
    """Count rows in a Supabase table."""
    client = get_client()
    query = client.table(table).select("*", count="exact")
    if filters:
        for col, val in filters.items():
            query = query.eq(col, val)
    result = query.execute()
    return result.count or 0


def supabase_request(method: str, path: str, json_data: Any = None,
                     params: Dict[str, str] = None, admin: bool = False) -> Any:
    """Make a raw HTTP request to Supabase REST API.
    admin=True uses service_role key (bypasses RLS).
    """
    import requests
    url = f"{SUPABASE_URL}/rest/v1{path}"
    api_key = SUPABASE_SERVICE_ROLE_KEY if admin else SUPABASE_KEY
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=json_data, timeout=10)
        elif method == "PATCH":
            resp = requests.patch(url, headers=headers, json=json_data, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10)
        else:
            return None
        if resp.status_code in (200, 201, 204):
            try:
                return resp.json()
            except Exception:
                return []
        logger.warning(f"Supabase request failed: {resp.status_code} {resp.text[:200]}")
        return None
    except Exception as e:
        logger.error(f"Supabase request error: {e}")
        return None


# ─── Groundwater-Specific Queries ────────────────────────────────────────────

def fetch_state_data(state: str, year: int) -> Optional[Dict]:
    """Fetch aggregated state-level groundwater data."""
    rows = sb_select("groundwater", filters={"state": state, "assessment_year": year})
    if not rows:
        return None

    # Prefer block-level data
    blocks = [r for r in rows if r.get("block")]
    if blocks:
        total_recharge = sum(r.get("annual_groundwater_recharge", 0) or 0 for r in blocks)
        total_extractable = sum(r.get("extractable_groundwater_resource", 0) or 0 for r in blocks)
        total_extraction = sum(r.get("groundwater_extraction", 0) or 0 for r in blocks)
        avg_stage = sum(r.get("extraction_stage", 0) or 0 for r in blocks) / len(blocks)
        districts = set(r.get("district", "") for r in blocks if r.get("district"))
        oe = sum(1 for r in blocks if r.get("category") == "Over-Exploited")
        critical = sum(1 for r in blocks if r.get("category") == "Critical")
        sc = sum(1 for r in blocks if r.get("category") == "Semi-Critical")
        safe = sum(1 for r in blocks if r.get("category") == "Safe")
        return {
            "state": state, "assessment_year": year,
            "total_recharge": round(total_recharge, 2),
            "total_extractable": round(total_extractable, 2),
            "total_extraction": round(total_extraction, 2),
            "avg_stage": round(avg_stage, 2),
            "districts": len(districts), "blocks": len(blocks),
            "oe_blocks": oe, "critical_blocks": critical,
            "sc_blocks": sc, "safe_blocks": safe, "total_blocks": len(blocks),
        }

    # Fall back to state-level aggregate row
    r = rows[0]
    return {
        "state": state, "assessment_year": year,
        "total_recharge": round(r.get("annual_groundwater_recharge", 0) or 0, 2),
        "total_extractable": round(r.get("extractable_groundwater_resource", 0) or 0, 2),
        "total_extraction": round(r.get("groundwater_extraction", 0) or 0, 2),
        "avg_stage": round(r.get("extraction_stage", 0) or 0, 2),
        "districts": 0, "blocks": 0,
        "oe_blocks": 1 if r.get("category") == "Over-Exploited" else 0,
        "critical_blocks": 1 if r.get("category") == "Critical" else 0,
        "sc_blocks": 1 if r.get("category") == "Semi-Critical" else 0,
        "safe_blocks": 1 if r.get("category") == "Safe" else 0,
        "total_blocks": 1,
    }


def fetch_state_latest(state: str) -> Optional[Dict]:
    """Fetch latest available data for a state."""
    rows = sb_select("groundwater", filters={"state": state})
    if not rows:
        return None
    # Try block-level first
    blocks = [r for r in rows if r.get("block")]
    if blocks:
        years = sorted(set(r["assessment_year"] for r in blocks if r.get("assessment_year")), reverse=True)
        if years:
            return fetch_state_data(state, years[0])
    # Fall back to state-level aggregates
    state_rows = [r for r in rows if not r.get("block") and r.get("assessment_year")]
    if not state_rows:
        return None
    latest = max(state_rows, key=lambda r: r.get("assessment_year", 0))
    return {
        "state": state,
        "assessment_year": latest.get("assessment_year"),
        "total_recharge": round(latest.get("annual_groundwater_recharge", 0) or 0, 2),
        "total_extractable": round(latest.get("extractable_groundwater_resource", 0) or 0, 2),
        "total_extraction": round(latest.get("groundwater_extraction", 0) or 0, 2),
        "avg_stage": round(latest.get("extraction_stage", 0) or 0, 2),
        "districts": 0,
        "blocks": 0,
        "oe_blocks": 1 if latest.get("category") == "Over-Exploited" else 0,
        "critical_blocks": 1 if latest.get("category") == "Critical" else 0,
        "sc_blocks": 1 if latest.get("category") == "Semi-Critical" else 0,
        "safe_blocks": 1 if latest.get("category") == "Safe" else 0,
        "total_blocks": 1,
    }


def fetch_state_trend(state: str) -> List[Dict]:
    """Fetch multi-year trend for a state."""
    rows = sb_select("groundwater", filters={"state": state})
    blocks = [r for r in rows if r.get("block")]
    if not blocks:
        return []

    by_year: Dict[int, List] = {}
    for r in blocks:
        yr = r.get("assessment_year")
        if yr:
            by_year.setdefault(yr, []).append(r)

    trend = []
    for yr in sorted(by_year.keys()):
        year_blocks = by_year[yr]
        trend.append({
            "assessment_year": yr,
            "total_extraction": round(sum(r.get("groundwater_extraction", 0) or 0 for r in year_blocks), 2),
            "avg_stage": round(sum(r.get("extraction_stage", 0) or 0 for r in year_blocks) / len(year_blocks), 2),
            "total_recharge": round(sum(r.get("annual_groundwater_recharge", 0) or 0 for r in year_blocks), 2),
            "blocks_assessed": len(year_blocks),
        })
    return trend


def fetch_rankings(limit: int = 10) -> List[Dict]:
    """Fetch state-level rankings by extraction stage."""
    rows = sb_select("groundwater")
    blocks = [r for r in rows if r.get("block")]
    if not blocks:
        return []

    by_state: Dict[str, List] = {}
    for r in blocks:
        s = r.get("state", "")
        if s:
            by_state.setdefault(s, []).append(r)

    rankings = []
    for state, state_blocks in by_state.items():
        avg_stage = sum(r.get("extraction_stage", 0) or 0 for r in state_blocks) / len(state_blocks)
        rankings.append({
            "state": state,
            "avg_stage": round(avg_stage, 2),
            "total_extraction": round(sum(r.get("groundwater_extraction", 0) or 0 for r in state_blocks), 2),
            "total_recharge": round(sum(r.get("annual_groundwater_recharge", 0) or 0 for r in state_blocks), 2),
            "blocks": len(state_blocks),
        })

    rankings.sort(key=lambda x: x["avg_stage"], reverse=True)
    return rankings[:limit]


def fetch_district_data(state: str) -> List[Dict]:
    """Fetch district-level aggregated data for a state."""
    rows = sb_select("groundwater", filters={"state": state})
    blocks = [r for r in rows if r.get("block")]
    if not blocks:
        return []

    by_dist: Dict[str, List] = {}
    for r in blocks:
        d = r.get("district", "")
        if d:
            by_dist.setdefault(d, []).append(r)

    districts = []
    for dist, dist_blocks in by_dist.items():
        avg_stage = sum(r.get("extraction_stage", 0) or 0 for r in dist_blocks) / len(dist_blocks)
        districts.append({
            "district": dist,
            "avg_stage": round(avg_stage, 2),
            "total_extraction": round(sum(r.get("groundwater_extraction", 0) or 0 for r in dist_blocks), 2),
            "blocks": len(dist_blocks),
            "year": max(r.get("assessment_year", 0) or 0 for r in dist_blocks),
        })
    districts.sort(key=lambda x: x["avg_stage"], reverse=True)
    return districts


def fetch_block_data(state: str, district: str = None) -> List[Dict]:
    """Fetch block-level data."""
    filters = {"state": state}
    rows = sb_select("groundwater", filters=filters)
    blocks = [r for r in rows if r.get("block")]
    if district:
        blocks = [r for r in blocks if r.get("district") == district]
    return blocks


def fetch_overall_stats() -> Dict:
    """Fetch national-level overview."""
    rows = sb_select("groundwater")
    blocks = [r for r in rows if r.get("block")]
    state_rows = [r for r in rows if not r.get("block")]

    # Use block-level data for detailed stats if available
    if blocks:
        states = set(r.get("state", "") for r in blocks if r.get("state"))
        districts = set(r.get("district", "") for r in blocks if r.get("district"))
        return {
            "total_extraction": round(sum(r.get("groundwater_extraction", 0) or 0 for r in blocks), 2),
            "total_recharge": round(sum(r.get("annual_groundwater_recharge", 0) or 0 for r in blocks), 2),
            "avg_stage": round(sum(r.get("extraction_stage", 0) or 0 for r in blocks) / len(blocks), 2),
            "states": len(states), "districts": len(districts), "blocks": len(blocks),
            "total_records": len(blocks),
            "oe_blocks": sum(1 for r in blocks if r.get("category") == "Over-Exploited"),
            "critical_blocks": sum(1 for r in blocks if r.get("category") == "Critical"),
            "sc_blocks": sum(1 for r in blocks if r.get("category") == "Semi-Critical"),
            "safe_blocks": sum(1 for r in blocks if r.get("category") == "Safe"),
        }

    # Fall back to state-level aggregates
    all_states = set(r.get("state", "") for r in state_rows if r.get("state"))
    return {
        "total_extraction": round(sum(r.get("groundwater_extraction", 0) or 0 for r in state_rows), 2),
        "total_recharge": round(sum(r.get("annual_groundwater_recharge", 0) or 0 for r in state_rows), 2),
        "avg_stage": round(sum(r.get("extraction_stage", 0) or 0 for r in state_rows) / max(len(state_rows), 1), 2),
        "states": len(all_states), "districts": 0, "blocks": 0,
        "total_records": len(state_rows),
        "oe_blocks": sum(1 for r in state_rows if r.get("category") == "Over-Exploited"),
        "critical_blocks": sum(1 for r in state_rows if r.get("category") == "Critical"),
        "sc_blocks": sum(1 for r in state_rows if r.get("category") == "Semi-Critical"),
        "safe_blocks": sum(1 for r in state_rows if r.get("category") == "Safe"),
    }


def fetch_category_distribution(state: str = None) -> Dict:
    """Fetch category distribution."""
    filters = {"state": state} if state else None
    rows = sb_select("groundwater", filters=filters)
    blocks = [r for r in rows if r.get("block")]
    counts = {}
    for r in blocks:
        cat = r.get("category", "Unknown")
        counts[cat] = counts.get(cat, 0) + 1
    total = sum(counts.values())
    return {
        "total": total,
        "categories": {c: {"count": n, "percentage": round(n / total * 100, 1)} for c, n in counts.items()} if total > 0 else {}
    }


def fetch_what_changed(state: str, year1: int, year2: int) -> List[Dict]:
    """Fetch block-level changes between two years."""
    rows = sb_select("groundwater", filters={"state": state})
    blocks = [r for r in rows if r.get("block")]

    by_key: Dict[tuple, Dict[int, Dict]] = {}
    for r in blocks:
        key = (r.get("block", ""), r.get("district", ""))
        yr = r.get("assessment_year")
        if yr in (year1, year2):
            by_key.setdefault(key, {})[yr] = r

    changes = []
    for key, years in by_key.items():
        r1 = years.get(year1)
        r2 = years.get(year2)
        if r1 and r2:
            changes.append({
                "block": key[0],
                "district": key[1],
                "stage_y1": r1.get("extraction_stage", 0),
                "stage_y2": r2.get("extraction_stage", 0),
                "cat_y1": r1.get("category", ""),
                "cat_y2": r2.get("category", ""),
                "ext_y1": r1.get("groundwater_extraction", 0),
                "ext_y2": r2.get("groundwater_extraction", 0),
            })
    return changes


def fetch_all_assessments(state: str = None, district: str = None,
                          block: str = None, year: int = None,
                          category: str = None, limit: int = 200) -> List[Dict]:
    """Fetch assessment records with optional filters."""
    filters = {}
    if state:
        filters["state"] = state
    rows = sb_select("groundwater", filters=filters, limit=min(limit, 1000))
    results = rows
    if district:
        results = [r for r in results if r.get("district") == district]
    if block:
        results = [r for r in results if r.get("block") == block]
    if year:
        results = [r for r in results if r.get("assessment_year") == year]
    if category:
        results = [r for r in results if r.get("category") == category]
    return results[:limit]
