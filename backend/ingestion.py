"""
Extensible Data Ingestion Framework for JAL-DRISHTI.
Supports CGWB, IMD, CWC, and state-level data sources.
"""

import json
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jaldrishti.db")


@dataclass
class IngestionResult:
    dataset_id: str
    status: str
    records_ingested: int
    records_rejected: int
    errors: List[str]
    timestamp: str


class BaseIngestionAdapter(ABC):
    """Base class for all data ingestion adapters."""

    @abstractmethod
    def dataset_id(self) -> str: ...

    @abstractmethod
    def dataset_name(self) -> str: ...

    @abstractmethod
    def fetch(self) -> List[Dict]: ...

    @abstractmethod
    def validate(self, record: Dict) -> bool: ...

    def normalize(self, record: Dict) -> Dict:
        return record

    def ingest(self) -> IngestionResult:
        errors = []
        total = 0
        rejected = 0

        try:
            records = self.fetch()
            logger.info(f"Fetched {len(records)} records from {self.dataset_id()}")

            from config import USE_SUPABASE

            if USE_SUPABASE:
                from supabase_client import sb_insert, sb_upsert, sb_count
                stored = 0
                for record in records:
                    total += 1
                    try:
                        if not self.validate(record):
                            rejected += 1
                            continue
                        normalized = self.normalize(record)
                        sb_insert("groundwater", normalized)
                        stored += 1
                    except Exception as e:
                        rejected += 1
                        errors.append(f"Record {total}: {str(e)[:100]}")

                # Update dataset version
                try:
                    sb_upsert("dataset_versions", {
                        "dataset_id": self.dataset_id(),
                        "dataset_name": self.dataset_name(),
                        "year": record.get("year", datetime.now().year),
                        "geographic_scope": record.get("geographic_scope", "India"),
                        "ingestion_date": datetime.now().isoformat(),
                        "version": "1.0",
                        "status": "completed" if not errors else "partial",
                        "record_count": total - rejected,
                        "quality_status": "validated" if not errors else "errors_found",
                    }, on_conflict="dataset_id")
                except Exception as e:
                    logger.warning(f"Failed to update dataset version: {e}")
            else:
                import sqlite3
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()

                for record in records:
                    total += 1
                    try:
                        if not self.validate(record):
                            rejected += 1
                            continue
                        normalized = self.normalize(record)
                        self._store(c, normalized)
                    except Exception as e:
                        rejected += 1
                        errors.append(f"Record {total}: {str(e)[:100]}")

                c.execute("""
                    INSERT OR REPLACE INTO dataset_versions
                    (dataset_id, dataset_name, year, geographic_scope, ingestion_date, version, status, record_count, quality_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.dataset_id(), self.dataset_name(),
                    record.get("year", datetime.now().year),
                    record.get("geographic_scope", "India"),
                    datetime.now().isoformat(),
                    "1.0",
                    "completed" if not errors else "partial",
                    total - rejected,
                    "validated" if not errors else "errors_found"
                ))

                conn.commit()
                conn.close()

            return IngestionResult(
                dataset_id=self.dataset_id(),
                status="success" if not errors else "partial",
                records_ingested=total - rejected,
                records_rejected=rejected,
                errors=errors[:50],
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            return IngestionResult(
                dataset_id=self.dataset_id(),
                status="failed",
                records_ingested=0,
                records_rejected=total,
                errors=[str(e)[:200]],
                timestamp=datetime.now().isoformat()
            )

    @abstractmethod
    def _store(self, cursor, record: Dict): ...


# ─── CGWB GWRA Adapter ──────────────────────────────────────────────────────

class CGWBAdapter(BaseIngestionAdapter):
    """Adapter for CGWB Ground Water Resource Assessment data from OpenCity CKAN."""

    def __init__(self, resource_ids: List[str], year: int):
        self._resource_ids = resource_ids
        self._year = year

    def dataset_id(self) -> str:
        return f"cgwb_gwra_{self._year}"

    def dataset_name(self) -> str:
        return f"CGWB Ground Water Resource Assessment {self._year}"

    def fetch(self) -> List[Dict]:
        import requests
        import ssl

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        all_records = []
        for rid in self._resource_ids:
            url = f"https://data.opencity.in/api/3/action/datastore_search?resource_id={rid}&limit=10000"
            try:
                resp = requests.get(url, timeout=60, verify=False)
                data = resp.json()
                if data.get("success"):
                    records = data["result"].get("records", [])
                    all_records.extend(records)
                    logger.info(f"Fetched {len(records)} records from resource {rid}")
            except Exception as e:
                logger.warning(f"Failed to fetch resource {rid}: {e}")
        return all_records

    def validate(self, record: Dict) -> bool:
        required = ["state"]
        return all(record.get(f) not in (None, "", "NULL") for f in required)

    def normalize(self, record: Dict) -> Dict:
        state_name_map = {
            "Jammu And Kashmir": "Jammu & Kashmir",
            "Andaman And Nicobar Islands": "Andaman & Nicobar Islands",
            "Dadra And Nagar Haveli And Daman And Diu": "Dadra & Nagar Haveli and Daman & Diu",
        }
        state = record.get("state", "")
        state = state_name_map.get(state, state)

        def to_mcm(val):
            try:
                v = float(val)
                if v > 1000:
                    return v / 1000
                return v
            except (ValueError, TypeError):
                return 0.0

        recharge = to_mcm(record.get("recharge_monsoon_rainfall", 0))
        extractable = to_mcm(record.get("annual_extractable_ground_water_resource", 0))
        extraction = to_mcm(record.get("total_annual_extraction", 0))
        stage = float(record.get("stage_of_ground_water_extraction", 0) or 0)

        return {
            "state": state,
            "district": record.get("district", ""),
            "block": record.get("block", record.get("assessment_unit", "")),
            "assessment_year": self._year,
            "annual_groundwater_recharge": recharge,
            "extractable_groundwater_resource": extractable,
            "groundwater_extraction": extraction,
            "extraction_stage": stage,
            "category": self._derive_category(stage),
            "latitude": float(record.get("latitude", 0) or 0),
            "longitude": float(record.get("longitude", 0) or 0),
            "is_demo_data": 0,
        }

    @staticmethod
    def _derive_category(stage: float) -> str:
        if stage <= 70: return "Safe"
        if stage <= 90: return "Semi-Critical"
        if stage <= 100: return "Critical"
        return "Over-Exploited"

    def _store(self, cursor, record: Dict):
        cursor.execute("""
            INSERT INTO groundwater
            (state, district, block, assessment_year, annual_groundwater_recharge,
             extractable_groundwater_resource, groundwater_extraction, extraction_stage,
             category, latitude, longitude, is_demo_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            record["state"], record["district"], record["block"],
            record["assessment_year"], record["annual_groundwater_recharge"],
            record["extractable_groundwater_resource"], record["groundwater_extraction"],
            record["extraction_stage"], record["category"],
            record["latitude"], record["longitude"]
        ))


