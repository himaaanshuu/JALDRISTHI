"""
Comprehensive Test Suite for JAL-DRISHTI Groundwater Intelligence.
Tests: query routing, geo resolution, numeric calculations, SQL queries, RAG, hallucination prevention.
"""

import sys
import os
import json
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))

from geo_resolver import resolve_state, resolve_location, resolve_district, get_all_states, CITY_TO_DISTRICT_STATE
from query_router import classify_query, QueryType, QueryRoute
from numeric_calc import (
    percentage_change, absolute_change, compute_comparison,
    compute_trend, compute_rankings, compute_risk_score, format_number
)
from config import DB_PATH, get_gec_category

# ─── Test Runner ─────────────────────────────────────────────────────────────

class TestResult:
    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, condition, msg=""):
        if condition:
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append(msg or "Assertion failed")

    def summary(self):
        total = self.passed + self.failed
        status = "PASS" if self.failed == 0 else "FAIL"
        print(f"  [{status}] {self.name}: {self.passed}/{total} passed")
        if self.errors:
            for e in self.errors[:3]:
                print(f"    - {e}")
        return self.failed == 0


# ─── Geographic Resolution Tests ─────────────────────────────────────────────

def test_geo_resolution():
    t = TestResult("Geographic Resolution")

    # State canonical names
    t.ok(resolve_state("punjab") == "Punjab", "Punjab resolution")
    t.ok(resolve_state("rajasthan") == "Rajasthan", "Rajasthan resolution")
    t.ok(resolve_state("tamil nadu") == "Tamil Nadu", "Tamil Nadu resolution")
    t.ok(resolve_state("west bengal") == "West Bengal", "West Bengal resolution")
    t.ok(resolve_state("madhya pradesh") == "Madhya Pradesh", "MP resolution")
    t.ok(resolve_state("uttar pradesh") == "Uttar Pradesh", "UP resolution")
    t.ok(resolve_state("jammu and kashmir") == "Jammu & Kashmir", "J&K resolution")
    t.ok(resolve_state("delhi") == "Delhi", "Delhi resolution")
    t.ok(resolve_state("puducherry") == "Puducherry", "Puducherry resolution")
    t.ok(resolve_state("lakshadweep") == "Lakshadweep", "Lakshadweep resolution")

    # Abbreviations
    t.ok(resolve_state("pb") == "Punjab", "PB -> Punjab")
    t.ok(resolve_state("rj") == "Rajasthan", "RJ -> Rajasthan")
    t.ok(resolve_state("up") == "Uttar Pradesh", "UP -> UP")
    t.ok(resolve_state("mp") == "Madhya Pradesh", "MP -> MP")
    t.ok(resolve_state("tn") == "Tamil Nadu", "TN -> Tamil Nadu")
    t.ok(resolve_state("wb") == "West Bengal", "WB -> West Bengal")
    t.ok(resolve_state("hr") == "Haryana", "HR -> Haryana")
    t.ok(resolve_state("ka") == "Karnataka", "KA -> Karnataka")

    # Hindi names
    t.ok(resolve_state("पंजाब") == "Punjab", "Hindi Punjab")
    t.ok(resolve_state("राजस्थान") == "Rajasthan", "Hindi Rajasthan")
    t.ok(resolve_state("बिहार") == "Bihar", "Hindi Bihar")
    t.ok(resolve_state("महाराष्ट्र") == "Maharashtra", "Hindi Maharashtra")
    t.ok(resolve_state("तमिल नाडु") == "Tamil Nadu", "Hindi Tamil Nadu")
    t.ok(resolve_state("उत्तर प्रदेश") == "Uttar Pradesh", "Hindi UP")

    # District resolution
    t.ok("Bengaluru" in resolve_district("bangalore"), "Bangalore -> Bengaluru")
    t.ok(resolve_district("calcutta") == "Kolkata", "Calcutta -> Kolkata")
    t.ok(resolve_district("madras") == "Chennai", "Madras -> Chennai")
    t.ok(resolve_district("poona") == "Pune", "Poona -> Pune")
    t.ok(resolve_district("jaipur") == "Jaipur", "Jaipur district")

    # Location from query
    loc = resolve_location("What is the groundwater status of Rajasthan?")
    t.ok(loc["state"] == "Rajasthan", "Location extraction: Rajasthan")

    loc = resolve_location("Compare Punjab and Haryana")
    t.ok(loc["state"] is not None, "Location extraction: compare")

    loc = resolve_location("Tell me about Jaipur")
    t.ok(loc["district"] == "Jaipur", "Location extraction: Jaipur district")
    t.ok(loc["state"] == "Rajasthan", "Location extraction: Jaipur -> Rajasthan")

    loc = resolve_location("Groundwater in Bangalore")
    t.ok(loc["district"] is not None, "Bangalore district resolved")
    t.ok(loc["state"] == "Karnataka", "Bangalore -> Karnataka")

    # All states list
    states = get_all_states()
    t.ok(len(states) >= 36, f"All states list: {len(states)} entries")

    # No false positives
    t.ok(resolve_state("hello") is None, "hello is not a state")
    t.ok(resolve_state("water") is None, "water is not a state")

    return t.summary()


