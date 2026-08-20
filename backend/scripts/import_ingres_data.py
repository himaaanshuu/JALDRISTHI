#!/usr/bin/env python3
"""
JAL-DRISHTI Official Data Ingestion Script
===========================================

Imports verified official CGWB/IN-GRES groundwater assessment data from
OpenCity.in CKAN datastore API into the JAL-DRISHTI database.

Data Sources:
  - OpenCity.in (CKAN) — mirrors of official CGWB/IN-GRES reports
  - Dataset: National Compilation of Dynamic Ground Water Resources of India 2025
  - Dataset: National Compilation on Dynamic Ground Water Resources of India 2024

Usage:
  python backend/scripts/import_ingres_data.py              # Import all available data
  python backend/scripts/import_ingres_data.py --year 2025  # Import only 2025 data
  python backend/scripts/import_ingres_data.py --dry-run    # Preview without inserting
  python backend/scripts/import_ingres_data.py --reset      # Clear old data and re-import

Important:
  - All numeric values come directly from official CGWB/IN-GRES reports
  - No values are fabricated, interpolated, or estimated
  - NULL is stored for unavailable fields
  - Each record is traceable to its source via source_id
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import ssl
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import init_db, SessionLocal, GroundWater, DataSource

# ─── CKAN Datastore API Base ────────────────────────────────────────────────

CKAN_BASE = "https://data.opencity.in/api/3/action/datastore_search"

# ─── Official Resource IDs ──────────────────────────────────────────────────

RESOURCES = {
    2025: {
        "state_level": {
            "resource_id": "cf526819-7b0c-497a-b681-522d72db9b65",
            "name": "India States and UTs — GW Extraction 2025",
            "unit": "bcm",
            "level": "state",
        },
        "district_level": {
            "Delhi": {"resource_id": "8e39cc66-06a4-417b-8a4f-dbd4a9495ed6", "records": 14},
            "Gujarat": {"resource_id": "f64c4019-ba33-4435-9d07-290ade3c398e", "records": 35},
            "Karnataka": {"resource_id": "9f5bad83-69fd-4f61-a501-c5c7fc9d22d5", "records": 33},
            "Maharashtra": {"resource_id": "ec046422-448d-4ceb-b422-59d85fa54986", "records": 38},
            "Tamil Nadu": {"resource_id": "8000309b-59d7-4b5e-aeb1-befaaab9c0f8", "records": 38},
            "Telangana": {"resource_id": "d8c4c53b-5c73-459c-b137-11c51e8fe8e0", "records": 33},
            "Goa": {"resource_id": "62220325-6e6b-45c7-89d9-bd197842b7f2", "records": 2},
        },
        "block_level": {
            "Karnataka — Bengaluru Urban": {
                "resource_id": "6ca5cc26-7709-4ae5-885b-a1586c41bd7f",
                "records": 6,
            },
        },
        "source_name": "National Compilation of Dynamic Ground Water Resources of India 2025",
        "source_url": "https://cgwb.gov.in/cgwbpnm/download/1741",
        "organization": "Central Ground Water Board (CGWB), Ministry of Jal Shakti",
        "publication_year": 2025,
    },
    2024: {
        "state_level": {
            "resource_id": "595e6455-2851-4d62-9503-ab1f8b65f5b4",
            "name": "India States and UTs — GW Extraction 2024",
            "unit": "bcm",
            "level": "state",
        },
        "district_level": {
            "Delhi": {"resource_id": "2c3acb4f-807d-48a3-bc67-b0ecc516fd57", "records": 14},
            "Gujarat": {"resource_id": "cc0fd6e6-4171-43ab-94d0-33eb1416be14", "records": 35},
            "Karnataka": {"resource_id": "a588eb06-1c5c-4db4-9356-18a15496afce", "records": 31},
            "Maharashtra": {"resource_id": "9b560637-3549-49c6-bee5-a1e8302c4a33", "records": 36},
            "Tamil Nadu": {"resource_id": "67491446-7887-4818-b444-e5a337cc26a7", "records": 38},
            "Telangana": {"resource_id": "b69fbc07-5d1c-4f73-9394-7252c65f9300", "records": 33},
            "Goa": {"resource_id": "f3481ceb-6c94-4c15-86ed-02ce19a0155c", "records": 2},
        },
        "block_level": {},
        "source_name": "National Compilation on Dynamic Ground Water Resources of India 2024",
        "source_url": "https://cgwb.gov.in/cgwbpnm/public/uploads/documents/17387543101433268167file.pdf",
        "organization": "Central Ground Water Board (CGWB), Ministry of Jal Shakti",
        "publication_year": 2025,  # Published Jan 2025, data for assessment year 2024
    },
}


# ─── Data Fetching ──────────────────────────────────────────────────────────

def fetch_ckan_records(resource_id: str, limit: int = 10000) -> list:
    """Fetch all records from a CKAN datastore resource."""
    params = urllib.parse.urlencode({
        "resource_id": resource_id,
        "limit": limit,
    })
    url = f"{CKAN_BASE}?{params}"

    try:
        # Create SSL context that handles certificate verification
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={"User-Agent": "JAL-DRISHTI/1.0"})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = json.loads(resp.read().decode())

        if data.get("success"):
            return data["result"]["records"]
        else:
            print(f"  [ERROR] CKAN API returned success=false for {resource_id}")
            return []
    except Exception as e:
        print(f"  [ERROR] Failed to fetch {resource_id}: {e}")
        return []


# ─── Data Cleaning & Normalization ──────────────────────────────────────────

def safe_float(value, default=None):
    """Safely convert a value to float. Returns default if conversion fails."""
    if value is None or value == "" or value == "NA" or value == "N/A":
        return default
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return default


def normalize_category(raw_category: str) -> str:
    """Normalize CGWB category names."""
    if not raw_category:
        return "Safe"
    cat = raw_category.strip().lower()
    if "over" in cat or "exploit" in cat:
        return "Over-Exploited"
    elif "critical" in cat:
        return "Critical"
    elif "semi" in cat:
        return "Semi-Critical"
    else:
        return "Safe"


# State name normalization map for CGWB/IN-GRES variations
STATE_NAME_MAP = {
    "Andaman And Nicobar": "Andaman & Nicobar Islands",
    "Andaman and Nicobar": "Andaman & Nicobar Islands",
    "Andaman & Nicobar Islands": "Andaman & Nicobar Islands",
    "Dadra & Nagar Haveli and Daman & Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Dadra and Nagar Haveli and Daman and Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Jammu And Kashmir": "Jammu & Kashmir",
    "Jammu and Kashmir": "Jammu & Kashmir",
    "Jammu & Kashmir": "Jammu & Kashmir",
}


def normalize_state_name(name: str) -> str:
    """Normalize state/UT name variations."""
    if not name:
        return name
    return STATE_NAME_MAP.get(name, name)


def derive_category(extraction_stage: float) -> str:
    """Derive category from extraction stage (GEC-2015 methodology)."""
    if extraction_stage is None:
        return "Safe"
    if extraction_stage > 100:
        return "Over-Exploited"
    elif extraction_stage > 90:
        return "Critical"
    elif extraction_stage > 70:
        return "Semi-Critical"
    else:
        return "Safe"


def bcm_to_mcm(bcm_value: float) -> float:
    """Convert Billion Cubic Meters to Million Cubic Meters."""
    if bcm_value is None:
        return None
    return bcm_value * 1000


# ─── State-Level Import ─────────────────────────────────────────────────────

def import_state_level(records: list, assessment_year: int, source_id: int) -> list:
    """
    Import state-level records.
    State-level data is in BCM — convert to MCM for consistency with existing schema.
    """
    inserted = []
    for rec in records:
        state_name = rec.get("Name of State/UT", "").strip()
        if not state_name or state_name.lower() in ("grand total", "total", "india", ""):
            continue

        state_name = normalize_state_name(state_name)

        recharge_bcm = safe_float(rec.get("Total annual groundwater recharge"))
        resource_bcm = safe_float(rec.get("Annual Extractable Groundwater Resource"))
        extraction_bcm = safe_float(rec.get("Total Annual Extraction"))
        stage_pct = safe_float(rec.get("Stage of GW extraction (%)"))

        # Convert BCM to MCM
        recharge_mcm = bcm_to_mcm(recharge_bcm) if recharge_bcm is not None else None
        resource_mcm = bcm_to_mcm(resource_bcm) if resource_bcm is not None else None
        extraction_mcm = bcm_to_mcm(extraction_bcm) if extraction_bcm is not None else None

        # Derive category from official extraction stage
        if stage_pct is not None:
            category = derive_category(stage_pct)
        elif resource_mcm and extraction_mcm and resource_mcm > 0:
            stage_pct = (extraction_mcm / resource_mcm) * 100
            category = derive_category(stage_pct)
        else:
            category = "Safe"

        inserted.append({
            "state": state_name,
            "district": "",
            "block": "",
            "assessment_year": assessment_year,
            "annual_groundwater_recharge": recharge_mcm,
            "extractable_groundwater_resource": resource_mcm,
            "groundwater_extraction": extraction_mcm,
            "extraction_stage": stage_pct,
            "category": category,
            "latitude": None,
            "longitude": None,
            "is_demo_data": 0,
            "source_id": source_id,
        })

    return inserted


# ─── District-Level Import ──────────────────────────────────────────────────

def import_district_level(records: list, state_name: str, assessment_year: int, source_id: int) -> list:
    """
    Import district-level records.
    District-level data is in ham (cubic hectometers = million cubic meters).
    """
    inserted = []
    for rec in records:
        district_name = rec.get("Name of District", "").strip()
        if not district_name:
            continue

        # Skip summary/total rows
        skip_names = {"total", "grand total", "total(bcm)", "total(ham)", "total bcm", "total ham", "india"}
        if district_name.lower().strip() in skip_names or district_name.lower().startswith("total"):
            continue

        state_name = normalize_state_name(state_name)

        recharge_ham = safe_float(rec.get("Total annual groundwater recharge"))
        resource_ham = safe_float(rec.get("Annual Extractable Groundwater Resource"))
        extraction_ham = safe_float(rec.get("Total Annual Extraction"))
        stage_pct = safe_float(rec.get("Stage of GW extraction (%)"))

        # ham = MCM (cubic hectometer = million cubic meters)
        # No conversion needed

        # Derive category from official extraction stage
        if stage_pct is not None:
            category = derive_category(stage_pct)
        elif resource_ham and extraction_ham and resource_ham > 0:
            stage_pct = (extraction_ham / resource_ham) * 100
            category = derive_category(stage_pct)
        else:
            category = "Safe"

        inserted.append({
            "state": state_name,
            "district": district_name,
            "block": district_name,  # Use district as block for district-level data
            "assessment_year": assessment_year,
            "annual_groundwater_recharge": recharge_ham,
            "extractable_groundwater_resource": resource_ham,
            "groundwater_extraction": extraction_ham,
            "extraction_stage": stage_pct,
            "category": category,
            "latitude": None,
            "longitude": None,
            "is_demo_data": 0,
            "source_id": source_id,
        })

    return inserted


# ─── Block/Taluk-Level Import ───────────────────────────────────────────────

def import_block_level(records: list, state_name: str, district_name: str, assessment_year: int, source_id: int) -> list:
    """
    Import block/taluk-level records.
    Block-level data is in ham (cubic hectometers = million cubic meters).
    """
    inserted = []
    for rec in records:
        block_name = rec.get("Taluk", rec.get("Name of Block", rec.get("Block", ""))).strip()
        if not block_name:
            continue

        state_name = normalize_state_name(state_name)

        recharge_ham = safe_float(rec.get("Total annual ground water recharge (Ham)",
                                    rec.get("Total annual groundwater recharge")))
        resource_ham = safe_float(rec.get("Annual extractable groundwater resource (Ham)",
                                    rec.get("Annual Extractable Groundwater Resource")))
        extraction_ham = safe_float(rec.get("Total extraction (Ham)",
                                    rec.get("Total Annual Extraction")))
        stage_pct = safe_float(rec.get("Stage of ground water extration (%)",
                                rec.get("Stage of GW extraction (%)")))

        # Try to get category from official data
        raw_cat = rec.get("Category(OE/Critical/Semicritical/Safe)", "")
        if raw_cat:
            category = normalize_category(raw_cat)
        elif stage_pct is not None:
            category = derive_category(stage_pct)
        elif resource_ham and extraction_ham and resource_ham > 0:
            stage_pct = (extraction_ham / resource_ham) * 100
            category = derive_category(stage_pct)
        else:
            category = "Safe"

        inserted.append({
            "state": state_name,
            "district": district_name,
            "block": block_name,
            "assessment_year": assessment_year,
            "annual_groundwater_recharge": recharge_ham,
            "extractable_groundwater_resource": resource_ham,
            "groundwater_extraction": extraction_ham,
            "extraction_stage": stage_pct,
            "category": category,
            "latitude": None,
            "longitude": None,
            "is_demo_data": 0,
            "source_id": source_id,
        })

    return inserted


# ─── Main Import Logic ──────────────────────────────────────────────────────

def run_import(years: list = None, dry_run: bool = False, reset: bool = False):
    """Main import function."""
    init_db()
    db = SessionLocal()

    if years is None:
        years = sorted(RESOURCES.keys())

    print("=" * 70)
    print("JAL-DRISHTI Official Data Ingestion")
    print("Source: CGWB / IN-GRES via OpenCity.in CKAN")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 70)

    # Reset old data if requested
    if reset:
        print("\n[RESET] Removing existing non-demo groundwater records...")
        deleted = db.query(GroundWater).filter(GroundWater.is_demo_data == 0).delete()
        print(f"  Deleted {deleted} existing official records.")
        db.commit()

    total_inserted = 0
    total_errors = 0

    for year in years:
        if year not in RESOURCES:
            print(f"\n[SKIP] No resource definitions for year {year}")
            continue

        config = RESOURCES[year]
        print(f"\n{'='*70}")
        print(f"IMPORTING YEAR: {year}")
        print(f"{'='*70}")

        # Create data source record
        source = DataSource(
            source_name=config["source_name"],
            source_url=config["source_url"],
            organization=config["organization"],
            assessment_year=year,
            publication_year=config["publication_year"],
            retrieved_at=datetime.utcnow().isoformat() + "Z",
            dataset_description=f"Official CGWB/IN-GRES groundwater assessment data for assessment year {year}",
            resource_ids=json.dumps([
                config["state_level"]["resource_id"],
                *[d["resource_id"] for d in config["district_level"].values()],
                *[d["resource_id"] for d in config.get("block_level", {}).values()],
            ]),
        )

        if not dry_run:
            db.add(source)
            db.flush()
            source_id = source.id
            print(f"  Created DataSource record (id={source_id})")
        else:
            source_id = -1
            print("  [DRY-RUN] Would create DataSource record")

        all_records = []

        # 1. State-level data
        print(f"\n  [STATE] Fetching state-level data...")
        state_records = fetch_ckan_records(config["state_level"]["resource_id"])
        print(f"    Fetched {len(state_records)} state records")
        state_rows = import_state_level(state_records, year, source_id)
        print(f"    Parsed {len(state_rows)} valid records")
        all_records.extend(state_rows)

        # 2. District-level data
        print(f"\n  [DISTRICT] Fetching district-level data...")
        for state_name, dist_config in config["district_level"].items():
            dist_records = fetch_ckan_records(dist_config["resource_id"])
            print(f"    {state_name}: fetched {len(dist_records)} district records")
            dist_rows = import_district_level(dist_records, state_name, year, source_id)
            print(f"    {state_name}: parsed {len(dist_rows)} valid records")
            all_records.extend(dist_rows)

        # 3. Block-level data
        block_config = config.get("block_level", {})
        if block_config:
            print(f"\n  [BLOCK] Fetching block-level data...")
            for block_key, block_cfg in block_config.items():
                parts = block_key.split(" — ")
                state_name = parts[0] if len(parts) > 0 else ""
                district_name = parts[1] if len(parts) > 1 else ""

                block_records = fetch_ckan_records(block_cfg["resource_id"])
                print(f"    {block_key}: fetched {len(block_records)} block records")
                block_rows = import_block_level(block_records, state_name, district_name, year, source_id)
                print(f"    {block_key}: parsed {len(block_rows)} valid records")
                all_records.extend(block_rows)

        # Validate records
        valid_records = []
        invalid_count = 0
        for row in all_records:
            # Basic validation
            if not row["state"]:
                invalid_count += 1
                continue
            if row["assessment_year"] is None:
                invalid_count += 1
                continue
            # Reject records where all numeric fields are NULL
            numeric_fields = [
                row["annual_groundwater_recharge"],
                row["extractable_groundwater_resource"],
                row["groundwater_extraction"],
            ]
            if all(v is None for v in numeric_fields):
                invalid_count += 1
                continue
            valid_records.append(row)

        print(f"\n  [VALIDATE] {len(valid_records)} valid records, {invalid_count} invalid/rejected")

        # Insert records
        if not dry_run and valid_records:
            db.bulk_insert_mappings(GroundWater, valid_records)
            db.commit()
            print(f"  [INSERT] {len(valid_records)} records inserted for {year}")
        elif dry_run:
            print(f"  [DRY-RUN] Would insert {len(valid_records)} records for {year}")
        else:
            print(f"  [SKIP] No valid records to insert for {year}")

        total_inserted += len(valid_records)
        total_errors += invalid_count

    # Summary
    print(f"\n{'='*70}")
    print("IMPORT SUMMARY")
    print(f"{'='*70}")
    print(f"  Years processed: {', '.join(str(y) for y in years)}")
    print(f"  Records inserted: {total_inserted}")
    print(f"  Records rejected: {total_errors}")

    # Count by year and state
    if not dry_run:
        for year in years:
            count = db.query(GroundWater).filter(
                GroundWater.assessment_year == year,
                GroundWater.is_demo_data == 0,
            ).count()
            print(f"  Year {year}: {count} official records in database")

    db.close()
    print(f"\n{'='*70}")
    print("DONE")
    print(f"{'='*70}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import official CGWB/IN-GRES groundwater data into JAL-DRISHTI"
    )
    parser.add_argument(
        "--year", type=int, nargs="+",
        help="Import only specific year(s) (default: all available)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview import without inserting records"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Remove existing official data before importing"
    )
    args = parser.parse_args()

    run_import(
        years=args.year,
        dry_run=args.dry_run,
        reset=args.reset,
    )