# ─── Knowledge Document Adapter ──────────────────────────────────────────────

class KnowledgeDocAdapter(BaseIngestionAdapter):
    """Adapter for ingesting textual knowledge documents into RAG."""

    def __init__(self, documents: List[Dict[str, str]], source_type: str = "government"):
        self._documents = documents
        self._source_type = source_type

    def dataset_id(self) -> str:
        return f"knowledge_{self._source_type}_{datetime.now().strftime('%Y%m%d')}"

    def dataset_name(self) -> str:
        return f"Knowledge Documents ({self._source_type})"

    def fetch(self) -> List[Dict]:
        return self._documents

    def validate(self, record: Dict) -> bool:
        return bool(record.get("topic") and record.get("content"))

    def normalize(self, record: Dict) -> Dict:
        return record

    def _store(self, cursor, record: Dict):
        pass  # Knowledge docs go to RAG engine, not SQLite


# ─── Validation Utilities ───────────────────────────────────────────────────

def validate_groundwater_record(record: Dict) -> List[str]:
    """Validate a groundwater record and return list of errors."""
    errors = []

    if not record.get("state"):
        errors.append("Missing state")

    stage = record.get("extraction_stage", 0)
    if stage and (stage < 0 or stage > 500):
        errors.append(f"Impossible extraction stage: {stage}")

    recharge = record.get("annual_groundwater_recharge", 0)
    extraction = record.get("groundwater_extraction", 0)
    if recharge and extraction and extraction > recharge * 2:
        errors.append(f"Extraction ({extraction}) far exceeds recharge ({recharge})")

    lat = record.get("latitude", 0)
    lng = record.get("longitude", 0)
    if lat and lng and (lat < 5 or lat > 40 or lng < 65 or lng > 100):
        errors.append(f"Coordinates out of India bounds: {lat}, {lng}")

    return errors