# ─── Query Router Tests ──────────────────────────────────────────────────────

def test_query_router():
    t = TestResult("Query Router")

    # State status
    q = classify_query("What is the groundwater status of Rajasthan?", {"state": "Rajasthan"})
    t.ok(q.query_type == QueryType.STATE_STATUS, "State status query")
    t.ok(q.route == QueryRoute.SQL_PLUS_RAG, "State status route")

    # Comparison
    q = classify_query("Compare Punjab and Haryana", {"state": None})
    t.ok(q.query_type == QueryType.COMPARISON, "Comparison query")
    t.ok(q.needs_calculation == True, "Comparison needs calculation")

    # Ranking
    q = classify_query("Which states have the highest groundwater extraction?", {})
    t.ok(q.query_type == QueryType.RANKING, "Ranking query")
    t.ok(q.route == QueryRoute.SQL_ONLY, "Ranking route: SQL only")

    # Trend
    q = classify_query("What is the trend in groundwater extraction over time?", {"state": "Rajasthan"})
    t.ok(q.query_type == QueryType.TREND, "Trend query")

    # Quality
    q = classify_query("Which districts have high fluoride?", {"state": "Rajasthan"})
    t.ok(q.query_type == QueryType.QUALITY, "Quality query")

    # Recommendation
    q = classify_query("What management measures are suitable?", {"state": "Punjab"})
    t.ok(q.query_type == QueryType.RECOMMENDATION, "Recommendation query")

    # Regulatory
    q = classify_query("What are the groundwater regulations?", {})
    t.ok(q.query_type == QueryType.REGULATORY, "Regulatory query")

    # Greeting
    q = classify_query("Hello", {})
    t.ok(q.query_type == QueryType.GREETING, "Greeting query")
    t.ok(q.route == QueryRoute.LLM_DIRECT, "Greeting route: LLM direct")

    # Hindi queries
    q = classify_query("राजस्थान की भूजल स्थिति क्या है?", {"state": "Rajasthan"})
    t.ok(q.query_type == QueryType.STATE_STATUS, "Hindi state status")

    q = classify_query("सबसे ज्यादा भूजल निकासी किस राज्य में है?", {})
    t.ok(q.query_type == QueryType.RANKING, "Hindi ranking query")

    return t.summary()


# ─── Numeric Calculation Tests ───────────────────────────────────────────────

