"""
JAL-DRISHTI AI — Parser Unit Tests
===================================
Run: python3 -m pytest test_parser.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse_message, KNOWN_STATES


# ─── Status Queries ──────────────────────────────────────────────────────────

class TestStatusIntent:
    def test_basic_status(self):
        r = parse_message("What is the groundwater status of Rajasthan?")
        assert r.intent == "status"
        assert r.state == "Rajasthan"
        assert r.confidence >= 0.5

    def test_status_haryana_in_db(self):
        r = parse_message("groundwater status of Haryana")
        assert r.intent == "status"
        assert r.state == "Haryana"  # Haryana now in KNOWN_STATES

    def test_status_with_tell_me_about(self):
        r = parse_message("Tell me about Gujarat")
        assert r.intent == "status"
        assert r.state == "Gujarat"

    def test_status_how_is(self):
        r = parse_message("How is Punjab doing?")
        assert r.intent == "status"
        assert r.state == "Punjab"

    def test_status_uttar_pradesh(self):
        r = parse_message("What is the groundwater status of Uttar Pradesh?")
        assert r.intent == "status"
        assert r.state == "Uttar Pradesh"

    def test_status_tamil_nadu(self):
        r = parse_message("Status of Tamil Nadu")
        assert r.intent == "status"
        assert r.state == "Tamil Nadu"


# ─── Comparison Queries ──────────────────────────────────────────────────────

class TestCompareIntent:
    def test_basic_compare(self):
        r = parse_message("Compare Gujarat between 2020 and 2024.")
        assert r.intent == "compare"
        assert r.state == "Gujarat"
        assert r.comparison_years == [2020, 2024]

    def test_compare_vs_keyword(self):
        r = parse_message("Rajasthan 2020 vs 2024")
        assert r.intent == "compare"
        assert r.state == "Rajasthan"
        assert r.comparison_years == [2020, 2024]

    def test_compare_punjab(self):
        r = parse_message("compare Punjab 2021 and 2023")
        assert r.intent == "compare"
        assert r.state == "Punjab"
        assert r.comparison_years == [2021, 2023]

    def test_compare_single_year(self):
        r = parse_message("compare Gujarat 2022")
        assert r.intent == "compare"
        assert r.state == "Gujarat"
        assert len(r.comparison_years) < 2  # Not enough years

    def test_compare_no_years(self):
        r = parse_message("compare Maharashtra and Karnataka")
        assert r.intent == "compare"
        assert r.comparison_years == []


# ─── Top Extraction Queries ──────────────────────────────────────────────────

class TestTopExtractionIntent:
    def test_basic_top(self):
        r = parse_message("Which districts have the highest extraction?")
        assert r.intent == "top_extraction"
        assert r.metric == "extraction"

    def test_top_with_state(self):
        r = parse_message("top extraction districts in Uttar Pradesh")
        assert r.intent == "top_extraction"
        assert r.state == "Uttar Pradesh"
        assert r.metric == "extraction"

    def test_top_largest(self):
        r = parse_message("Which blocks have the largest withdrawal?")
        assert r.intent == "top_extraction"

    def test_top_most_keyword(self):
        r = parse_message("most extraction in Karnataka")
        assert r.intent == "top_extraction"
        assert r.state == "Karnataka"


# ─── Critical Areas Queries ──────────────────────────────────────────────────

class TestCriticalAreasIntent:
    def test_over_exploited(self):
        r = parse_message("Show over-exploited areas.")
        assert r.intent == "critical_areas"
        assert r.category == "Over-Exploited"

    def test_critical_areas(self):
        r = parse_message("Show over-exploited areas in Punjab.")
        assert r.intent == "critical_areas"
        assert r.state == "Punjab"
        assert r.category == "Over-Exploited"

    def test_critical_blocks(self):
        r = parse_message("Which blocks are critical in Rajasthan?")
        assert r.intent == "critical_areas"
        assert r.state == "Rajasthan"
        assert r.category == "Critical"

    def test_stressed_areas(self):
        r = parse_message("Show stressed areas in Maharashtra")
        assert r.intent == "critical_areas"
        assert r.state == "Maharashtra"

    def test_depleted(self):
        r = parse_message("Show depleted groundwater areas")
        assert r.intent == "critical_areas"
        assert r.category == "Over-Exploited"


# ─── Trend Queries ───────────────────────────────────────────────────────────

class TestTrendIntent:
    def test_basic_trend(self):
        r = parse_message("What is the extraction trend for Punjab?")
        assert r.intent == "trend"
        assert r.state == "Punjab"
        assert r.metric == "extraction"

    def test_trend_over_time(self):
        r = parse_message("Show groundwater trend over time for Gujarat")
        assert r.intent == "trend"
        assert r.state == "Gujarat"

    def test_trend_historical(self):
        r = parse_message("historical trend for Tamil Nadu")
        assert r.intent == "trend"
        assert r.state == "Tamil Nadu"

    def test_trend_no_state(self):
        r = parse_message("What is the trend?")
        assert r.intent == "trend"
        assert r.state is None


# ─── Category Queries ────────────────────────────────────────────────────────

class TestCategoryIntent:
    def test_basic_category(self):
        r = parse_message("Show category distribution for Karnataka.")
        assert r.intent == "category"
        assert r.state == "Karnataka"

    def test_category_breakdown(self):
        r = parse_message("breakdown of safe and critical blocks in Gujarat")
        assert r.intent == "category"
        assert r.state == "Gujarat"

    def test_category_all_states(self):
        r = parse_message("What is the category distribution?")
        assert r.intent == "category"
        assert r.state is None


# ─── Location Queries ────────────────────────────────────────────────────────

class TestLocationIntent:
    def test_districts(self):
        r = parse_message("Show districts in Tamil Nadu.")
        assert r.intent == "location"
        assert r.state == "Tamil Nadu"

    def test_blocks(self):
        r = parse_message("Show blocks in Rajasthan")
        assert r.intent == "location"
        assert r.state == "Rajasthan"

    def test_regions(self):
        r = parse_message("Which regions are in Karnataka?")
        assert r.intent == "location"
        assert r.state == "Karnataka"


# ─── Greeting Queries ────────────────────────────────────────────────────────

class TestGreetingIntent:
    def test_hello(self):
        r = parse_message("hello")
        assert r.intent == "greeting"

    def test_hi(self):
        r = parse_message("hi")
        assert r.intent == "greeting"

    def test_help(self):
        r = parse_message("help me")
        assert r.intent == "greeting"


# ─── Entity Extraction ───────────────────────────────────────────────────────

class TestEntityExtraction:
    def test_all_states_extractable(self):
        for state in KNOWN_STATES:
            r = parse_message(f"status of {state}")
            assert r.state == state, f"Failed to extract state: {state}"

    def test_year_extraction(self):
        r = parse_message("data for 2022")
        assert r.year == 2022

    def test_multiple_years(self):
        r = parse_message("compare 2020 and 2024")
        assert r.comparison_years == [2020, 2024]

    def test_metric_extraction(self):
        for msg, expected in [
            ("extraction data", "extraction"),
            ("recharge rates", "recharge"),
            ("ph levels", "ph"),
            ("rainfall data", "rainfall"),
            ("turbidity levels", "turbidity"),
        ]:
            r = parse_message(msg)
            assert r.metric == expected, f"Failed for '{msg}': got {r.metric}, expected {expected}"

    def test_category_extraction(self):
        for msg, expected in [
            ("safe blocks", "Safe"),
            ("semi-critical areas", "Semi-Critical"),
            ("critical zones", "Critical"),
            ("over-exploited regions", "Over-Exploited"),
        ]:
            r = parse_message(msg)
            assert r.category == expected, f"Failed for '{msg}': got {r.category}, expected {expected}"


# ─── Confidence Scoring ──────────────────────────────────────────────────────

class TestConfidence:
    def test_high_confidence_rich_query(self):
        r = parse_message("Compare Gujarat between 2020 and 2024 extraction")
        assert r.confidence >= 0.75

    def test_medium_confidence(self):
        r = parse_message("What is the groundwater status of Rajasthan?")
        assert 0.4 <= r.confidence <= 0.75

    def test_low_confidence_greeting(self):
        r = parse_message("hello")
        assert r.confidence <= 0.5


# ─── Raw Message Preserved ──────────────────────────────────────────────────

class TestRawMessage:
    def test_raw_message_preserved(self):
        msg = "What is the groundwater status of Rajasthan?"
        r = parse_message(msg)
        assert r.raw_message == msg


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simple test runner (no pytest dependency)
    import traceback
    passed = 0
    failed = 0
    errors = []

    test_classes = [
        TestStatusIntent, TestCompareIntent, TestTopExtractionIntent,
        TestCriticalAreasIntent, TestTrendIntent, TestCategoryIntent,
        TestLocationIntent, TestGreetingIntent, TestEntityExtraction,
        TestConfidence, TestRawMessage,
    ]

    for cls in test_classes:
        instance = cls()
        for name in sorted(dir(instance)):
            if name.startswith("test_"):
                try:
                    getattr(instance, name)()
                    passed += 1
                    print(f"  ✓ {cls.__name__}.{name}")
                except Exception as e:
                    failed += 1
                    errors.append((f"{cls.__name__}.{name}", e))
                    print(f"  ✗ {cls.__name__}.{name}: {e}")

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if errors:
        print(f"\nFailed tests:")
        for name, e in errors:
            print(f"  {name}: {e}")
    print(f"{'='*60}")
    sys.exit(1 if failed else 0)
