"""
Smart Chat Pipeline for Groundwater Intelligence.
Routes queries to SQL (for numbers) or RAG (for knowledge), aggregates context, and generates professional responses.
"""

import json
import os
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from geo_resolver import resolve_location, resolve_state, get_all_states
from query_router import classify_query, QueryType, QueryRoute, ClassifiedQuery
from numeric_calc import (
    compute_state_comparison, compute_trend, compute_rankings,
    compute_category_distribution, compute_risk_score, format_number,
    percentage_change, absolute_change
)
from config import (
    DB_PATH, OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT,
    OLLAMA_NUM_CTX, OLLAMA_NUM_PREDICT, OLLAMA_TEMPERATURE,
    RAG_TOP_K, SYSTEM_PROMPT_EN, SYSTEM_PROMPT_HI,
    LATEST_ASSESSMENT_YEAR, ASSESSMENT_YEARS, USE_SUPABASE
)


# ─── Conversation State ──────────────────────────────────────────────────────

@dataclass
class ConversationState:
    session_id: str
    last_state: Optional[str] = None
    last_district: Optional[str] = None
    last_block: Optional[str] = None
    history: List[Dict[str, str]] = field(default_factory=list)

    def update(self, entities: Dict[str, Optional[str]], user_msg: str, assistant_msg: str):
        if entities.get("state"):
            self.last_state = entities["state"]
        if entities.get("district"):
            self.last_district = entities["district"]
        if entities.get("block"):
            self.last_block = entities["block"]
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        if len(self.history) > 20:
            self.history = self.history[-20:]


# Session store
_sessions: Dict[str, ConversationState] = {}


def get_session(session_id: str) -> ConversationState:
    if session_id not in _sessions:
        _sessions[session_id] = ConversationState(session_id=session_id)
    return _sessions[session_id]


# ─── SQL Data Retrieval ─────────────────────────────────────────────────────

def _get_sb():
    from supabase_client import (
        fetch_state_data, fetch_state_latest, fetch_state_trend,
        fetch_rankings, fetch_district_data, fetch_block_data,
        fetch_overall_stats, fetch_category_distribution, fetch_what_changed
    )
    return {
        "fetch_state_data": fetch_state_data,
        "fetch_state_latest": fetch_state_latest,
        "fetch_state_trend": fetch_state_trend,
        "fetch_rankings": fetch_rankings,
        "fetch_district_data": fetch_district_data,
        "fetch_block_data": fetch_block_data,
        "fetch_overall_stats": fetch_overall_stats,
        "fetch_category_distribution": fetch_category_distribution,
        "fetch_what_changed": fetch_what_changed,
    }