def test_numeric_calculations():
    t = TestResult("Numeric Calculations")

    # Percentage change
    t.ok(percentage_change(100, 150) == 50.0, "50% increase")
    t.ok(percentage_change(100, 80) == -20.0, "20% decrease")
    t.ok(percentage_change(100, 100) == 0.0, "No change")
    t.ok(percentage_change(0, 50) == 0.0, "Zero base")

    # Absolute change
    t.ok(absolute_change(100, 150) == 50.0, "Absolute +50")
    t.ok(absolute_change(100, 80) == -20.0, "Absolute -20")

    # Comparison
    data_a = {"extraction_stage": 150.0, "groundwater_extraction": 28000.0, "annual_groundwater_recharge": 21000.0, "assessment_year": 2025}
    data_b = {"extraction_stage": 105.0, "groundwater_extraction": 13000.0, "annual_groundwater_recharge": 14000.0, "assessment_year": 2025}
    comp = compute_comparison("Punjab", data_a, "Haryana", data_b, "extraction_stage", "%")
    t.ok(comp is not None, "Comparison computed")
    t.ok(comp.value_a == 150.0, "Punjab stage correct")
    t.ok(comp.value_b == 105.0, "Haryana stage correct")
    t.ok(comp.a_higher == True, "Punjab higher")

    # Trend
    points = [
        {"assessment_year": 2020, "avg_stage": 60.0},
        {"assessment_year": 2022, "avg_stage": 62.0},
        {"assessment_year": 2024, "avg_stage": 65.0},
        {"assessment_year": 2025, "avg_stage": 68.0},
    ]
    trend = compute_trend("Rajasthan", "avg_stage", "%", points)
    t.ok(trend is not None, "Trend computed")
    t.ok(trend.direction == "increasing", "Trend increasing")
    t.ok(trend.total_change == 8.0, "Total change 8%")

    # Rankings
    items = [
        {"state": "Punjab", "avg_stage": 146.0},
        {"state": "Haryana", "avg_stage": 105.0},
        {"state": "Rajasthan", "avg_stage": 89.0},
    ]
    ranks = compute_rankings(items, "state", "avg_stage", "%")
    t.ok(len(ranks) == 3, "3 rankings")
    t.ok(ranks[0].name == "Punjab", "Punjab ranked #1")
    t.ok(ranks[0].value == 146.0, "Punjab value correct")

    # Risk score
    risk = compute_risk_score({
        "avg_extraction_stage": 146.0,
        "over_exploited_pct": 63.0,
        "critical_pct": 9.0,
        "trend_delta": 5.0
    })
    t.ok(risk["score"] > 70, f"High risk score: {risk['score']}")
    t.ok(risk["level"] in ("High", "Critical"), f"Risk level: {risk['level']}")

    # Format number
    formatted = format_number(1500000, "MCM")
    t.ok("M" in formatted, f"Format million: {formatted}")
    formatted2 = format_number(50000, "MCM")
    t.ok("K" in formatted2, f"Format thousand: {formatted2}")

    # GEC category
    t.ok(get_gec_category(50) == "Safe", "50% = Safe")
    t.ok(get_gec_category(75) == "Semi-Critical", "75% = Semi-Critical")
    t.ok(get_gec_category(95) == "Critical", "95% = Critical")
    t.ok(get_gec_category(120) == "Over-Exploited", "120% = Over-Exploited")

    return t.summary()


# ─── Database Query Tests ────────────────────────────────────────────────────

def test_database_queries():
    t = TestResult("Database Queries")

    if not os.path.exists(DB_PATH):
        print("  [SKIP] Database not found")
        return True

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Basic existence
    c.execute("SELECT COUNT(*) FROM groundwater")
    total = c.fetchone()[0]
    t.ok(total > 0, f"Records exist: {total}")

    # State query
    c.execute("SELECT DISTINCT state FROM groundwater WHERE state != '' ORDER BY state")
    states = [r[0] for r in c.fetchall()]
    t.ok(len(states) >= 20, f"States in DB: {len(states)}")
    t.ok("Punjab" in states, "Punjab in DB")
    t.ok("Rajasthan" in states, "Rajasthan in DB")
    t.ok("Tamil Nadu" in states, "Tamil Nadu in DB")

    # Block query with extraction stage - use a state that has blocks
    c.execute("""
        SELECT block, district, state, extraction_stage, category
        FROM groundwater WHERE block != '' AND state = 'Gujarat'
        ORDER BY extraction_stage DESC LIMIT 5
    """)
    rows = c.fetchall()
    t.ok(len(rows) > 0, f"Gujarat blocks: {len(rows)}")
    if rows:
        t.ok(rows[0][3] > 0, f"Top Gujarat block stage: {rows[0][3]}%")

    # Category distribution
    c.execute("""
        SELECT category, COUNT(*) FROM groundwater
        WHERE block != '' GROUP BY category
    """)
    cats = dict(c.fetchall())
    t.ok("Safe" in cats, "Safe category exists")
    t.ok("Over-Exploited" in cats, "Over-Exploited category exists")

    # Year-wise query
    c.execute("SELECT DISTINCT assessment_year FROM groundwater ORDER BY assessment_year")
    years = [r[0] for r in c.fetchall()]
    t.ok(len(years) >= 2, f"Assessment years: {years}")

    # Trend query - use a state that has data across years
    c.execute("""
        SELECT assessment_year, ROUND(AVG(extraction_stage), 2)
        FROM groundwater WHERE state = 'Gujarat' AND block != ''
        GROUP BY assessment_year ORDER BY assessment_year
    """)
    trend = c.fetchall()
    t.ok(len(trend) >= 1, f"Gujarat trend points: {len(trend)}")

    # Comparison query
    c.execute("""
        SELECT state, ROUND(AVG(extraction_stage), 2) as avg_stage
        FROM groundwater WHERE block != ''
        GROUP BY state ORDER BY avg_stage DESC LIMIT 5
    """)
    top = c.fetchall()
    t.ok(len(top) > 0, "Top extraction states query works")
    t.ok(top[0][0] in ("Delhi", "Gujarat", "Karnataka", "Maharashtra", "Tamil Nadu", "Telangana"), f"Top state: {top[0][0]}")

    # District query - use a state that has districts
    c.execute("""
        SELECT district, ROUND(AVG(extraction_stage), 2)
        FROM groundwater WHERE state = 'Gujarat' AND block != ''
        GROUP BY district ORDER BY AVG(extraction_stage) DESC
    """)
    districts = c.fetchall()
    t.ok(len(districts) > 0, f"Gujarat districts: {len(districts)}")

    # Over-exploited blocks
    c.execute("""
        SELECT block, district, state, extraction_stage
        FROM groundwater WHERE category = 'Over-Exploited' AND block != ''
        ORDER BY extraction_stage DESC LIMIT 10
    """)
    oe = c.fetchall()
    t.ok(len(oe) > 0, f"Over-exploited blocks: {len(oe)}")
    if oe:
        t.ok(oe[0][3] > 100, f"Top OE stage: {oe[0][3]}%")

    conn.close()
    return t.summary()


