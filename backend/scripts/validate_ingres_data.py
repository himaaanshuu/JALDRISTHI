#!/usr/bin/env python3
"""
JAL-DRISHTI Data Validation Report
===================================

Generates a comprehensive data-quality report for the JAL-DRISHTI database,
checking both official (CGWB/IN-GRES) and synthetic (demo) records.

Usage:
  python backend/scripts/validate_ingres_data.py
  python backend/scripts/validate_ingres_data.py --year 2025
  python backend/scripts/validate_ingres_data.py --source-only
"""

import sys
import os
import argparse
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import init_db, SessionLocal, GroundWater, DataSource

CATEGORY_VALID = {"Safe", "Semi-Critical", "Critical", "Over-Exploited"}


def run_validation(year_filter=None, source_only=False):
    init_db()
    db = SessionLocal()

    print("=" * 70)
    print("JAL-DRISHTI DATA QUALITY REPORT")
    print("=" * 70)

    # ─── Source Provenance ──────────────────────────────────────────────
    sources = db.query(DataSource).all()
    print(f"\n## DATA SOURCES ({len(sources)} registered)")
    print("-" * 50)
    for s in sources:
        print(f"  [{s.id}] {s.source_name}")
        print(f"       Organization: {s.organization}")
        print(f"       Assessment Year: {s.assessment_year}")
        print(f"       Published: {s.publication_year}")
        print(f"       URL: {s.source_url}")
        print(f"       Retrieved: {s.retrieved_at}")
        resource_ids = s.resource_ids or "[]"
        print(f"       Resource IDs: {resource_ids[:80]}...")

    # ─── Total Records ──────────────────────────────────────────────────
    query = db.query(GroundWater)
    if source_only:
        query = query.filter(GroundWater.is_demo_data == 0)
    if year_filter:
        query = query.filter(GroundWater.assessment_year.in_(year_filter))

    total = query.count()
    print(f"\n## TOTAL RECORDS: {total}")

    # ─── Records by Year ────────────────────────────────────────────────
    from sqlalchemy import func
    by_year = (
        db.query(
            GroundWater.assessment_year,
            GroundWater.is_demo_data,
            func.count().label("cnt"),
        )
        .group_by(GroundWater.assessment_year, GroundWater.is_demo_data)
        .order_by(GroundWater.assessment_year)
    )
    if year_filter:
        by_year = by_year.filter(GroundWater.assessment_year.in_(year_filter))
    if source_only:
        by_year = by_year.filter(GroundWater.is_demo_data == 0)
    by_year = by_year.all()

    print(f"\n## RECORDS BY YEAR")
    print("-" * 50)
    year_totals = defaultdict(lambda: {"official": 0, "demo": 0})
    for y, is_demo, cnt in by_year:
        label = "DEMO" if is_demo else "OFFICIAL"
        year_totals[y]["official" if not is_demo else "demo"] += cnt
        print(f"  {y}: {cnt:>5} records ({label})")
    for y in sorted(year_totals.keys()):
        d = year_totals[y]
        total_y = d["official"] + d["demo"]
        print(f"  {y}: {total_y:>5} total  ({d['official']} official, {d['demo']} demo)")

    # ─── Records by State ───────────────────────────────────────────────
    q_states = (
        db.query(GroundWater.state, func.count().label("cnt"))
        .group_by(GroundWater.state)
        .order_by(GroundWater.state)
    )
    if source_only:
        q_states = q_states.filter(GroundWater.is_demo_data == 0)
    if year_filter:
        q_states = q_states.filter(GroundWater.assessment_year.in_(year_filter))
    by_state = q_states.all()

    print(f"\n## RECORDS BY STATE ({len(by_state)} states/UTs)")
    print("-" * 50)
    for state, cnt in by_state:
        print(f"  {state:<30} {cnt:>5} records")

    # ─── Missing Values ─────────────────────────────────────────────────
    print(f"\n## MISSING VALUES")
    print("-" * 50)
    fields_to_check = [
        ("state", GroundWater.state),
        ("district", GroundWater.district),
        ("block", GroundWater.block),
        ("assessment_year", GroundWater.assessment_year),
        ("annual_groundwater_recharge", GroundWater.annual_groundwater_recharge),
        ("extractable_groundwater_resource", GroundWater.extractable_groundwater_resource),
        ("groundwater_extraction", GroundWater.groundwater_extraction),
        ("extraction_stage", GroundWater.extraction_stage),
        ("category", GroundWater.category),
        ("latitude", GroundWater.latitude),
        ("longitude", GroundWater.longitude),
        ("source_id", GroundWater.source_id),
    ]
    for field_name, field_col in fields_to_check:
        null_count = query.filter(field_col.is_(None)).count()
        if field_name in ("state", "district", "block", "assessment_year", "category"):
            empty_count = query.filter(field_col == "").count()
            total_missing = null_count + empty_count
        else:
            total_missing = null_count
        pct = (total_missing / total * 100) if total > 0 else 0
        status = "OK" if total_missing == 0 else f"MISSING: {total_missing} ({pct:.1f}%)"
        print(f"  {field_name:<40} {status}")

    # ─── Duplicate Records ──────────────────────────────────────────────
    from sqlalchemy import text
    dup_query = text("""
        SELECT state, district, block, assessment_year, COUNT(*) as cnt
        FROM groundwater
        GROUP BY state, district, block, assessment_year
        HAVING COUNT(*) > 1
    """)
    duplicates = db.execute(dup_query).fetchall()
    print(f"\n## DUPLICATE RECORDS")
    print("-" * 50)
    if duplicates:
        print(f"  Found {len(duplicates)} duplicate (state, district, block, year) combinations:")
        for row in duplicates[:20]:
            print(f"    {row[0]}/{row[1]}/{row[2]} ({row[3]}): {row[4]} copies")
    else:
        print("  No duplicate records found.")

    # ─── Invalid Categories ─────────────────────────────────────────────
    print(f"\n## CATEGORY VALIDATION")
    print("-" * 50)
    cat_query = (
        db.query(GroundWater.category, func.count().label("cnt"))
        .group_by(GroundWater.category)
    )
    if source_only:
        cat_query = cat_query.filter(GroundWater.is_demo_data == 0)
    categories = cat_query.all()
    for cat, cnt in categories:
        valid = "VALID" if cat in CATEGORY_VALID else "INVALID"
        print(f"  {cat:<25} {cnt:>5} records  [{valid}]")

    # ─── Extraction Stage Sanity ────────────────────────────────────────
    print(f"\n## EXTRACTION STAGE SANITY CHECK")
    print("-" * 50)
    stage_query = query.filter(GroundWater.extraction_stage.isnot(None))
    stages = stage_query.with_entities(GroundWater.extraction_stage).all()
    if stages:
        stage_vals = [s[0] for s in stages]
        negative = sum(1 for v in stage_vals if v < 0)
        over_500 = sum(1 for v in stage_vals if v > 500)
        print(f"  Total records with extraction_stage: {len(stage_vals)}")
        print(f"  Min: {min(stage_vals):.2f}%")
        print(f"  Max: {max(stage_vals):.2f}%")
        print(f"  Negative values: {negative}")
        print(f"  Values > 500%: {over_500}")
    else:
        print("  No extraction_stage values found.")

    # ─── Source Coverage ────────────────────────────────────────────────
    print(f"\n## SOURCE COVERAGE")
    print("-" * 50)
    official = query.filter(GroundWater.is_demo_data == 0).count()
    demo = query.filter(GroundWater.is_demo_data == 1).count()
    print(f"  Official (CGWB/IN-GRES): {official} records")
    print(f"  Synthetic (demo):        {demo} records")
    print(f"  Total:                   {official + demo} records")

    # ─── Summary ────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("VALIDATION COMPLETE")
    print(f"{'='*70}")

    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate JAL-DRISHTI groundwater data")
    parser.add_argument("--year", type=int, nargs="+", help="Filter by year(s)")
    parser.add_argument("--source-only", action="store_true", help="Only validate official records")
    args = parser.parse_args()
    run_validation(year_filter=args.year, source_only=args.source_only)