def _fetch_state_data(state: str, year: int = LATEST_ASSESSMENT_YEAR) -> Optional[Dict]:
    """Fetch state-level aggregated data."""
    if USE_SUPABASE:
        from supabase_client import fetch_state_data
        return fetch_state_data(state, year)
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT state, assessment_year,
            ROUND(SUM(annual_groundwater_recharge), 2) as total_recharge,
            ROUND(SUM(extractable_groundwater_resource), 2) as total_extractable,
            ROUND(SUM(groundwater_extraction), 2) as total_extraction,
            ROUND(AVG(extraction_stage), 2) as avg_stage,
            COUNT(DISTINCT district) as districts,
            COUNT(DISTINCT block) as blocks,
            SUM(CASE WHEN category='Over-Exploited' THEN 1 ELSE 0 END) as oe_blocks,
            SUM(CASE WHEN category='Critical' THEN 1 ELSE 0 END) as critical_blocks,
            SUM(CASE WHEN category='Semi-Critical' THEN 1 ELSE 0 END) as sc_blocks,
            SUM(CASE WHEN category='Safe' THEN 1 ELSE 0 END) as safe_blocks,
            COUNT(*) as total_blocks
        FROM groundwater
        WHERE state = ? AND assessment_year = ? AND block != ''
        GROUP BY state, assessment_year
    """, (state, year))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def _fetch_state_latest(state: str) -> Optional[Dict]:
    """Fetch latest available data for a state."""
    if USE_SUPABASE:
        from supabase_client import fetch_state_latest
        return fetch_state_latest(state)
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT assessment_year FROM groundwater
        WHERE state = ? AND block != ''
        ORDER BY assessment_year DESC LIMIT 1
    """, (state,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    year = row[0]
    conn.close()
    return _fetch_state_data(state, year)


def _fetch_state_comparison(state_a: str, state_b: str, year: int = LATEST_ASSESSMENT_YEAR) -> Dict:
    """Fetch data for two states and compute comparison."""
    data_a = _fetch_state_data(state_a, year)
    data_b = _fetch_state_data(state_b, year)
    if not data_a or not data_b:
        return {"error": "Data not available for one or both states"}

    def map_data(d):
        return {
            "annual_groundwater_recharge": d.get("total_recharge", 0),
            "extractable_groundwater_resource": d.get("total_extractable", 0),
            "groundwater_extraction": d.get("total_extraction", 0),
            "extraction_stage": d.get("avg_stage", 0),
            "assessment_year": d.get("assessment_year", year),
        }

    return compute_state_comparison(map_data(data_a), state_a, map_data(data_b), state_b)


def _fetch_state_trend(state: str) -> Optional[Dict]:
    """Fetch multi-year trend for a state."""
    if USE_SUPABASE:
        from supabase_client import fetch_state_trend
        rows = fetch_state_trend(state)
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT assessment_year,
                ROUND(SUM(groundwater_extraction), 2) as total_extraction,
                ROUND(AVG(extraction_stage), 2) as avg_stage,
                ROUND(SUM(annual_groundwater_recharge), 2) as total_recharge,
                COUNT(DISTINCT block) as blocks_assessed
            FROM groundwater
            WHERE state = ? AND block != ''
            GROUP BY assessment_year
            ORDER BY assessment_year
        """, (state,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
    if len(rows) < 2:
        return None
    return compute_trend(state, "avg_stage", "%", rows)


def _fetch_rankings(metric: str = "extraction_stage", limit: int = 10, state: str = None) -> List[Dict]:
    """Fetch state-level rankings."""
    if USE_SUPABASE:
        from supabase_client import fetch_rankings
        return fetch_rankings(limit)
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    where = "WHERE block != ''"
    params = []
    if state:
        where += " AND state = ?"
        params.append(state)
    c.execute(f"""
        SELECT state,
            ROUND(AVG(extraction_stage), 2) as avg_stage,
            ROUND(SUM(groundwater_extraction), 2) as total_extraction,
            ROUND(SUM(annual_groundwater_recharge), 2) as total_recharge,
            COUNT(DISTINCT block) as blocks
        FROM groundwater
        {where}
        GROUP BY state
        ORDER BY avg_stage DESC
        LIMIT ?
    """, params + [limit])
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def _fetch_district_data(state: str, district: str = None) -> List[Dict]:
    """Fetch district-level data for a state."""
    if USE_SUPABASE:
        from supabase_client import fetch_district_data, fetch_block_data
        if district:
            return fetch_block_data(state, district)
        return fetch_district_data(state)
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if district:
        c.execute("""
            SELECT district, block, extraction_stage, category,
                groundwater_extraction, annual_groundwater_recharge, assessment_year
            FROM groundwater
            WHERE state = ? AND district = ? AND block != ''
            ORDER BY extraction_stage DESC
        """, (state, district))
    else:
        c.execute("""
            SELECT district,
                ROUND(AVG(extraction_stage), 2) as avg_stage,
                ROUND(SUM(groundwater_extraction), 2) as total_extraction,
                COUNT(DISTINCT block) as blocks,
                MAX(assessment_year) as year
            FROM groundwater
            WHERE state = ? AND block != ''
            GROUP BY district
            ORDER BY avg_stage DESC
        """, (state,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def _fetch_block_data(state: str, district: str = None, block: str = None) -> List[Dict]:
    """Fetch block-level data."""
    if USE_SUPABASE:
        from supabase_client import fetch_block_data
        return fetch_block_data(state, district)
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    conditions = ["state = ?", "block != ''"]
    params = [state]
    if district:
        conditions.append("district = ?")
        params.append(district)
    if block:
        conditions.append("block = ?")
        params.append(block)
    where = " AND ".join(conditions)
    c.execute(f"""
        SELECT block, district, state, extraction_stage, category,
            groundwater_extraction, annual_groundwater_recharge,
            extractable_groundwater_resource, assessment_year,
            latitude, longitude
        FROM groundwater
        WHERE {where}
        ORDER BY extraction_stage DESC
    """, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def _fetch_category_distribution(state: str = None) -> Dict:
    """Fetch category distribution."""
    if USE_SUPABASE:
        from supabase_client import fetch_category_distribution
        return fetch_category_distribution(state)
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if state:
        c.execute("""
            SELECT category, COUNT(*) as count
            FROM groundwater WHERE state = ? AND block != ''
            GROUP BY category
        """, (state,))
    else:
        c.execute("""
            SELECT category, COUNT(*) as count
            FROM groundwater WHERE block != ''
            GROUP BY category
        """)
    rows = c.fetchall()
    conn.close()
    total = sum(r[1] for r in rows)
    return {
        "total": total,
        "categories": {r[0]: {"count": r[1], "percentage": round(r[1]/total*100, 1)} for r in rows} if total > 0 else {}
    }


def _fetch_overall_stats() -> Dict:
    """Fetch national-level overview."""
    if USE_SUPABASE:
        from supabase_client import fetch_overall_stats
        return fetch_overall_stats()
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT
            ROUND(SUM(groundwater_extraction), 2) as total_extraction,
            ROUND(SUM(annual_groundwater_recharge), 2) as total_recharge,
            ROUND(AVG(extraction_stage), 2) as avg_stage,
            COUNT(DISTINCT state) as states,
            COUNT(DISTINCT district) as districts,
            COUNT(DISTINCT block) as blocks,
            COUNT(*) as total_records,
            SUM(CASE WHEN category='Over-Exploited' THEN 1 ELSE 0 END) as oe_blocks,
            SUM(CASE WHEN category='Critical' THEN 1 ELSE 0 END) as critical_blocks,
            SUM(CASE WHEN category='Semi-Critical' THEN 1 ELSE 0 END) as sc_blocks,
            SUM(CASE WHEN category='Safe' THEN 1 ELSE 0 END) as safe_blocks
        FROM groundwater WHERE block != ''
    """)
    row = dict(c.fetchone())
    conn.close()
    return row