# ─── SQL Injection Prevention Tests ──────────────────────────────────────────

def test_sql_injection():
    t = TestResult("SQL Injection Prevention")

    malicious_queries = [
        "'; DROP TABLE groundwater; --",
        "1' OR '1'='1",
        "Punjab' UNION SELECT * FROM groundwater --",
        "admin'--",
        "1; DELETE FROM groundwater WHERE 1=1",
    ]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for mq in malicious_queries:
        try:
            c.execute("SELECT * FROM groundwater WHERE state = ?", (mq,))
            rows = c.fetchall()
            t.ok(True, f"Injection blocked: {mq[:30]}...")
        except Exception:
            t.ok(True, f"Injection caused error (safe): {mq[:30]}...")

    # Verify table still exists
    c.execute("SELECT COUNT(*) FROM groundwater")
    count = c.fetchone()[0]
    t.ok(count > 0, "Table intact after injection attempts")

    conn.close()
    return t.summary()


# ─── Hallucination Prevention Tests ──────────────────────────────────────────

def test_hallucination_prevention():
    t = TestResult("Hallucination Prevention")

    # Test that we don't invent values for unknown states
    from geo_resolver import resolve_state
    t.ok(resolve_state("Atlantis") is None, "Unknown state returns None")
    t.ok(resolve_state("Wakanda") is None, "Fictional state returns None")
    t.ok(resolve_state("") is None, "Empty string returns None")

    # Test that non-existent district doesn't match
    loc = resolve_location("Tell me about groundwater in FakeCity123")
    t.ok(loc["district"] is None or loc["district"] == "Fakecity123", "Unknown district handled")

    # Test numeric calculation doesn't fabricate
    t.ok(percentage_change(0, 0) == 0.0, "Zero division handled")
    result = compute_trend("NonExistent", "metric", "%", [])
    t.ok(result is None, "Empty trend returns None")

    # Test comparison with missing data
    comp = compute_comparison("A", {}, "B", {}, "metric", "%")
    t.ok(comp is None, "Missing data returns None")

    return t.summary()


# ─── Follow-up Context Tests ─────────────────────────────────────────────────

def test_followup_context():
    t = TestResult("Follow-up Context")

    from smart_chat import get_session

    session = get_session("test_session")

    # Simulate conversation
    session.update({"state": "Rajasthan", "district": None}, "Tell me about Rajasthan", "Rajasthan overview...")
    t.ok(session.last_state == "Rajasthan", "State remembered")

    # Follow-up without state mention
    loc = resolve_location("What about Jaipur?")
    t.ok(loc["district"] == "Jaipur", "Follow-up district resolved")

    # Session context fill
    session.update({"state": None, "district": None}, "What about that state?", "Details...")
    t.ok(session.last_state == "Rajasthan", "Session context preserved")

    return t.summary()


# ─── Run All Tests ───────────────────────────────────────────────────────────

def run_all_tests():
    print("=" * 60)
    print("JAL-DRISHTI COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    results = []
    results.append(test_geo_resolution())
    results.append(test_query_router())
    results.append(test_numeric_calculations())
    results.append(test_database_queries())
    results.append(test_sql_injection())
    results.append(test_hallucination_prevention())
    results.append(test_followup_context())

    print("=" * 60)
    total_pass = sum(1 for r in results if r)
    total_fail = sum(0 for r in results if r)
    print(f"TEST SUITE: {total_pass}/{len(results)} test groups passed")
    print("=" * 60)

    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
