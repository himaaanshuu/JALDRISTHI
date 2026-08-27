#!/usr/bin/env python3
"""
Migrate data from local SQLite to Supabase.
Run: python3 migrate_to_supabase.py
"""

import os
import sys
import sqlite3
import json
import time

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))

from supabase_client import get_client, sb_insert, sb_select, sb_count

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "jaldrishti.db")
BATCH_SIZE = 50  # Supabase REST API batch limit


def migrate_table(table_name: str, sqlite_query: str, columns: list, transform=None):
    """Migrate a single table from SQLite to Supabase."""
    if not os.path.exists(DB_PATH):
        print(f"  [SKIP] SQLite DB not found: {DB_PATH}")
        return 0

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute(sqlite_query)
        rows = [dict(r) for r in c.fetchall()]
    except Exception as e:
        print(f"  [SKIP] Table {table_name}: {e}")
        conn.close()
        return 0
    conn.close()

    if not rows:
        print(f"  [SKIP] Table {table_name}: no data")
        return 0

    # Check existing count
    existing = sb_count(table_name)
    if existing > 0:
        print(f"  [SKIP] Table {table_name}: {existing} rows already exist")
        return existing

    print(f"  Migrating {table_name}: {len(rows)} rows...")

    # Transform if needed
    if transform:
        rows = [transform(r) for r in rows]

    # Remove 'id' columns (Supabase auto-generates)
    for r in rows:
        r.pop("id", None)

    # Insert in batches
    migrated = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        try:
            sb_insert(table_name, batch)
            migrated += len(batch)
            print(f"    [{migrated}/{len(rows)}] inserted")
        except Exception as e:
            print(f"    [ERROR] Batch {i}: {str(e)[:200]}")
            # Try one by one
            for row in batch:
                try:
                    sb_insert(table_name, row)
                    migrated += 1
                except Exception as e2:
                    print(f"      [SKIP] row: {str(e2)[:100]}")
        time.sleep(0.1)  # Rate limiting

    print(f"  [DONE] {table_name}: {migrated}/{len(rows)} rows migrated")
    return migrated


def migrate_data_sources():
    """Migrate data_sources table."""
    return migrate_table(
        "data_sources",
        "SELECT * FROM data_sources",
        ["id", "source_name", "source_url", "organization", "assessment_year",
         "publication_year", "retrieved_at", "dataset_description", "resource_ids"]
    )


def migrate_groundwater():
    """Migrate groundwater table."""
    def transform(row):
        return {
            "state": row.get("state", ""),
            "district": row.get("district", ""),
            "block": row.get("block", ""),
            "assessment_year": row.get("assessment_year"),
            "annual_groundwater_recharge": row.get("annual_groundwater_recharge"),
            "extractable_groundwater_resource": row.get("extractable_groundwater_resource"),
            "groundwater_extraction": row.get("groundwater_extraction"),
            "extraction_stage": row.get("extraction_stage"),
            "category": row.get("category", ""),
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
            "is_demo_data": row.get("is_demo_data", 1),
            "source_id": row.get("source_id"),
        }
    return migrate_table(
        "groundwater",
        "SELECT * FROM groundwater WHERE block != '' OR (block = '' AND is_demo_data = 0)",
        [],  # columns handled by transform
        transform=transform
    )


def migrate_water_readings():
    """Migrate water_readings table."""
    def transform(row):
        return {
            "station_id": row.get("station_id", ""),
            "water_level": row.get("water_level"),
            "rainfall_mm": row.get("rainfall_mm"),
            "ph_level": row.get("ph_level"),
            "turbidity": row.get("turbidity"),
            "timestamp": row.get("timestamp"),
            "status": row.get("status", "normal"),
        }
    return migrate_table(
        "water_readings",
        "SELECT * FROM water_readings",
        [],
        transform=transform
    )


def main():
    print("=" * 60)
    print("JAL-DRISHTI: SQLite → Supabase Migration")
    print("=" * 60)
    print(f"SQLite: {DB_PATH}")
    print(f"Supabase: {os.getenv('SUPABASE_URL', 'NOT SET')}")
    print()

    # Test Supabase connection
    try:
        client = get_client()
        print("Supabase connection: OK")
    except Exception as e:
        print(f"Supabase connection FAILED: {e}")
        print("Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in .env")
        sys.exit(1)

    print()

    # Migrate tables
    total = 0
    total += migrate_data_sources()
    total += migrate_groundwater()
    total += migrate_water_readings()

    print()
    print("=" * 60)
    print(f"Migration complete! Total rows: {total}")
    print("=" * 60)


if __name__ == "__main__":
    main()
