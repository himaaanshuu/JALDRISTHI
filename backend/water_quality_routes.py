"""
Water Quality API Endpoints for JALDRISTHI.
Handles water quality data queries, ingestion, and analysis.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from supabase_client import sb_select, sb_insert, sb_upsert, sb_count
from auth_middleware import require_auth, require_admin, get_user_id

router = APIRouter(prefix="/api/water-quality", tags=["water-quality"])

# BIS/CGWB Drinking Water Standards (WHO/India 2012)
BIS_STANDARDS = {
    "ph": {"min": 6.5, "max": 8.5, "unit": "pH", "param": "pH"},
    "tds_mg_l": {"max": 500, "unit": "mg/L", "param": "TDS"},
    "fluoride_mg_l": {"max": 1.0, "unit": "mg/L", "param": "Fluoride"},
    "arsenic_ug_l": {"max": 10, "unit": "μg/L", "param": "Arsenic"},
    "nitrate_mg_l": {"max": 45, "unit": "mg/L", "param": "Nitrate"},
    "iron_mg_l": {"max": 0.3, "unit": "mg/L", "param": "Iron"},
    "chloride_mg_l": {"max": 250, "unit": "mg/L", "param": "Chloride"},
    "sulphate_mg_l": {"max": 200, "unit": "mg/L", "param": "Sulphate"},
    "hardness_mg_l": {"max": 200, "unit": "mg/L", "param": "Hardness"},
    "uranium_ug_l": {"max": 30, "unit": "μg/L", "param": "Uranium"},
    "ec_umho_cm": {"max": 750, "unit": "μS/cm", "param": "EC"},
}


def assess_parameter(param: str, value: float) -> Dict[str, Any]:
    """Assess a single parameter against BIS standards."""
    if param not in BIS_STANDARDS or value is None:
        return {"parameter": param, "value": value, "status": "unknown", "limit": None}

    std = BIS_STANDARDS[param]
    limit = std["max"]
    if value <= limit:
        status = "safe"
    elif value <= limit * 1.5:
        status = "moderate"
    else:
        status = "exceeded"

    return {
        "parameter": std["param"],
        "value": value,
        "unit": std["unit"],
        "limit": limit,
        "status": status,
        "exceedance_pct": round(((value - limit) / limit) * 100, 1) if value > limit else 0,
    }


def assess_sample(record: Dict[str, Any]) -> Dict[str, Any]:
    """Assess all parameters of a water quality sample."""
    assessments = []
    param_fields = [k for k in BIS_STANDARDS.keys() if k in record]

    for param in param_fields:
        value = record.get(param)
        if value is not None:
            assessments.append(assess_parameter(param, value))

    exceeded = [a for a in assessments if a["status"] == "exceeded"]
    total = len(assessments)

    if total == 0:
        overall = "unknown"
    elif len(exceeded) == 0:
        overall = "safe"
    elif len(exceeded) <= 2:
        overall = "moderate"
    else:
        overall = "unsuitable"

    return {
        "overall_status": overall,
        "parameters_assessed": total,
        "parameters_exceeded": len(exceeded),
        "assessments": assessments,
        "exceeded_parameters": [a["parameter"] for a in exceeded],
    }


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.get("/standards")
async def get_bis_standards():
    """Get BIS/CGWB drinking water quality standards."""
    return {"standards": BIS_STANDARDS, "source": "BIS 2012 / CGWB"}


@router.get("/state/{state}")
async def get_state_quality(
    state: str,
    year: Optional[int] = Query(None, description="Assessment year"),
    limit: int = Query(100, ge=1, le=500),
):
    """Get water quality data for a state."""
    filters = {"state": state}
    if year:
        filters["assessment_year"] = year

    records = sb_select("groundwater_quality", filters=filters, limit=limit)
    if not records:
        raise HTTPException(status_code=404, detail=f"No water quality data found for {state}")

    assessed = [assess_sample(r) for r in records]

    # Aggregate by district
    by_district: Dict[str, List] = {}
    for r, a in zip(records, assessed):
        dist = r.get("district", "Unknown")
        by_district.setdefault(dist, []).append({"record": r, "assessment": a})

    district_summary = []
    for dist, samples in by_district.items():
        statuses = [s["assessment"]["overall_status"] for s in samples]
        exceeded_params = set()
        for s in samples:
            exceeded_params.update(s["assessment"]["exceeded_parameters"])
        district_summary.append({
            "district": dist,
            "samples": len(samples),
            "safe_count": statuses.count("safe"),
            "moderate_count": statuses.count("moderate"),
            "unsuitable_count": statuses.count("unsuitable"),
            "exceeded_parameters": list(exceeded_params),
            "latest_sample": samples[-1]["record"],
        })

    return {
        "state": state,
        "total_samples": len(records),
        "district_summary": district_summary,
        "records": records,
    }


@router.get("/district/{state}/{district}")
async def get_district_quality(
    state: str,
    district: str,
    year: Optional[int] = Query(None),
):
    """Get water quality data for a specific district."""
    filters = {"state": state, "district": district}
    if year:
        filters["assessment_year"] = year

    records = sb_select("groundwater_quality", filters=filters, limit=200)
    if not records:
        raise HTTPException(status_code=404, detail=f"No water quality data for {district}, {state}")

    assessed = [assess_sample(r) for r in records]

    # Aggregate parameters across all samples
    param_agg: Dict[str, List[float]] = {}
    for r in records:
        for param in BIS_STANDARDS:
            val = r.get(param)
            if val is not None:
                param_agg.setdefault(param, []).append(val)

    param_summary = []
    for param, values in param_agg.items():
        std = BIS_STANDARDS[param]
        avg_val = sum(values) / len(values)
        max_val = max(values)
        param_summary.append({
            "parameter": std["param"],
            "avg": round(avg_val, 2),
            "max": round(max_val, 2),
            "min": round(min(values), 2),
            "count": len(values),
            "limit": std["max"],
            "exceedance_count": sum(1 for v in values if v > std["max"]),
        })

    return {
        "state": state,
        "district": district,
        "total_samples": len(records),
        "parameter_summary": param_summary,
        "records": records,
    }


@router.get("/overall")
async def get_overall_quality_stats():
    """Get national-level water quality overview."""
    count = sb_count("groundwater_quality")
    if count == 0:
        return {"total_samples": 0, "message": "No water quality data available yet"}

    records = sb_select("groundwater_quality", limit=500)
    assessed = [assess_sample(r) for r in records]

    statuses = [a["overall_status"] for a in assessed]
    all_exceeded = set()
    for a in assessed:
        all_exceeded.update(a["exceeded_parameters"])

    by_state: Dict[str, Dict] = {}
    for r, a in zip(records, assessed):
        s = r.get("state", "Unknown")
        if s not in by_state:
            by_state[s] = {"safe": 0, "moderate": 0, "unsuitable": 0, "total": 0}
        by_state[s]["total"] += 1
        status = a["overall_status"]
        if status in by_state[s]:
            by_state[s][status] += 1

    return {
        "total_samples": count,
        "safe": statuses.count("safe"),
        "moderate": statuses.count("moderate"),
        "unsuitable": statuses.count("unsuitable"),
        "exceeded_parameters": list(all_exceeded),
        "by_state": by_state,
    }


@router.post("/ingest")
async def ingest_quality_data(
    records: List[Dict[str, Any]],
    user: Dict[str, Any] = require_admin,
):
    """Ingest water quality records (admin only)."""
    if len(records) > 100:
        raise HTTPException(status_code=400, detail="Max 100 records per batch")

    required_fields = ["state", "assessment_year"]
    for i, r in enumerate(records):
        for field in required_fields:
            if field not in r:
                raise HTTPException(status_code=400, detail=f"Record {i} missing '{field}'")

    result = sb_upsert("groundwater_quality", records, on_conflict="id")
    return {"status": "ingested", "count": len(records), "user": get_user_id(user)}