def run_validation_report():
    """Generate a data quality validation report."""
    from config import USE_SUPABASE

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_records": 0,
        "valid_records": 0,
        "issues": {},
    }

    if USE_SUPABASE:
        from supabase_client import sb_select
        rows = sb_select("groundwater")
        blocks = [r for r in rows if r.get("block")]
        report["total_records"] = len(blocks)
        issues = {"missing_state": 0, "impossible_stage": 0, "extraction_exceeds_recharge": 0, "missing_coords": 0}
        valid = 0
        for r in blocks:
            is_valid = True
            if not r.get("state"):
                issues["missing_state"] += 1
                is_valid = False
            ext = r.get("groundwater_extraction", 0) or 0
            rech = r.get("annual_groundwater_recharge", 0) or 0
            if rech and ext > rech * 2:
                issues["extraction_exceeds_recharge"] += 1
                is_valid = False
            if is_valid:
                valid += 1
        report["valid_records"] = valid
        report["issues"] = issues
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM groundwater")
        report["total_records"] = c.fetchone()[0]
        c.execute("""
            SELECT id, state, district, block, extraction_stage,
                   groundwater_extraction, annual_groundwater_recharge
            FROM groundwater WHERE block != ''
        """)
        issues = {"missing_state": 0, "impossible_stage": 0, "extraction_exceeds_recharge": 0, "missing_coords": 0}
        for row in c.fetchall():
            valid = True
            if not row[1]:
                issues["missing_state"] += 1
                valid = False
            if row[5] and row[6] and row[5] > row[6] * 2:
                issues["extraction_exceeds_recharge"] += 1
                valid = False
            if valid:
                report["valid_records"] += 1
        report["issues"] = issues
        conn.close()

    report["quality_score"] = round(report["valid_records"] / max(report["total_records"], 1) * 100, 1)
    return report


# ─── Available Adapters Registry ─────────────────────────────────────────────

ADAPTERS = {
    "cgwb_gwra_2025": lambda: CGWBAdapter(
        resource_ids=["5add9730-1838-4781-a072-ce8d303c3844"],
        year=2025
    ),
    "cgwb_gwra_2024": lambda: CGWBAdapter(
        resource_ids=["595e6455-2851-4d62-9503-ab1f8b65f5b4"],
        year=2024
    ),
}


def ingest_dataset(dataset_key: str) -> IngestionResult:
    """Run ingestion for a registered dataset."""
    if dataset_key not in ADAPTERS:
        return IngestionResult(
            dataset_id=dataset_key, status="error",
            records_ingested=0, records_rejected=0,
            errors=[f"Unknown dataset: {dataset_key}"],
            timestamp=datetime.now().isoformat()
        )
    adapter = ADAPTERS[dataset_key]()
    return adapter.ingest()