def _fetch_what_changed(state: str, year1: int, year2: int) -> Dict:
    """Compare two years for a state."""
    if USE_SUPABASE:
        from supabase_client import fetch_what_changed
        rows = fetch_what_changed(state, year1, year2)
        improvements = deteriorations = unchanged = 0
        for r in rows:
            delta = (r.get("stage_y2") or 0) - (r.get("stage_y1") or 0)
            if delta < -2:
                improvements += 1
            elif delta > 2:
                deteriorations += 1
            else:
                unchanged += 1
        avg_y1 = sum(r.get("stage_y1") or 0 for r in rows) / max(len(rows), 1)
        avg_y2 = sum(r.get("stage_y2") or 0 for r in rows) / max(len(rows), 1)
        return {
            "state": state, "year1": year1, "year2": year2,
            "total_blocks": len(rows),
            "avg_stage_y1": round(avg_y1, 2),
            "avg_stage_y2": round(avg_y2, 2),
            "stage_change": round(absolute_change(avg_y1, avg_y2), 2),
            "pct_change": round(percentage_change(avg_y1, avg_y2), 2),
            "improvements": improvements,
            "deteriorations": deteriorations,
            "unchanged": unchanged,
            "overall_trend": "improving" if avg_y2 < avg_y1 else "deteriorating" if avg_y2 > avg_y1 else "stable",
        }
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT block, district,
            MAX(CASE WHEN assessment_year=? THEN extraction_stage END) as stage_y1,
            MAX(CASE WHEN assessment_year=? THEN extraction_stage END) as stage_y2,
            MAX(CASE WHEN assessment_year=? THEN category END) as cat_y1,
            MAX(CASE WHEN assessment_year=? THEN category END) as cat_y2,
            MAX(CASE WHEN assessment_year=? THEN groundwater_extraction END) as ext_y1,
            MAX(CASE WHEN assessment_year=? THEN groundwater_extraction END) as ext_y2
        FROM groundwater
        WHERE state = ? AND block != ''
        GROUP BY block, district
        HAVING stage_y1 IS NOT NULL AND stage_y2 IS NOT NULL
    """, (year1, year2, year1, year2, year1, year2, state))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    improvements = deteriorations = unchanged = 0
    for r in rows:
        delta = (r["stage_y2"] or 0) - (r["stage_y1"] or 0)
        if delta < -2:
            improvements += 1
        elif delta > 2:
            deteriorations += 1
        else:
            unchanged += 1

    avg_y1 = sum(r["stage_y1"] or 0 for r in rows) / max(len(rows), 1)
    avg_y2 = sum(r["stage_y2"] or 0 for r in rows) / max(len(rows), 1)

    return {
        "state": state, "year1": year1, "year2": year2,
        "total_blocks": len(rows),
        "avg_stage_y1": round(avg_y1, 2),
        "avg_stage_y2": round(avg_y2, 2),
        "stage_change": round(absolute_change(avg_y1, avg_y2), 2),
        "pct_change": round(percentage_change(avg_y1, avg_y2), 2),
        "improvements": improvements,
        "deteriorations": deteriorations,
        "unchanged": unchanged,
        "overall_trend": "improving" if avg_y2 < avg_y1 else "deteriorating" if avg_y2 > avg_y1 else "stable",
    }


# ─── Context Aggregation ─────────────────────────────────────────────────────

def _build_sql_context(query_type: QueryType, entities: Dict, classified: ClassifiedQuery) -> str:
    """Build structured context from SQL data."""
    parts = []
    state = entities.get("state")
    district = entities.get("district")
    block = entities.get("block")

    if query_type == QueryType.GREETING:
        return ""

    if query_type == QueryType.COMPARISON:
        # Need two states from the query
        from parser import KNOWN_STATES
        msg = classified.entities.get("raw_message", "").lower() if hasattr(classified.entities, "get") else ""
        mentioned = [s for s in KNOWN_STATES if s.lower() in msg]
        if len(mentioned) >= 2:
            comp = _fetch_state_comparison(mentioned[0], mentioned[1])
            if "comparisons" in comp:
                parts.append(f"Comparison between {comp['state_a']} and {comp['state_b']}:")
                for c in comp["comparisons"]:
                    parts.append(f"  {c['metric']}: {comp['state_a']}={c[comp['state_a']]:,.1f} {c['unit']}, "
                               f"{comp['state_b']}={c[comp['state_b']]:,.1f} {c['unit']}, "
                               f"difference={c['difference']:,.1f} {c['unit']} ({c['percentage_change']:+.1f}%)")
        elif state:
            trend = _fetch_state_trend(state)
            if trend:
                parts.append(f"{state} trend: direction={trend.direction}, "
                           f"change={trend.total_change:.1f}% ({trend.percentage_change:+.1f}%)")
        if not parts:
            return ""

    elif query_type == QueryType.RANKING:
        rankings = _fetch_rankings(limit=10, state=state)
        if rankings:
            parts.append("State-level groundwater extraction rankings (by stage of extraction):")
            for i, r in enumerate(rankings, 1):
                parts.append(f"  {i}. {r['state']}: {r['avg_stage']:.1f}% stage, "
                           f"{r['total_extraction']:,.0f} MCM extraction")

    elif query_type == QueryType.TREND and state:
        trend = _fetch_state_trend(state)
        if trend:
            parts.append(f"{state} groundwater trend ({trend.metric}):")
            parts.append(f"  Direction: {trend.direction}")
            parts.append(f"  Total change: {trend.total_change:+.1f} {trend.unit}")
            parts.append(f"  Percentage change: {trend.percentage_change:+.1f}%")
            parts.append(f"  Avg annual change: {trend.avg_annual_change:+.2f} {trend.unit}/year")
            parts.append(f"  Data points: {', '.join(f'{p.year}={p.value:.1f}' for p in trend.points)}")

    elif query_type == QueryType.CATEGORY:
        dist = _fetch_category_distribution(state)
        parts.append(f"Category distribution{' for ' + state if state else ''}:")
        parts.append(f"  Total blocks assessed: {dist['total']}")
        for cat, info in dist.get("categories", {}).items():
            parts.append(f"  {cat}: {info['count']} blocks ({info['percentage']}%)")

    elif query_type in (QueryType.STATE_STATUS, QueryType.EXTRACTION, QueryType.RECHARGE):
        if state:
            data = _fetch_state_latest(state)
            if data:
                parts.append(f"{state} groundwater status (Assessment Year: {data['assessment_year']}):")
                parts.append(f"  Total Annual Recharge: {data['total_recharge']:,.2f} MCM")
                parts.append(f"  Extractable Resource: {data['total_extractable']:,.2f} MCM")
                parts.append(f"  Groundwater Extraction: {data['total_extraction']:,.2f} MCM")
                parts.append(f"  Stage of Extraction: {data['avg_stage']:.2f}%")
                parts.append(f"  Districts: {data['districts']}, Blocks assessed: {data['blocks']}")
                parts.append(f"  Safe: {data['safe_blocks']}, Semi-Critical: {data['sc_blocks']}, "
                           f"Critical: {data['critical_blocks']}, Over-Exploited: {data['oe_blocks']}")
            else:
                parts.append(f"No data found for {state}.")
        else:
            overview = _fetch_overall_stats()
            parts.append(f"India Groundwater Overview (latest assessment):")
            parts.append(f"  Total Extraction: {overview['total_extraction']:,.2f} MCM")
            parts.append(f"  Total Recharge: {overview['total_recharge']:,.2f} MCM")
            parts.append(f"  Average Stage: {overview['avg_stage']:.2f}%")
            parts.append(f"  States: {overview['states']}, Districts: {overview['districts']}, Blocks: {overview['blocks']}")
            parts.append(f"  Safe: {overview['safe_blocks']}, Over-Exploited: {overview['oe_blocks']}")

    elif query_type == QueryType.DISTRICT_STATUS and state:
        districts = _fetch_district_data(state, district)
        if districts:
            parts.append(f"District data for {state}{' - ' + district if district else ''}:")
            for d in districts[:15]:
                if "avg_stage" in d:
                    parts.append(f"  {d['district']}: {d['avg_stage']:.1f}% stage, "
                               f"{d['total_extraction']:,.0f} MCM, {d['blocks']} blocks ({d.get('year', 'N/A')})")
                else:
                    parts.append(f"  {d['block']},{d['district']}: {d['extraction_stage']:.1f}% {d['category']}")

    elif query_type == QueryType.BLOCK_STATUS and state:
        blocks = _fetch_block_data(state, district, block)
        if blocks:
            parts.append(f"Block data{' for ' + state if state else ''}:")
            for b in blocks[:10]:
                parts.append(f"  {b['block']},{b['district']}: {b['extraction_stage']:.1f}% {b['category']}, "
                           f"{b['groundwater_extraction']:,.0f} MCM ({b['assessment_year']})")

    elif query_type == QueryType.QUALITY:
        parts.append("Groundwater quality data is available through official CGWB monitoring stations.")
        parts.append("Key parameters: Fluoride, Arsenic, Nitrate, Iron, TDS, pH, Chloride.")
        if state:
            parts.append(f"Quality assessment for {state} is part of the CGWB annual monitoring program.")

    elif query_type == QueryType.LEVEL:
        parts.append("Groundwater level data is monitored through CGWB observation wells.")
        parts.append("Pre-monsoon (May-June): maximum depletion. Post-monsoon (Oct-Nov): recharge period.")
        if state:
            parts.append(f"Level monitoring stations exist across {state}.")

    elif query_type == QueryType.RECOMMENDATION:
        if state:
            data = _fetch_state_latest(state)
            if data:
                stage = data["avg_stage"]
                parts.append(f"Management context for {state}:")
                parts.append(f"  Current extraction stage: {stage:.1f}%")
                if stage > 100:
                    parts.append("  Status: Over-exploited. Immediate demand management needed.")
                    parts.append("  Recommendations: Crop diversification, micro-irrigation, "
                               "borewell regulation, rainwater harvesting, community management.")
                elif stage > 90:
                    parts.append("  Status: Critical. Strong interventions required.")
                    parts.append("  Recommendations: Strict extraction limits, artificial recharge, "
                               "crop switching, water pricing.")
                elif stage > 70:
                    parts.append("  Status: Semi-Critical. Preventive measures needed.")
                    parts.append("  Recommendations: Monitor closely, promote efficient irrigation, "
                               "recharge structures.")
                else:
                    parts.append("  Status: Safe. Maintain current management.")
                    parts.append("  Recommendations: Continue monitoring, protect recharge zones.")

    elif query_type == QueryType.REGULATORY:
        parts.append("Groundwater regulation in India:")
        parts.append("  - Model Groundwater Act 2017 (template for states)")
        parts.append("  - CGWA manages NOC for industrial abstraction in over-exploited areas")
        parts.append("  - State-specific groundwater acts and rules")
        parts.append("  - Borewell registration mandates in several states")
        parts.append("  - Atal Bhujal Yojana: community-led management incentive program")

    return "\n".join(parts)


def _build_rag_context(query: str) -> str:
    """Retrieve relevant knowledge from RAG engine."""
    try:
        from rag import get_rag_engine
        engine = get_rag_engine()
        results = engine.retrieve(query, top_k=RAG_TOP_K)
        if not results:
            return ""
        context_parts = []
        for r in results:
            context_parts.append(f"[{r['topic']}] {r['content']}")
        return "\n\n".join(context_parts)
    except Exception:
        return ""


# ─── LLM Generation ──────────────────────────────────────────────────────────

def _call_llm(system_prompt: str, user_context: str, query: str, language: str) -> str:
    """Call Ollama LLM for response generation."""
    user_msg = f"{user_context}\n\nUser Question: {query}\n\nProvide a professional, concise response:"
    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": user_msg,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": OLLAMA_TEMPERATURE,
                "top_p": 0.85,
                "num_ctx": OLLAMA_NUM_CTX,
                "num_predict": OLLAMA_NUM_PREDICT,
            },
        }, timeout=OLLAMA_TIMEOUT)
        resp.raise_for_status()
        return resp.json().get("response", "")
    except requests.exceptions.ConnectionError:
        return "The intelligent analysis service is currently unavailable. Please try again shortly."
    except requests.exceptions.Timeout:
        return "The analysis is taking longer than expected. Please try a simpler query."
    except Exception as e:
        return f"An error occurred while processing your request. Please try again."


def _call_llm_streaming(system_prompt: str, user_context: str, query: str, language: str):
    """Stream LLM response token by token."""
    user_msg = f"{user_context}\n\nUser Question: {query}\n\nProvide a professional, concise response:"
    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": user_msg,
            "system": system_prompt,
            "stream": True,
            "options": {
                "temperature": OLLAMA_TEMPERATURE,
                "top_p": 0.85,
                "num_ctx": OLLAMA_NUM_CTX,
                "num_predict": OLLAMA_NUM_PREDICT,
            },
        }, timeout=OLLAMA_TIMEOUT, stream=True)
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
    except requests.exceptions.ConnectionError:
        yield "The intelligent analysis service is currently unavailable."
    except requests.exceptions.Timeout:
        yield "The analysis is taking longer than expected."
    except Exception:
        yield "An error occurred while processing your request."


# ─── Main Pipeline ───────────────────────────────────────────────────────────

def smart_chat(query: str, session_id: str = "default", language: str = "english") -> Dict:
    """
    Main chat pipeline. Routes query, fetches data, generates professional response.
    """
    # 1. Get conversation state
    session = get_session(session_id)

    # 2. Resolve geographic entities
    entities = resolve_location(query)

    # Fill in from conversation context if missing
    if not entities.get("state") and session.last_state:
        lower_q = query.lower()
        if any(w in lower_q for w in ["this", "that", "there", "here", "it", "what about", "और", "उस"]):
            entities["state"] = session.last_state
        if not entities.get("district") and session.last_district:
            entities["district"] = session.last_district

    # 3. Classify query
    classified = classify_query(query, entities)
    classified.entities["raw_message"] = query

    # 4. Handle greetings directly
    if classified.query_type == QueryType.GREETING:
        if language == "hindi":
            reply = ("नमस्ते! मैं जल दृष्टि भूजल बुद्धिमत्ता सहायक हूँ।\n\n"
                    "मैं आपको भारत के किसी भी राज्य या केंद्र शासित प्रदेश की भूजल स्थिति के बारे में बता सकता हूँ।\n\n"
                    "उदाहरण: 'राजस्थान की भूजल स्थिति क्या है?' या 'पंजाब और हरियाणा की तुलना करें।'")
        else:
            reply = ("Hello! I'm the Jal Drishti Groundwater Intelligence Assistant.\n\n"
                    "I can help you with groundwater information across all Indian states and union territories.\n\n"
                    "Try asking:\n"
                    "- What is the groundwater status of Rajasthan?\n"
                    "- Compare Punjab and Haryana\n"
                    "- Which states have the highest extraction?\n"
                    "- Show trends in groundwater extraction")
        session.update(entities, query, reply)
        return {
            "reply": reply, "sources": [], "query_type": "greeting",
            "entities": entities, "session_id": session_id
        }

    # 5. Build SQL context (for numerical data)
    sql_context = _build_sql_context(classified.query_type, entities, classified)

    # 6. Build RAG context (for knowledge/explanations)
    rag_context = _build_rag_context(query)

    # 7. Combine contexts
    combined_context = ""
    if sql_context:
        combined_context += "STRUCTURED DATA:\n" + sql_context + "\n\n"
    if rag_context:
        combined_context += "KNOWLEDGE BASE:\n" + rag_context + "\n\n"

    if not combined_context:
        combined_context = "No specific data found for this query. Provide a general response based on groundwater domain knowledge."

    # 8. Select system prompt
    system_prompt = SYSTEM_PROMPT_HI if language == "hindi" else SYSTEM_PROMPT_EN

    # 9. Generate response
    reply = _call_llm(system_prompt, combined_context, query, language)

    # 10. Clean response - remove any leaked internal references
    reply = _clean_response(reply)

    # 11. Build sources
    sources = []
    if sql_context:
        sources.append({"title": "Official Groundwater Assessment Data", "type": "database", "relevance": 1.0})
    if rag_context:
        sources.append({"title": "Groundwater Knowledge Base", "type": "knowledge", "relevance": 0.8})

    # 12. Update session
    session.update(entities, query, reply)

    return {
        "reply": reply,
        "sources": sources,
        "query_type": classified.query_type.value,
        "entities": entities,
        "session_id": session_id,
        "route": classified.route.value,
    }


def smart_chat_streaming(query: str, session_id: str = "default", language: str = "english"):
    """Streaming version of smart_chat."""
    session = get_session(session_id)
    entities = resolve_location(query)

    if not entities.get("state") and session.last_state:
        lower_q = query.lower()
        if any(w in lower_q for w in ["this", "that", "there", "here", "it", "what about", "और", "उस"]):
            entities["state"] = session.last_state

    classified = classify_query(query, entities)
    classified.entities["raw_message"] = query

    if classified.query_type == QueryType.GREETING:
        if language == "hindi":
            reply = ("नमस्ते! मैं जल दृष्टि भूजल बुद्धिमत्ता सहायक हूँ।\n\n"
                    "मैं आपको भारत के किसी भी राज्य की भूजल स्थिति बता सकता हूँ।\n\n"
                    "उदाहरण: 'राजस्थान की भूजल स्थिति क्या है?'")
        else:
            reply = ("Hello! I'm the Jal Drishti Groundwater Intelligence Assistant.\n\n"
                    "I can help you with groundwater information across all Indian states and UTs.\n\n"
                    "Try: 'What is the groundwater status of Rajasthan?'")
        session.update(entities, query, reply)
        yield {"type": "content", "content": reply}
        yield {"type": "done"}
        return

    sql_context = _build_sql_context(classified.query_type, entities, classified)
    rag_context = _build_rag_context(query)

    combined_context = ""
    if sql_context:
        combined_context += "STRUCTURED DATA:\n" + sql_context + "\n\n"
    if rag_context:
        combined_context += "KNOWLEDGE BASE:\n" + rag_context + "\n\n"
    if not combined_context:
        combined_context = "No specific data found. Provide general groundwater response."

    system_prompt = SYSTEM_PROMPT_HI if language == "hindi" else SYSTEM_PROMPT_EN

    full_reply = ""
    for token in _call_llm_streaming(system_prompt, combined_context, query, language):
        full_reply += token
        yield {"type": "token", "content": token}

    full_reply = _clean_response(full_reply)
    session.update(entities, query, full_reply)

    sources = []
    if sql_context:
        sources.append({"title": "Official Groundwater Assessment Data", "type": "database"})
    if rag_context:
        sources.append({"title": "Groundwater Knowledge Base", "type": "knowledge"})

    yield {"type": "sources", "content": sources}
    yield {"type": "done"}


def _clean_response(text: str) -> str:
    """Remove any leaked internal references from LLM response."""
    import re
    leaks = [
        r"according to (?:the )?(?:Ollama|LLM|model|rag|retrieval|prompt|context|database|document|file)",
        r"based on (?:the )?(?:Ollama|LLM|model|rag|retrieval|prompt|context)",
        r"from (?:the )?(?:Ollama|LLM|model|rag|retrieval|prompt|context)",
        r"(?:Ollama|LLM|llama|llm)\s+(?:model|system|engine|pipeline)",
        r"(?:system|user|internal)\s+(?:prompt|instruction|context)",
    ]
    for pattern in leaks:
        text = re.sub(pattern, "Based on official data", text, flags=re.IGNORECASE)
    return text
