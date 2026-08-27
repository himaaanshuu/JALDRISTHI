from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from dotenv import load_dotenv

load_dotenv()

from database import init_db, get_db, WaterReading, GroundWater, DataSource
from config import DB_PATH, USE_SUPABASE
from parser import parse_message, ChatIntent, KNOWN_STATES
from geo_resolver import resolve_location, resolve_state, get_all_states
from query_router import classify_query, QueryType
from numeric_calc import (
    compute_state_comparison, compute_trend, compute_rankings,
    compute_category_distribution, compute_risk_score, format_number
)
from smart_chat import smart_chat, smart_chat_streaming, get_session

OLLAMA_BIN = os.getenv(
    "OLLAMA_BIN",
    "/Applications/Ollama.app/Contents/Resources/ollama",
)
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not USE_SUPABASE:
        init_db()
    seed_demo_data()
    yield

app = FastAPI(title="JAL-DRISHTI AI", version="1.0.0", lifespan=lifespan)

# CORS configuration from environment
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.ngrok-free\.dev$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_demo_data():
    if USE_SUPABASE:
        from supabase_client import sb_count, sb_insert
        if sb_count("water_readings") == 0:
            import random
            stations = ["RIVER-01", "RIVER-02", "DAM-01", "LAKE-01"]
            readings = []
            for station in stations:
                for _ in range(10):
                    readings.append({
                        "station_id": station,
                        "water_level": round(random.uniform(2.0, 12.0), 2),
                        "rainfall_mm": round(random.uniform(0.0, 50.0), 2),
                        "ph_level": round(random.uniform(6.5, 8.5), 2),
                        "turbidity": round(random.uniform(1.0, 100.0), 2),
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": random.choice(["normal", "warning", "critical"]),
                    })
            sb_insert("water_readings", readings)
        return

    from database import SessionLocal
    db = SessionLocal()
    if db.query(WaterReading).count() == 0:
        import random
        stations = ["RIVER-01", "RIVER-02", "DAM-01", "LAKE-01"]
        for station in stations:
            for _ in range(10):
                db.add(WaterReading(
                    station_id=station,
                    water_level=round(random.uniform(2.0, 12.0), 2),
                    rainfall_mm=round(random.uniform(0.0, 50.0), 2),
                    ph_level=round(random.uniform(6.5, 8.5), 2),
                    turbidity=round(random.uniform(1.0, 100.0), 2),
                    timestamp=datetime.utcnow(),
                    status=random.choice(["normal", "warning", "critical"]),
                ))
        db.commit()
    db.close()


# ─── Pydantic Models ────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


class ReadingResponse(BaseModel):
    id: int
    station_id: str
    water_level: float
    rainfall_mm: float
    ph_level: float
    turbidity: float
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_stations: int
    total_readings: int
    alerts_active: int
    avg_water_level: float


class GroundWaterRecord(BaseModel):
    id: int
    state: str
    district: str
    block: str
    assessment_year: int
    annual_groundwater_recharge: float
    extractable_groundwater_resource: float
    groundwater_extraction: float
    extraction_stage: float
    category: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True


class StateInfo(BaseModel):
    state: str
    districts: int
    blocks: int
    latest_assessment_year: int
    avg_extraction_stage: float


class DistrictInfo(BaseModel):
    state: str
    district: str
    blocks: int
    latest_assessment_year: int
    avg_extraction_stage: float


class BlockInfo(BaseModel):
    state: str
    district: str
    block: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    latest_extraction_stage: float
    latest_category: str


class AssessmentRecord(BaseModel):
    id: int
    state: str
    district: str
    block: str
    assessment_year: int
    annual_groundwater_recharge: Optional[float] = 0
    extractable_groundwater_resource: Optional[float] = 0
    groundwater_extraction: float
    extraction_stage: float
    category: str

    class Config:
        from_attributes = True


class CategoryDistribution(BaseModel):
    category: str
    count: int
    percentage: float


class TopExtractionBlock(BaseModel):
    state: str
    district: str
    block: str
    assessment_year: int
    groundwater_extraction: float
    extraction_stage: float
    category: str


class TrendPoint(BaseModel):
    assessment_year: int
    total_extraction: float
    avg_extraction_stage: float
    total_recharge: float
    blocks_assessed: int


# ─── What Changed? Models ────────────────────────────────────────────────────

class BlockChange(BaseModel):
    block: str
    district: str
    state: str
    old_category: str
    new_category: str
    old_extraction: float
    new_extraction: float
    extraction_change_pct: float
    change_type: str  # "improved" | "deteriorated" | "unchanged"


class WhatChangedResponse(BaseModel):
    state: str
    year1: int
    year2: int
    total_blocks_y1: int
    total_blocks_y2: int
    extraction_change_pct: float
    avg_stage_y1: float
    avg_stage_y2: float
    stage_change_pct: float
    improvements: int
    deteriorations: int
    unchanged: int
    category_shifts: dict  # {"Safe → Critical": 2, ...}
    overall_trend: str  # "improving" | "deteriorating" | "stable"
    block_changes: List[BlockChange]


# ─── Risk Score Models ───────────────────────────────────────────────────────

class RiskFactor(BaseModel):
    factor: str
    contribution: float  # points added to base score
    description: str


class RiskScoreResponse(BaseModel):
    state: str
    year: int
    risk_score: int  # 0-100
    risk_level: str  # "Low" | "Medium" | "High" | "Critical"
    avg_extraction_stage: float
    dominant_category: str
    trend_direction: str  # "improving" | "deteriorating" | "stable"
    factors: List[RiskFactor]
    disclaimer: str = "AI-derived analytical indicator. Not an official INGRES/CGWB classification."


# ─── Health & Dashboard ─────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        service="JAL-DRISHTI AI",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
    )


# ─── Data Source & Coverage ────────────────────────────────────────────────

class DataSourceInfo(BaseModel):
    id: int
    source_name: str
    source_url: str
    organization: str
    assessment_year: int
    publication_year: int
    retrieved_at: str
    dataset_description: str
    record_count: int


class DataCoverageResponse(BaseModel):
    total_records: int
    official_records: int
    demo_records: int
    assessment_years: List[int]
    states_covered: int
    districts_covered: int
    blocks_covered: int
    total_recharge: float
    total_extraction: float
    avg_extraction_stage: float
    sources: List[DataSourceInfo]


@app.get("/api/data/coverage", response_model=DataCoverageResponse)
def get_data_coverage(db: Session = Depends(get_db)):
    total = db.query(GroundWater).count()
    official = db.query(GroundWater).filter(GroundWater.is_demo_data == 0).count()
    demo = db.query(GroundWater).filter(GroundWater.is_demo_data == 1).count()

    years = sorted([
        y[0] for y in db.query(GroundWater.assessment_year).distinct().all() if y[0]
    ])
    states = db.query(func.count(func.distinct(GroundWater.state))).scalar() or 0
    districts = db.query(func.count(func.distinct(GroundWater.district))).filter(
        GroundWater.district != ""
    ).scalar() or 0
    blocks = db.query(func.count(func.distinct(GroundWater.block))).filter(
        GroundWater.block != ""
    ).scalar() or 0

    # Aggregate groundwater metrics
    total_recharge = db.query(func.sum(GroundWater.annual_groundwater_recharge)).scalar() or 0.0
    total_extraction = db.query(func.sum(GroundWater.groundwater_extraction)).scalar() or 0.0
    avg_stage = db.query(func.avg(GroundWater.extraction_stage)).scalar() or 0.0

    # Get source info with record counts
    sources = []
    for src in db.query(DataSource).all():
        src_count = db.query(GroundWater).filter(GroundWater.source_id == src.id).count()
        sources.append(DataSourceInfo(
            id=src.id,
            source_name=src.source_name,
            source_url=src.source_url,
            organization=src.organization,
            assessment_year=src.assessment_year or 0,
            publication_year=src.publication_year or 0,
            retrieved_at=src.retrieved_at or "",
            dataset_description=src.dataset_description or "",
            record_count=src_count,
        ))

    return DataCoverageResponse(
        total_records=total,
        official_records=official,
        demo_records=demo,
        assessment_years=years,
        states_covered=states,
        districts_covered=districts,
        blocks_covered=blocks,
        total_recharge=round(total_recharge, 2),
        total_extraction=round(total_extraction, 2),
        avg_extraction_stage=round(avg_stage, 1),
        sources=sources,
    )


@app.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_readings = db.query(WaterReading).count()
    total_stations = db.query(WaterReading.station_id).distinct().count()
    alerts = db.query(WaterReading).filter(
        WaterReading.status.in_(["warning", "critical"])
    ).count()
    avg_level = db.query(func.avg(WaterReading.water_level)).scalar() or 0.0

    return DashboardStats(
        total_stations=total_stations,
        total_readings=total_readings,
        alerts_active=alerts,
        avg_water_level=round(float(avg_level), 2),
    )


@app.get("/api/readings", response_model=List[ReadingResponse])
def get_readings(db: Session = Depends(get_db)):
    return db.query(WaterReading).order_by(WaterReading.timestamp.desc()).limit(50).all()


# ─── Groundwater: Reference Data ────────────────────────────────────────────

@app.get("/api/states", response_model=List[StateInfo])
def get_states(db: Session = Depends(get_db)):
    rows = (
        db.query(
            GroundWater.state,
            func.count(func.distinct(GroundWater.district)).label("districts"),
            func.count(func.distinct(GroundWater.block)).label("blocks"),
            func.max(GroundWater.assessment_year).label("latest_year"),
            func.avg(GroundWater.extraction_stage).label("avg_stage"),
        )
        .group_by(GroundWater.state)
        .order_by(GroundWater.state)
        .all()
    )
    return [
        StateInfo(
            state=r.state,
            districts=r.districts,
            blocks=r.blocks,
            latest_assessment_year=r.latest_year,
            avg_extraction_stage=round(float(r.avg_stage), 2),
        )
        for r in rows
    ]


@app.get("/api/districts", response_model=List[DistrictInfo])
def get_districts(
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db),
):
    query = db.query(
        GroundWater.state,
        GroundWater.district,
        func.count(func.distinct(GroundWater.block)).label("blocks"),
        func.max(GroundWater.assessment_year).label("latest_year"),
        func.avg(GroundWater.extraction_stage).label("avg_stage"),
    ).group_by(GroundWater.state, GroundWater.district)

    if state:
        query = query.filter(GroundWater.state == state)

    rows = query.order_by(GroundWater.state, GroundWater.district).all()

    return [
        DistrictInfo(
            state=r.state,
            district=r.district,
            blocks=r.blocks,
            latest_assessment_year=r.latest_year,
            avg_extraction_stage=round(float(r.avg_stage), 2),
        )
        for r in rows
    ]


@app.get("/api/blocks", response_model=List[BlockInfo])
def get_blocks(
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    db: Session = Depends(get_db),
):
    subq = (
        db.query(
            GroundWater.state,
            GroundWater.district,
            GroundWater.block,
            func.max(GroundWater.assessment_year).label("max_year"),
        )
        .group_by(GroundWater.state, GroundWater.district, GroundWater.block)
        .subquery()
    )

    query = (
        db.query(GroundWater)
        .join(
            subq,
            (GroundWater.state == subq.c.state)
            & (GroundWater.district == subq.c.district)
            & (GroundWater.block == subq.c.block)
            & (GroundWater.assessment_year == subq.c.max_year),
        )
        .order_by(GroundWater.state, GroundWater.district, GroundWater.block)
    )

    if state:
        query = query.filter(GroundWater.state == state)
    if district:
        query = query.filter(GroundWater.district == district)

    rows = query.filter(
        GroundWater.latitude.isnot(None),
        GroundWater.longitude.isnot(None),
        GroundWater.district != "",
    ).all()

    return [
        BlockInfo(
            state=r.state,
            district=r.district,
            block=r.block,
            latitude=r.latitude,
            longitude=r.longitude,
            latest_extraction_stage=r.extraction_stage,
            latest_category=r.category,
        )
        for r in rows
    ]


# ─── Groundwater: Assessments ───────────────────────────────────────────────

@app.get("/api/assessments", response_model=List[AssessmentRecord])
def get_assessments(
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    block: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(200, le=5000),
    db: Session = Depends(get_db),
):
    query = db.query(GroundWater)

    if state:
        query = query.filter(GroundWater.state == state)
    if district:
        query = query.filter(GroundWater.district == district)
    if block:
        query = query.filter(GroundWater.block == block)
    if year:
        query = query.filter(GroundWater.assessment_year == year)
    if category:
        query = query.filter(GroundWater.category == category)

    rows = (
        query.order_by(
            GroundWater.state, GroundWater.district, GroundWater.block, GroundWater.assessment_year
        )
        .limit(limit)
        .all()
    )

    return [
        AssessmentRecord(
            id=r.id,
            state=r.state,
            district=r.district,
            block=r.block,
            assessment_year=r.assessment_year,
            annual_groundwater_recharge=r.annual_groundwater_recharge,
            extractable_groundwater_resource=r.extractable_groundwater_resource,
            groundwater_extraction=r.groundwater_extraction,
            extraction_stage=r.extraction_stage,
            category=r.category,
        )
        for r in rows
    ]


@app.get("/api/assessment/latest", response_model=List[AssessmentRecord])
def get_assessment_latest(
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    block: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    latest_year = db.query(func.max(GroundWater.assessment_year)).scalar()
    if not latest_year:
        return []

    query = db.query(GroundWater).filter(GroundWater.assessment_year == latest_year)

    if state:
        query = query.filter(GroundWater.state == state)
    if district:
        query = query.filter(GroundWater.district == district)
    if block:
        query = query.filter(GroundWater.block == block)

    rows = query.order_by(GroundWater.state, GroundWater.district, GroundWater.block).all()

    return [
        AssessmentRecord(
            id=r.id,
            state=r.state,
            district=r.district,
            block=r.block,
            assessment_year=r.assessment_year,
            annual_groundwater_recharge=r.annual_groundwater_recharge,
            extractable_groundwater_resource=r.extractable_groundwater_resource,
            groundwater_extraction=r.groundwater_extraction,
            extraction_stage=r.extraction_stage,
            category=r.category,
        )
        for r in rows
    ]


@app.get("/api/assessment/history", response_model=List[AssessmentRecord])
def get_assessment_history(
    state: str = Query(..., description="State name (required)"),
    district: str = Query(..., description="District name (required)"),
    block: str = Query(..., description="Block name (required)"),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(GroundWater)
        .filter(
            GroundWater.state == state,
            GroundWater.district == district,
            GroundWater.block == block,
        )
        .order_by(GroundWater.assessment_year)
        .all()
    )

    return [
        AssessmentRecord(
            id=r.id,
            state=r.state,
            district=r.district,
            block=r.block,
            assessment_year=r.assessment_year,
            annual_groundwater_recharge=r.annual_groundwater_recharge,
            extractable_groundwater_resource=r.extractable_groundwater_resource,
            groundwater_extraction=r.groundwater_extraction,
            extraction_stage=r.extraction_stage,
            category=r.category,
        )
        for r in rows
    ]


# ─── Groundwater: Analytics ─────────────────────────────────────────────────

@app.get("/api/analytics/category-distribution", response_model=List[CategoryDistribution])
def get_category_distribution(
    state: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GroundWater.category, func.count().label("count"))

    if state:
        query = query.filter(GroundWater.state == state)
    if year:
        query = query.filter(GroundWater.assessment_year == year)

    rows = query.group_by(GroundWater.category).all()
    total = sum(r.count for r in rows)

    return [
        CategoryDistribution(
            category=r.category,
            count=r.count,
            percentage=round((r.count / total) * 100, 1) if total > 0 else 0.0,
        )
        for r in rows
    ]


@app.get("/api/analytics/top-extraction", response_model=List[TopExtractionBlock])
def get_top_extraction(
    state: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    if not year:
        latest = db.query(func.max(GroundWater.assessment_year)).scalar()
        year = latest

    query = (
        db.query(GroundWater)
        .filter(GroundWater.assessment_year == year)
        .filter(GroundWater.district != "")
        .filter(GroundWater.block != "")
    )

    if state:
        query = query.filter(GroundWater.state == state)

    rows = (
        query.order_by(desc(GroundWater.groundwater_extraction))
        .limit(limit)
        .all()
    )

    return [
        TopExtractionBlock(
            state=r.state,
            district=r.district,
            block=r.block,
            assessment_year=r.assessment_year,
            groundwater_extraction=r.groundwater_extraction,
            extraction_stage=r.extraction_stage,
            category=r.category,
        )
        for r in rows
    ]


@app.get("/api/analytics/trend", response_model=List[TrendPoint])
def get_trend(
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(
        GroundWater.assessment_year,
        func.sum(GroundWater.groundwater_extraction).label("total_extraction"),
        func.avg(GroundWater.extraction_stage).label("avg_stage"),
        func.sum(GroundWater.annual_groundwater_recharge).label("total_recharge"),
        func.count(func.distinct(GroundWater.block)).label("blocks"),
    ).filter(
        GroundWater.groundwater_extraction.isnot(None),
        GroundWater.annual_groundwater_recharge.isnot(None),
    )

    if state:
        query = query.filter(GroundWater.state == state)
    if district:
        query = query.filter(GroundWater.district == district)

    rows = (
        query.group_by(GroundWater.assessment_year)
        .order_by(GroundWater.assessment_year)
        .all()
    )

    return [
        TrendPoint(
            assessment_year=r.assessment_year,
            total_extraction=round(float(r.total_extraction), 2),
            avg_extraction_stage=round(float(r.avg_stage), 2),
            total_recharge=round(float(r.total_recharge), 2),
            blocks_assessed=r.blocks,
        )
        for r in rows
    ]


@app.get("/api/analytics/what-changed", response_model=WhatChangedResponse)
def get_what_changed(
    state: str = Query(...),
    year1: int = Query(...),
    year2: int = Query(...),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    CATEGORY_ORDER = {"Safe": 0, "Semi-Critical": 1, "Critical": 2, "Over-Exploited": 3}

    # Get blocks for year1
    q1 = db.query(GroundWater).filter(
        GroundWater.state == state,
        GroundWater.assessment_year == year1,
    )
    if district:
        q1 = q1.filter(GroundWater.district == district)
    rows1 = q1.all()

    # Get blocks for year2
    q2 = db.query(GroundWater).filter(
        GroundWater.state == state,
        GroundWater.assessment_year == year2,
    )
    if district:
        q2 = q2.filter(GroundWater.district == district)
    rows2 = q2.all()

    if not rows1 or not rows2:
        return WhatChangedResponse(
            state=state, year1=year1, year2=year2,
            total_blocks_y1=len(rows1), total_blocks_y2=len(rows2),
            extraction_change_pct=0, avg_stage_y1=0, avg_stage_y2=0,
            stage_change_pct=0, improvements=0, deteriorations=0, unchanged=0,
            category_shifts={}, overall_trend="stable", block_changes=[],
        )

    # Build lookup: (state, district, block) → row
    lookup1 = {(r.state, r.district, r.block): r for r in rows1}
    lookup2 = {(r.state, r.district, r.block): r for r in rows2}
    all_keys = set(lookup1.keys()) | set(lookup2.keys())

    # Calculate block-level changes
    block_changes = []
    improvements = 0
    deteriorations = 0
    unchanged = 0
    category_shifts: dict[str, int] = {}

    for key in all_keys:
        r1 = lookup1.get(key)
        r2 = lookup2.get(key)

        if r1 and r2:
            old_cat = r1.category
            new_cat = r2.category
            old_ext = r1.groundwater_extraction
            new_ext = r2.groundwater_extraction
            ext_change = ((new_ext - old_ext) / old_ext * 100) if old_ext else 0

            cat1_rank = CATEGORY_ORDER.get(old_cat, -1)
            cat2_rank = CATEGORY_ORDER.get(new_cat, -1)

            if cat2_rank < cat1_rank:
                change_type = "improved"
                improvements += 1
            elif cat2_rank > cat1_rank:
                change_type = "deteriorated"
                deteriorations += 1
            else:
                change_type = "unchanged"
                unchanged += 1

            shift_key = f"{old_cat} → {new_cat}"
            if old_cat != new_cat:
                category_shifts[shift_key] = category_shifts.get(shift_key, 0) + 1

            block_changes.append(BlockChange(
                block=r2.block,
                district=r2.district,
                state=r2.state,
                old_category=old_cat,
                new_category=new_cat,
                old_extraction=round(old_ext, 1),
                new_extraction=round(new_ext, 1),
                extraction_change_pct=round(ext_change, 1),
                change_type=change_type,
            ))
        elif r2:
            # New block in year2
            block_changes.append(BlockChange(
                block=r2.block, district=r2.district, state=r2.state,
                old_category="N/A", new_category=r2.category,
                old_extraction=0, new_extraction=round(r2.groundwater_extraction, 1),
                extraction_change_pct=0, change_type="new",
            ))

    # Aggregate stats
    ext1 = sum(r.groundwater_extraction for r in rows1)
    ext2 = sum(r.groundwater_extraction for r in rows2)
    extraction_change_pct = ((ext2 - ext1) / ext1 * 100) if ext1 else 0

    avg_stage1 = sum(r.extraction_stage for r in rows1) / len(rows1) if rows1 else 0
    avg_stage2 = sum(r.extraction_stage for r in rows2) / len(rows2) if rows2 else 0
    stage_change_pct = ((avg_stage2 - avg_stage1) / avg_stage1 * 100) if avg_stage1 else 0

    # Overall trend
    if improvements > deteriorations:
        overall_trend = "improving"
    elif deteriorations > improvements:
        overall_trend = "deteriorating"
    else:
        overall_trend = "stable"

    # Sort block changes: deteriorated first, then unchanged, then improved
    sort_order = {"deteriorated": 0, "new": 1, "unchanged": 2, "improved": 3}
    block_changes.sort(key=lambda x: (sort_order.get(x.change_type, 4), -abs(x.extraction_change_pct)))

    return WhatChangedResponse(
        state=state,
        year1=year1,
        year2=year2,
        total_blocks_y1=len(rows1),
        total_blocks_y2=len(rows2),
        extraction_change_pct=round(extraction_change_pct, 1),
        avg_stage_y1=round(avg_stage1, 1),
        avg_stage_y2=round(avg_stage2, 1),
        stage_change_pct=round(stage_change_pct, 1),
        improvements=improvements,
        deteriorations=deteriorations,
        unchanged=unchanged,
        category_shifts=category_shifts,
        overall_trend=overall_trend,
        block_changes=block_changes,
    )


@app.get("/api/analytics/risk-score", response_model=RiskScoreResponse)
def get_risk_score(
    state: str = Query(...),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Calculate AI-derived groundwater risk score (0-100).

    Scoring methodology:
    - Base score from extraction stage (0-40 points)
    - Category penalty (0-30 points)
    - Trend adjustment (-15 to +15 points)
    - Concentration factor (0-15 points)

    0-25: Low Risk | 26-50: Medium Risk | 51-75: High Risk | 76-100: Critical Risk
    """
    CATEGORY_RISK = {
        "Safe": 0,
        "Semi-Critical": 15,
        "Critical": 25,
        "Over-Exploited": 30,
    }

    if not year:
        year = db.query(func.max(GroundWater.assessment_year)).scalar()
    if not year:
        return RiskScoreResponse(
            state=state, year=0, risk_score=0, risk_level="Low",
            avg_extraction_stage=0, dominant_category="Safe",
            trend_direction="stable", factors=[],
        )

    rows = db.query(GroundWater).filter(
        GroundWater.state == state,
        GroundWater.assessment_year == year,
    ).all()

    if not rows:
        return RiskScoreResponse(
            state=state, year=year, risk_score=0, risk_level="Low",
            avg_extraction_stage=0, dominant_category="Safe",
            trend_direction="stable", factors=[],
        )

    factors: List[RiskFactor] = []
    score = 0.0

    # 1. Extraction Stage Score (0-40 points)
    avg_stage = sum(r.extraction_stage for r in rows) / len(rows)
    if avg_stage >= 100:
        stage_pts = 40
    elif avg_stage >= 90:
        stage_pts = 35
    elif avg_stage >= 70:
        stage_pts = 20 + (avg_stage - 70) * 0.75
    elif avg_stage >= 50:
        stage_pts = 10 + (avg_stage - 50) * 0.5
    else:
        stage_pts = avg_stage * 0.2
    score += stage_pts
    factors.append(RiskFactor(
        factor="Extraction Stage",
        contribution=round(stage_pts, 1),
        description=f"Average extraction stage: {avg_stage:.1f}%",
    ))

    # 2. Category Penalty (0-30 points)
    cat_counts = {}
    for r in rows:
        cat_counts[r.category] = cat_counts.get(r.category, 0) + 1
    total_blocks = len(rows)

    dominant_cat = max(cat_counts, key=cat_counts.get) if cat_counts else "Safe"
    cat_pts = CATEGORY_RISK.get(dominant_cat, 0)

    # Add penalty for over-exploited blocks
    oe_count = cat_counts.get("Over-Exploited", 0)
    if oe_count > 0:
        oe_penalty = (oe_count / total_blocks) * 10
        cat_pts = min(30, cat_pts + oe_penalty)

    score += cat_pts
    factors.append(RiskFactor(
        factor="Category Distribution",
        contribution=round(cat_pts, 1),
        description=f"Dominant category: {dominant_cat} ({cat_counts.get(dominant_cat, 0)}/{total_blocks} blocks)",
    ))

    # 3. Trend Adjustment (-15 to +15 points)
    prev_year = year - 1
    prev_rows = db.query(GroundWater).filter(
        GroundWater.state == state,
        GroundWater.assessment_year == prev_year,
    ).all()

    if prev_rows:
        prev_avg_stage = sum(r.extraction_stage for r in prev_rows) / len(prev_rows)
        stage_change = avg_stage - prev_avg_stage

        if stage_change > 5:
            trend_pts = 15
            trend_desc = f"Deteriorating: +{stage_change:.1f}% stage increase from {prev_year}"
            trend_dir = "deteriorating"
        elif stage_change > 2:
            trend_pts = 8
            trend_desc = f"Slight deterioration: +{stage_change:.1f}% stage increase"
            trend_dir = "deteriorating"
        elif stage_change < -5:
            trend_pts = -15
            trend_desc = f"Improving: {stage_change:.1f}% stage decrease from {prev_year}"
            trend_dir = "improving"
        elif stage_change < -2:
            trend_pts = -8
            trend_desc = f"Slight improvement: {stage_change:.1f}% stage decrease"
            trend_dir = "improving"
        else:
            trend_pts = 0
            trend_desc = f"Stable: {stage_change:+.1f}% change from {prev_year}"
            trend_dir = "stable"
    else:
        trend_pts = 0
        trend_desc = "No historical data for trend comparison"
        trend_dir = "stable"

    score += trend_pts
    factors.append(RiskFactor(
        factor="Historical Trend",
        contribution=round(trend_pts, 1),
        description=trend_desc,
    ))

    # 4. Concentration Factor (0-15 points)
    # High concentration of risk in few blocks is better than widespread risk
    critical_blocks = sum(1 for r in rows if r.category in ("Critical", "Over-Exploited"))
    if total_blocks > 0:
        concentration = critical_blocks / total_blocks
        if concentration > 0.5:
            conc_pts = 15
        elif concentration > 0.3:
            conc_pts = 10
        elif concentration > 0.1:
            conc_pts = 5
        else:
            conc_pts = 0
    else:
        conc_pts = 0

    score += conc_pts
    factors.append(RiskFactor(
        factor="Risk Concentration",
        contribution=round(conc_pts, 1),
        description=f"{critical_blocks}/{total_blocks} blocks in Critical/Over-Exploited categories",
    ))

    # Clamp score to 0-100
    final_score = max(0, min(100, round(score)))

    # Determine risk level
    if final_score <= 25:
        risk_level = "Low"
    elif final_score <= 50:
        risk_level = "Medium"
    elif final_score <= 75:
        risk_level = "High"
    else:
        risk_level = "Critical"

    return RiskScoreResponse(
        state=state,
        year=year,
        risk_score=final_score,
        risk_level=risk_level,
        avg_extraction_stage=round(avg_stage, 1),
        dominant_category=dominant_cat,
        trend_direction=trend_dir,
        factors=factors,
    )


# ─── Chat / AI Assistant ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatSource(BaseModel):
    title: str
    endpoint: str
    record_count: int
    data: list


class Evidence(BaseModel):
    source: str = "Central Ground Water Board / IN-GRES"
    assessment_year: Optional[int] = None
    location: str = "All India"
    records_used: int = 0
    confidence: str = "Medium"  # High / Medium / Low
    source_url: str = "https://cgwb.gov.in/en/ground-water-resource-assessment-0"
    data_type: str = "official"  # "official" | "synthetic" | "mixed"


class ChartData(BaseModel):
    type: str  # "line" | "bar" | "pie"
    title: str
    data: list  # list of dicts for Recharts


class ParsedIntent(BaseModel):
    intent: str = "general"
    state: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    year: Optional[int] = None
    comparison_years: List[int] = []
    metric: Optional[str] = None
    category: Optional[str] = None
    confidence: float = 0.0
    language: str = "english"


# ─── Hindi/Hinglish Translations ─────────────────────────────────────────────

# Word-level replacements for response text
HI_WORD_MAP = {
    "Groundwater Status": "भूजल स्थिति",
    "groundwater status": "भूजल स्थिति",
    "Total Extraction": "कुल निकासी",
    "Total Recharge": "कुल रिचार्ज",
    "Avg Stage": "औसत चरण",
    "Total Blocks": "कुल ब्लॉक",
    "blocks assessed across": "ब्लॉकों का मूल्यांकन",
    "Category Breakdown:": "श्रेणी विवरण:",
    "Assessment Year:": "मूल्यांकन वर्ष:",
    "Extraction:": "निकासी:",
    "Stage:": "चरण:",
    "Recharge:": "रिचार्ज:",
    "Ratio:": "अनुपात:",
    "Average": "औसत",
    "Total": "कुल",
    "Safe": "सुरक्षित",
    "Semi-Critical": "अर्ध-गंभीर",
    "Critical": "गंभीर",
    "Over-Exploited": "अत्यधिक दोहन",
    "The data shows that groundwater extraction is within sustainable limits.":
        "डेटा दर्शाता है कि भूजल निकासी टिकाऊ सीमाओं के भीतर है।",
    "The data shows that groundwater extraction is above sustainable limits.":
        "डेटा दर्शाता है कि भूजल निकासी टिकाऊ सीमाओं से अधिक है।",
    "These regions show the highest extraction volumes and may require monitoring.":
        "ये क्षेत्र सबसे अधिक निकासी मात्रा दिखाते हैं और निगरानी की आवश्यकता हो सकती है।",
    "These areas have extraction rates approaching or exceeding sustainable limits. Immediate monitoring and regulation are recommended.":
        "इन क्षेत्रों में निकासी दरें टिकाऊ सीमाओं के करीब या उससे अधिक हैं। तत्काल निगरानी और विनियमन की सिफारिश की जाती है।",
    "This indicates increasing groundwater stress.":
        "यह बढ़ते भूजल तनाव को दर्शाता है।",
    "This shows improving water management.":
        "यह बेहतर जल प्रबंधन दर्शाता है।",
    "Overall Change:": "कुल परिवर्तन:",
    "extraction": "निकासी",
    "recharge": "रिचार्ज",
    "stage": "चरण",
    "blocks": "ब्लॉक",
}

# Full-sentence translations for greetings and error messages
HI_FULL_MAP = {
    "Hello! I'm the JAL-DRISHTI AI Assistant. I can help you analyze official CGWB/IN-GRES groundwater assessment data across India.\n\nData Source: Central Ground Water Board (CGWB), Ministry of Jal Shakti\nAssessment Years: 2024, 2025\nCoverage: All 36 States/UTs, 200+ districts\n\nTry asking me about:\n- Groundwater status of any state\n- Comparisons between years\n- Districts with highest extraction\n- Over-exploited or critical areas":
        "नमस्ते! मैं JAL-DRISHTI AI सहायक हूँ। मैं भारत के सभी 36 राज्यों/केंद्र शासित प्रदेशों, 200+ जिलों में आधिकारिक CGWB/IN-GRES भूजल मूल्यांकन डेटा का विश्लेषण करने में आपकी मदद कर सकता हूँ।\n\nडेटा स्रोत: केंद्रीय भूजल बोर्ड (CGWB), जल शक्ति मंत्रालय\nमूल्यांकन वर्ष: 2024, 2025\n\nमुझसे पूछें:\n- किसी भी राज्य की भूजल स्थिति\n- वर्षों के बीच तुलना\n- सबसे ज्यादा दोहन वाले जिले\n- अत्यधिक दोहन या गंभीर क्षेत्र",
    "Please specify a state. Example: `What is the groundwater status of Rajasthan?`":
        "कृपया एक राज्य बताएं। उदाहरण: `राजस्थान में भूजल स्थिति क्या है?`",
    "No data available.":
        "कोई डेटा उपलब्ध नहीं है।",
    "No extraction data found.":
        "कोई निकासी डेटा नहीं मिला।",
    "No trend data available.":
        "कोई प्रवृत्ति डेटा उपलब्ध नहीं है।",
    "No category data available.":
        "कोई श्रेणी डेटा उपलब्ध नहीं है।",
    "Please specify a state and two years. Example:\n`Compare Gujarat between 2020 and 2024.`":
        "कृपया एक राज्य और दो वर्ष बताएं। उदाहरण:\n`गुजरात की तुलना 2020 और 2024 के बीच करें।`",
    "I'm not sure I understood that question.":
        "मुझे यकीन नहीं है कि मैंने यह प्रश्न समझा।",
}

# Followup translations
HI_FOLLOWUP_MAP = {
    "What is the groundwater status of Rajasthan?": "राजस्थान में भूजल स्थिति क्या है?",
    "Compare Gujarat between 2020 and 2024.": "गुजरात की तुलना 2020 और 2024 के बीच करें।",
    "Which districts have the highest extraction?": "कौन से जिलों में सबसे ज्यादा निकासी है?",
    "Show over-exploited areas.": "अत्यधिक दोहन वाले क्षेत्र दिखाएं।",
    "Show over-exploited areas in Punjab.": "पंजाब में अत्यधिक दोहन वाले क्षेत्र दिखाएं।",
    "What is the extraction trend?": "निकासी प्रवृत्ति क्या है?",
    "Show category distribution.": "श्रेणी वितरण दिखाएं।",
    "Show extraction trend over time.": "समय के साथ निकासी प्रवृत्ति दिखाएं।",
    "What is the overall category distribution?": "समग्र श्रेणी वितरण क्या है?",
    "Which districts have highest extraction?": "कौन से जिलों में सबसे ज्यादा निकासी है?",
}

# Patterns for dynamic followups (English pattern → Hindi replacement)
HI_FOLLOWUP_PATTERNS = [
    ("Compare {state} between 2020 and 2024.", "{state} की तुलना 2020 और 2024 के बीच करें।"),
    ("What is the groundwater status of {state}?", "{state} में भूजल स्थिति क्या है?"),
    ("Which districts in {state} have highest extraction?", "{state} में कौन से जिलों में सबसे ज्यादा निकासी है?"),
    ("Show trend for {state}.", "{state} के लिए प्रवृत्ति दिखाएं।"),
    ("Show districts in {state}.", "{state} में जिले दिखाएं।"),
    ("Show blocks in {state}.", "{state} में ब्लॉक दिखाएं।"),
    ("Compare {state} between {y1} and {y2}.", "{state} की तुलना {y1} और {y2} के बीच करें।"),
    ("Show category distribution for {state}.", "{state} के लिए श्रेणी वितरण दिखाएं।"),
    ("Show over-exploited areas in {state}.", "{state} में अत्यधिक दोहन वाले क्षेत्र दिखाएं।"),
]


def translate_reply(text: str, language: str) -> str:
    """Translate an English reply to Hindi/Hinglish if needed."""
    if language not in ("hindi", "hinglish"):
        return text

    # Try exact full-sentence match first
    if text in HI_FULL_MAP:
        return HI_FULL_MAP[text]

    # Apply word-level replacements (longest first to avoid partial matches)
    for en, hi in sorted(HI_WORD_MAP.items(), key=lambda x: -len(x[0])):
        text = text.replace(en, hi)

    return text


def translate_followups(followups: List[str], language: str) -> List[str]:
    """Translate follow-up suggestions to Hindi/Hinglish if needed."""
    if language not in ("hindi", "hinglish"):
        return followups

    import re as _re

    translated = []
    for f in followups:
        # Try exact match first
        if f in HI_FOLLOWUP_MAP:
            translated.append(HI_FOLLOWUP_MAP[f])
            continue

        # Try pattern matching for dynamic followups
        matched = False
        for pattern, replacement in HI_FOLLOWUP_PATTERNS:
            # Convert pattern to regex: {state} → capture group
            regex_pattern = _re.escape(pattern).replace(r"\{state\}", r"(.+?)").replace(r"\{y1\}", r"(\d{4})").replace(r"\{y2\}", r"(\d{4})")
            m = _re.fullmatch(regex_pattern, f)
            if m:
                result = replacement
                for i, group in enumerate(m.groups(), 1):
                    result = result.replace(f"{{{['state','y1','y2'][i-1]}}}", group)
                translated.append(result)
                matched = True
                break

        if not matched:
            translated.append(f)

    return translated


class ChatResponse(BaseModel):
    reply: str
    sources: List[ChatSource]
    suggested_followups: List[str]
    parsed_intent: ParsedIntent = ParsedIntent()
    chart: Optional[ChartData] = None
    evidence: Optional[Evidence] = None
    risk_score: Optional[RiskScoreResponse] = None


def _evidence(
    year: Optional[int] = None,
    location: str = "All India",
    records: int = 0,
    confidence: str = "Medium",
    endpoint: str = "/api/assessments",
    data_type: str = "official",
) -> Evidence:
    """Build an Evidence object for a chat response."""
    source_label = "Central Ground Water Board / IN-GRES"
    source_url = "https://cgwb.gov.in/en/ground-water-resource-assessment-0"

    if year:
        source_label += f" — Assessment Year {year}"
        source_url = f"https://cgwb.gov.in/en/ground-water-resource-assessment-0"

    return Evidence(
        source=source_label,
        assessment_year=year,
        location=location,
        records_used=records,
        confidence=confidence,
        source_url=source_url,
        data_type=data_type,
    )


def _confidence_from_records(n: int) -> str:
    """Map record count to confidence label."""
    if n >= 8:
        return "High"
    if n >= 4:
        return "Medium"
    return "Low"


def _calc_risk_score(db: Session, state: str, year: int) -> Optional[RiskScoreResponse]:
    """Calculate risk score for a state/year. Returns None if no data."""
    CATEGORY_RISK = {"Safe": 0, "Semi-Critical": 15, "Critical": 25, "Over-Exploited": 30}

    rows = db.query(GroundWater).filter(
        GroundWater.state == state,
        GroundWater.assessment_year == year,
    ).all()
    if not rows:
        return None

    factors: List[RiskFactor] = []
    score = 0.0

    # 1. Extraction Stage (0-40)
    avg_stage = sum(r.extraction_stage for r in rows) / len(rows)
    if avg_stage >= 100:
        stage_pts = 40
    elif avg_stage >= 90:
        stage_pts = 35
    elif avg_stage >= 70:
        stage_pts = 20 + (avg_stage - 70) * 0.75
    elif avg_stage >= 50:
        stage_pts = 10 + (avg_stage - 50) * 0.5
    else:
        stage_pts = avg_stage * 0.2
    score += stage_pts
    factors.append(RiskFactor(factor="Extraction Stage", contribution=round(stage_pts, 1),
                              description=f"Average extraction stage: {avg_stage:.1f}%"))

    # 2. Category (0-30)
    cat_counts = {}
    for r in rows:
        cat_counts[r.category] = cat_counts.get(r.category, 0) + 1
    total_blocks = len(rows)
    dominant_cat = max(cat_counts, key=cat_counts.get) if cat_counts else "Safe"
    cat_pts = CATEGORY_RISK.get(dominant_cat, 0)
    oe_count = cat_counts.get("Over-Exploited", 0)
    if oe_count > 0:
        cat_pts = min(30, cat_pts + (oe_count / total_blocks) * 10)
    score += cat_pts
    factors.append(RiskFactor(factor="Category Distribution", contribution=round(cat_pts, 1),
                              description=f"Dominant: {dominant_cat} ({cat_counts.get(dominant_cat, 0)}/{total_blocks} blocks)"))

    # 3. Trend (-15 to +15)
    prev_rows = db.query(GroundWater).filter(
        GroundWater.state == state, GroundWater.assessment_year == year - 1
    ).all()
    if prev_rows:
        prev_avg = sum(r.extraction_stage for r in prev_rows) / len(prev_rows)
        change = avg_stage - prev_avg
        if change > 5:
            trend_pts, trend_dir, trend_desc = 15, "deteriorating", f"+{change:.1f}% from {year-1}"
        elif change > 2:
            trend_pts, trend_dir, trend_desc = 8, "deteriorating", f"+{change:.1f}% from {year-1}"
        elif change < -5:
            trend_pts, trend_dir, trend_desc = -15, "improving", f"{change:.1f}% from {year-1}"
        elif change < -2:
            trend_pts, trend_dir, trend_desc = -8, "improving", f"{change:.1f}% from {year-1}"
        else:
            trend_pts, trend_dir, trend_desc = 0, "stable", f"{change:+.1f}% from {year-1}"
    else:
        trend_pts, trend_dir, trend_desc = 0, "stable", "No historical data"
    score += trend_pts
    factors.append(RiskFactor(factor="Historical Trend", contribution=round(trend_pts, 1), description=trend_desc))

    # 4. Concentration (0-15)
    critical_blocks = sum(1 for r in rows if r.category in ("Critical", "Over-Exploited"))
    concentration = critical_blocks / total_blocks if total_blocks else 0
    conc_pts = 15 if concentration > 0.5 else 10 if concentration > 0.3 else 5 if concentration > 0.1 else 0
    score += conc_pts
    factors.append(RiskFactor(factor="Risk Concentration", contribution=round(conc_pts, 1),
                              description=f"{critical_blocks}/{total_blocks} blocks Critical/Over-Exploited"))

    final_score = max(0, min(100, round(score)))
    risk_level = "Low" if final_score <= 25 else "Medium" if final_score <= 50 else "High" if final_score <= 75 else "Critical"

    return RiskScoreResponse(
        state=state, year=year, risk_score=final_score, risk_level=risk_level,
        avg_extraction_stage=round(avg_stage, 1), dominant_category=dominant_cat,
        trend_direction=trend_dir, factors=factors,
    )


# ─── Intent Handlers ─────────────────────────────────────────────────────────

def _handle_greeting() -> ChatResponse:
    return ChatResponse(
        reply=(
            "Hello! I'm the JAL-DRISHTI AI Assistant. I can help you analyze "
            "official CGWB/IN-GRES groundwater assessment data across India.\n\n"
            "Data Source: Central Ground Water Board (CGWB), Ministry of Jal Shakti\n"
            "Assessment Years: 2024, 2025\n"
            "Coverage: All 36 States/UTs, 200+ districts\n\n"
            "Try asking me about:\n"
            "- Groundwater status of any state\n"
            "- Comparisons between years\n"
            "- Districts with highest extraction\n"
            "- Over-exploited or critical areas"
        ),
        sources=[],
        suggested_followups=[
            "What is the groundwater status of Rajasthan?",
            "Compare Gujarat between 2024 and 2025.",
            "Which districts have the highest extraction?",
            "Show over-exploited areas.",
        ],
        evidence=Evidence(
            source="Central Ground Water Board / IN-GRES",
            assessment_year=None,
            location="All India",
            records_used=0,
            confidence="High",
            source_url="https://cgwb.gov.in/en/ground-water-resource-assessment-0",
            data_type="official",
        ),
    )


def _handle_status(db: Session, state: str) -> ChatResponse:
    latest_year = db.query(func.max(GroundWater.assessment_year)).scalar()
    if not latest_year:
        return ChatResponse(
            reply="No assessment data found in the database.",
            sources=[],
            suggested_followups=[],
        )

    rows = db.query(GroundWater).filter(
        GroundWater.state == state,
        GroundWater.assessment_year == latest_year,
    ).all()

    if not rows:
        return ChatResponse(
            reply=(
                f"No data found for **{state}**.\n\n"
                f"Available states: {', '.join(KNOWN_STATES)}"
            ),
            sources=[],
            suggested_followups=[f"What is the groundwater status of {s}?" for s in KNOWN_STATES[:3]],
        )

    districts = sorted(set(r.district for r in rows))
    blocks = sorted(set(r.block for r in rows))
    categories = {}
    for r in rows:
        categories[r.category] = categories.get(r.category, 0) + 1

    avg_stage = sum(r.extraction_stage for r in rows) / len(rows)
    total_extraction = sum(r.groundwater_extraction for r in rows)
    total_recharge = sum(r.annual_groundwater_recharge for r in rows)
    ratio = (total_extraction / total_recharge * 100) if total_recharge else 0

    if avg_stage < 70:
        status_label = "Safe"
        status_desc = "groundwater extraction is within sustainable limits."
    elif avg_stage < 90:
        status_label = "Semi-Critical"
        status_desc = "extraction is approaching sustainable limits and needs monitoring."
    elif avg_stage < 100:
        status_label = "Critical"
        status_desc = "extraction is near or at the limit of sustainability."
    else:
        status_label = "Over-Exploited"
        status_desc = "extraction exceeds recharge, requiring immediate intervention."

    cat_str = " | ".join(f"{v} {k}" for k, v in sorted(categories.items()))

    reply = (
        f"**Groundwater Status of {state} ({latest_year})**\n\n"
        f"**{len(blocks)} blocks** assessed across **{len(districts)} districts**: "
        f"{', '.join(districts)}\n\n"
        f"**Category Breakdown:** {cat_str}\n\n"
        f"**Average Extraction Stage:** {avg_stage:.1f}% — **{status_label}**\n\n"
        f"**Total Extraction:** {total_extraction:,.0f} MCM\n"
        f"**Total Recharge:** {total_recharge:,.0f} MCM\n"
        f"**Extraction-to-Recharge Ratio:** {ratio:.1f}%\n\n"
        f"The data shows that {status_desc}\n\n"
        f"*Source: CGWB Groundwater Assessment ({latest_year}) — {len(rows)} block-level records from `/api/assessments?state={state}&year={latest_year}`*"
    )

    sources = [ChatSource(
        title=f"{state} — {latest_year} Assessment",
        endpoint=f"/api/assessments?state={state}&year={latest_year}",
        record_count=len(rows),
        data=[
            {"block": r.block, "district": r.district, "stage": r.extraction_stage, "category": r.category}
            for r in sorted(rows, key=lambda x: -x.extraction_stage)[:5]
        ],
    )]

    return ChatResponse(
        reply=reply,
        sources=sources,
        suggested_followups=[
            f"Compare {state} between 2020 and 2024.",
            f"Which districts in {state} have highest extraction?",
            f"Show trend for {state}.",
        ],
        evidence=_evidence(
            year=latest_year,
            location=state,
            records=len(rows),
            confidence=_confidence_from_records(len(rows)),
            endpoint=f"/api/assessments?state={state}&year={latest_year}",
        ),
        risk_score=_calc_risk_score(db, state, latest_year),
    )


def _handle_compare(db: Session, state: str, years: List[int]) -> ChatResponse:
    if len(years) < 2:
        return ChatResponse(
            reply="Please specify two years to compare. Example: `Compare Gujarat between 2020 and 2024.`",
            sources=[],
            suggested_followups=[f"Compare {state or 'Rajasthan'} between 2020 and 2024."],
        )

    y1, y2 = years[0], years[1]
    rows1 = db.query(GroundWater).filter(GroundWater.state == state, GroundWater.assessment_year == y1, GroundWater.district == "").all()
    rows2 = db.query(GroundWater).filter(GroundWater.state == state, GroundWater.assessment_year == y2, GroundWater.district == "").all()

    if not rows1 or not rows2:
        return ChatResponse(
            reply=f"Insufficient data to compare **{state}** between {y1} and {y2}.",
            sources=[],
            suggested_followups=[f"What is the groundwater status of {state}?"],
        )

    ext1 = sum(r.groundwater_extraction for r in rows1)
    ext2 = sum(r.groundwater_extraction for r in rows2)
    stage1 = sum(r.extraction_stage for r in rows1) / len(rows1)
    stage2 = sum(r.extraction_stage for r in rows2) / len(rows2)
    recharge1 = sum(r.annual_groundwater_recharge for r in rows1)
    recharge2 = sum(r.annual_groundwater_recharge for r in rows2)
    resource1 = sum(r.extractable_groundwater_resource for r in rows1)
    resource2 = sum(r.extractable_groundwater_resource for r in rows2)

    ext_change = ((ext2 - ext1) / ext1 * 100) if ext1 else 0
    stage_change = stage2 - stage1

    reply = (
        f"**Comparison: {state} ({y1} vs {y2})**\n\n"
        f"| Metric | {y1} | {y2} | Change |\n"
        f"|--------|------|------|--------|\n"
        f"| Total Extraction | {ext1:,.0f} MCM | {ext2:,.0f} MCM | {ext_change:+.1f}% |\n"
        f"| Avg Extraction Stage | {stage1:.1f}% | {stage2:.1f}% | {stage_change:+.1f}% |\n"
        f"| Total Recharge | {recharge1:,.0f} MCM | {recharge2:,.0f} MCM | {((recharge2-recharge1)/recharge1*100) if recharge1 else 0:+.1f}% |\n"
        f"| Extractable Resource | {resource1:,.0f} MCM | {resource2:,.0f} MCM | {((resource2-resource1)/resource1*100) if resource1 else 0:+.1f}% |\n\n"
    )

    if ext_change > 0:
        reply += f"Extraction has **increased by {ext_change:.1f}%**, indicating growing stress on groundwater resources in {state}."
    elif ext_change < 0:
        reply += f"Extraction has **decreased by {abs(ext_change):.1f}%**, suggesting improved water management in {state}."
    else:
        reply += f"Extraction has remained **stable** over this period in {state}."

    reply += f"\n\n*Source: CGWB Groundwater Assessment ({y1} & {y2}) — compared {len(rows1)} + {len(rows2)} block records from `/api/assessments`*"

    sources = [
        ChatSource(
            title=f"{state} — {y1}",
            endpoint=f"/api/assessments?state={state}&year={y1}",
            record_count=len(rows1),
            data=[{"block": r.block, "extraction": r.groundwater_extraction, "stage": r.extraction_stage} for r in rows1[:3]],
        ),
        ChatSource(
            title=f"{state} — {y2}",
            endpoint=f"/api/assessments?state={state}&year={y2}",
            record_count=len(rows2),
            data=[{"block": r.block, "extraction": r.groundwater_extraction, "stage": r.extraction_stage} for r in rows2[:3]],
        ),
    ]

    return ChatResponse(
        reply=reply,
        sources=sources,
        suggested_followups=[
            f"Which districts in {state} are most stressed?",
            f"Show the full trend for {state}.",
        ],
        evidence=_evidence(
            year=y2,
            location=f"{state} ({y1} vs {y2})",
            records=len(rows1) + len(rows2),
            confidence=_confidence_from_records(len(rows1) + len(rows2)),
        ),
    )


def _handle_top_extraction(db: Session, state: Optional[str]) -> ChatResponse:
    latest_year = db.query(func.max(GroundWater.assessment_year)).scalar()
    if not latest_year:
        return ChatResponse(reply="No data available.", sources=[], suggested_followups=[])

    query = db.query(GroundWater).filter(GroundWater.assessment_year == latest_year)
    if state:
        query = query.filter(GroundWater.state == state)
    rows = query.order_by(desc(GroundWater.groundwater_extraction)).limit(5).all()

    if not rows:
        return ChatResponse(reply="No extraction data found.", sources=[], suggested_followups=[])

    scope = f" in {state}" if state else ""
    lines = []
    for i, r in enumerate(rows, 1):
        lines.append(
            f"**{i}. {r.block}, {r.district}** ({r.state})\n"
            f"   Extraction: **{r.groundwater_extraction:,.0f} MCM** | Stage: {r.extraction_stage:.1f}% | {r.category}"
        )

    reply = (
        f"**Top 5 Extraction Regions{scope} ({latest_year})**\n\n"
        + "\n\n".join(lines) +
        f"\n\nThese regions show the highest extraction volumes and may require monitoring."
        f"\n\n*Source: CGWB Groundwater Assessment ({latest_year}) — ranked from `/api/analytics/top-extraction`*"
    )

    sources = [ChatSource(
        title=f"Top Extraction{scope} — {latest_year}",
        endpoint=f"/api/analytics/top-extraction?limit=5{'&state=' + state if state else ''}&year={latest_year}",
        record_count=len(rows),
        data=[{"block": r.block, "district": r.district, "extraction": r.groundwater_extraction} for r in rows],
    )]

    chart = ChartData(
        type="bar",
        title=f"Top 5 Extraction Regions{scope} ({latest_year})",
        data=[{"name": f"{r.block}, {r.district}", "extraction": round(r.groundwater_extraction, 1)} for r in rows],
    )

    followups = ["Show over-exploited areas.", "What is the extraction trend?"]
    if state:
        followups.insert(0, f"Compare {state} between 2020 and 2024.")
    return ChatResponse(
        reply=reply,
        sources=sources,
        suggested_followups=followups,
        chart=chart,
        evidence=_evidence(
            year=latest_year,
            location=state or "All India",
            records=len(rows),
            confidence=_confidence_from_records(len(rows)),
        ),
    )


def _handle_critical_areas(db: Session, state: Optional[str]) -> ChatResponse:
    latest_year = db.query(func.max(GroundWater.assessment_year)).scalar()
    if not latest_year:
        return ChatResponse(reply="No data available.", sources=[], suggested_followups=[])

    query = db.query(GroundWater).filter(
        GroundWater.category.in_(["Critical", "Over-Exploited"]),
        GroundWater.assessment_year == latest_year,
    )
    if state:
        query = query.filter(GroundWater.state == state)
    rows = query.order_by(desc(GroundWater.extraction_stage)).all()

    if not rows:
        return ChatResponse(
            reply=f"No critical or over-exploited areas found{' in ' + state if state else ''} in {latest_year}.",
            sources=[],
            suggested_followups=["Show category distribution."],
        )

    lines = []
    for r in rows:
        lines.append(f"- **{r.block}, {r.district}** ({r.state}) — {r.category} — Stage: **{r.extraction_stage:.1f}%**")

    reply = (
        f"**Critical & Over-Exploited Areas ({latest_year})**\n\n"
        f"Found **{len(rows)} blocks** requiring attention:\n\n"
        + "\n".join(lines) +
        "\n\nThese areas have extraction rates approaching or exceeding sustainable limits. "
        "Immediate monitoring and regulation are recommended."
        f"\n\n*Source: CGWB Groundwater Assessment ({latest_year}) — filtered from `/api/assessments`*"
    )

    sources = [ChatSource(
        title=f"Critical Areas — {latest_year}",
        endpoint=f"/api/assessments?category=Critical&year={latest_year}{'&state=' + state if state else ''}",
        record_count=len(rows),
        data=[{"block": r.block, "district": r.district, "state": r.state, "stage": r.extraction_stage} for r in rows[:5]],
    )]

    return ChatResponse(
        reply=reply,
        sources=sources,
        suggested_followups=[
            "What is the overall category distribution?",
            "Show extraction trend over time.",
        ],
        evidence=_evidence(
            year=latest_year,
            location=state or "All India",
            records=len(rows),
            confidence=_confidence_from_records(len(rows)),
        ),
    )


def _handle_trend(db: Session, state: Optional[str]) -> ChatResponse:
    query = db.query(
        GroundWater.assessment_year,
        func.sum(GroundWater.groundwater_extraction).label("total_ext"),
        func.avg(GroundWater.extraction_stage).label("avg_stage"),
        func.sum(GroundWater.annual_groundwater_recharge).label("total_recharge"),
        func.count(GroundWater.block).label("blocks"),
    )
    if state:
        query = query.filter(GroundWater.state == state)
    rows = query.group_by(GroundWater.assessment_year).order_by(GroundWater.assessment_year).all()

    if not rows:
        return ChatResponse(reply="No trend data available.", sources=[], suggested_followups=[])

    lines = []
    for r in rows:
        lines.append(
            f"- **{r.assessment_year}:** {r.total_ext:,.0f} MCM extraction | "
            f"{r.avg_stage:.1f}% stage | {r.total_recharge:,.0f} MCM recharge | "
            f"{r.blocks} blocks"
        )

    first, last = rows[0], rows[-1]
    change = ((last.total_ext - first.total_ext) / first.total_ext * 100) if first.total_ext else 0

    scope = f" for {state}" if state else ""
    reply = (
        f"**Groundwater Trend{scope} ({rows[0].assessment_year}–{rows[-1].assessment_year})**\n\n"
        + "\n".join(lines) +
        f"\n\n**Overall Change:** {change:+.1f}% in total extraction over the period. "
        + ("This indicates increasing groundwater stress." if change > 0 else "This shows improving water management.")
        + f"\n\n*Source: CGWB Groundwater Assessment ({rows[0].assessment_year}–{rows[-1].assessment_year}) — aggregated from `/api/analytics/trend`*"
    )

    sources = [ChatSource(
        title=f"Trend{scope}",
        endpoint=f"/api/analytics/trend{'?state=' + state if state else ''}",
        record_count=len(rows),
        data=[{"year": r.assessment_year, "extraction": r.total_ext, "stage": r.avg_stage} for r in rows],
    )]

    chart = ChartData(
        type="line",
        title=f"Groundwater Extraction Trend{scope} ({rows[0].assessment_year}–{rows[-1].assessment_year})",
        data=[
            {"year": r.assessment_year, "extraction": round(r.total_ext, 1), "recharge": round(r.total_recharge, 1)}
            for r in rows
        ],
    )

    return ChatResponse(
        reply=reply,
        sources=sources,
        suggested_followups=[
            f"Compare {state or 'states'} between 2020 and 2024.",
            "Which districts have highest extraction?",
        ],
        chart=chart,
        evidence=_evidence(
            year=rows[-1].assessment_year if rows else None,
            location=state or "All India",
            records=sum(r.blocks for r in rows),
            confidence=_confidence_from_records(len(rows)),
        ),
    )


def _handle_category(db: Session, state: Optional[str]) -> ChatResponse:
    query = db.query(GroundWater.category, func.count(), func.avg(GroundWater.extraction_stage))
    if state:
        query = query.filter(GroundWater.state == state)
    rows = query.group_by(GroundWater.category).all()
    total = sum(r[1] for r in rows)

    if not rows:
        return ChatResponse(reply="No category data available.", sources=[], suggested_followups=[])

    scope = f" in {state}" if state else ""
    lines = []
    for cat, count, avg_stage in sorted(rows, key=lambda x: -x[1]):
        pct = (count / total * 100) if total else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        lines.append(f"- **{cat}:** {count} blocks ({pct:.1f}%) — avg stage {avg_stage:.1f}%")

    reply = (
        f"**Category Distribution{scope}**\n\n"
        f"Total: **{total} blocks**\n\n"
        + "\n".join(lines) +
        "\n\nCategories follow CGWB classification: "
        "Safe (<70%), Semi-Critical (70–90%), Critical (90–100%), Over-Exploited (>100%)."
        f"\n\n*Source: CGWB Groundwater Assessment — aggregated from `/api/analytics/category-distribution`*"
    )

    sources = [ChatSource(
        title=f"Category Distribution{scope}",
        endpoint=f"/api/analytics/category-distribution{'?state=' + state if state else ''}",
        record_count=len(rows),
        data=[{"category": c, "count": n, "avg_stage": round(s, 1)} for c, n, s in rows],
    )]

    chart = ChartData(
        type="pie",
        title=f"Category Distribution{scope}",
        data=[{"name": cat, "value": count} for cat, count, _ in sorted(rows, key=lambda x: -x[1])],
    )

    return ChatResponse(
        reply=reply,
        sources=sources,
        suggested_followups=[
            f"What is the groundwater status of {state or 'Rajasthan'}?",
            "Show over-exploited areas.",
        ],
        chart=chart,
        evidence=_evidence(
            year=None,
            location=state or "All India",
            records=total,
            confidence=_confidence_from_records(total),
        ),
    )


def _handle_location(db: Session, state: Optional[str]) -> ChatResponse:
    if not state:
        return ChatResponse(
            reply="Please specify a state. Example: `Show districts in Punjab.`",
            sources=[],
            suggested_followups=[f"Show districts in {s}." for s in KNOWN_STATES[:4]],
        )

    latest_year = db.query(func.max(GroundWater.assessment_year)).scalar()
    if not latest_year:
        return ChatResponse(reply="No data available.", sources=[], suggested_followups=[])

    rows = db.query(GroundWater).filter(
        GroundWater.state == state,
        GroundWater.assessment_year == latest_year,
    ).order_by(GroundWater.district, GroundWater.block).all()

    if not rows:
        return ChatResponse(
            reply=f"No data found for **{state}**.",
            sources=[],
            suggested_followups=[f"What is the groundwater status of {s}?" for s in KNOWN_STATES[:3]],
        )

    by_district = {}
    for r in rows:
        by_district.setdefault(r.district, []).append(r)

    lines = []
    for dist, blocks in sorted(by_district.items()):
        block_names = ", ".join(f"{b.block} ({b.extraction_stage:.0f}%)" for b in blocks)
        lines.append(f"- **{dist}** ({len(blocks)} blocks): {block_names}")

    reply = (
        f"**{state} — District & Block Breakdown ({latest_year})**\n\n"
        f"**{len(by_district)} districts**, **{len(rows)} blocks**:\n\n"
        + "\n".join(lines)
        + f"\n\n*Source: CGWB Groundwater Assessment ({latest_year}) — from `/api/blocks?state={state}`*"
    )

    sources = [ChatSource(
        title=f"{state} Blocks — {latest_year}",
        endpoint=f"/api/blocks?state={state}",
        record_count=len(rows),
        data=[{"district": r.district, "block": r.block, "stage": r.extraction_stage} for r in rows[:5]],
    )]

    return ChatResponse(
        reply=reply,
        sources=sources,
        suggested_followups=[
            f"Compare {state} between 2020 and 2024.",
            f"Which districts in {state} have highest extraction?",
        ],
        evidence=_evidence(
            year=latest_year,
            location=state,
            records=len(rows),
            confidence=_confidence_from_records(len(rows)),
        ),
    )


def _handle_what_changed(db: Session, state: Optional[str], years: List[int]) -> ChatResponse:
    if not state:
        return ChatResponse(
            reply="Please specify a state. Example: `What changed in Rajasthan between 2020 and 2024?`",
            sources=[],
            suggested_followups=[f"What changed in {s} between 2020 and 2024?" for s in KNOWN_STATES[:4]],
            evidence=_evidence(location="All India", records=500, confidence="High"),
        )

    if len(years) < 2:
        return ChatResponse(
            reply="Please specify two years to compare. Example: `What changed in Rajasthan between 2020 and 2024?`",
            sources=[],
            suggested_followups=[f"What changed in {state} between 2020 and 2024?"],
            evidence=_evidence(year=None, location=state, records=0, confidence="Low"),
        )

    y1, y2 = years[0], years[1]

    # Call the analytics endpoint logic directly
    CATEGORY_ORDER = {"Safe": 0, "Semi-Critical": 1, "Critical": 2, "Over-Exploited": 3}

    q1 = db.query(GroundWater).filter(GroundWater.state == state, GroundWater.assessment_year == y1)
    q2 = db.query(GroundWater).filter(GroundWater.state == state, GroundWater.assessment_year == y2)
    rows1 = q1.all()
    rows2 = q2.all()

    if not rows1 or not rows2:
        return ChatResponse(
            reply=f"Insufficient data to compare **{state}** between {y1} and {y2}.",
            sources=[],
            suggested_followups=[f"What is the groundwater status of {state}?"],
            evidence=_evidence(year=y2, location=state, records=len(rows1) + len(rows2), confidence="Low"),
        )

    lookup1 = {(r.district, r.block): r for r in rows1}
    lookup2 = {(r.district, r.block): r for r in rows2}
    all_keys = set(lookup1.keys()) | set(lookup2.keys())

    improvements = 0
    deteriorations = 0
    unchanged = 0
    category_shifts: dict[str, int] = {}
    block_details = []

    for key in all_keys:
        r1 = lookup1.get(key)
        r2 = lookup2.get(key)
        if r1 and r2:
            old_cat = r1.category
            new_cat = r2.category
            ext1 = r1.groundwater_extraction
            ext2 = r2.groundwater_extraction
            ext_change = ((ext2 - ext1) / ext1 * 100) if ext1 else 0

            cat1_rank = CATEGORY_ORDER.get(old_cat, -1)
            cat2_rank = CATEGORY_ORDER.get(new_cat, -1)

            if cat2_rank < cat1_rank:
                change_type = "improved"
                improvements += 1
            elif cat2_rank > cat1_rank:
                change_type = "deteriorated"
                deteriorations += 1
            else:
                change_type = "unchanged"
                unchanged += 1

            shift_key = f"{old_cat} → {new_cat}"
            if old_cat != new_cat:
                category_shifts[shift_key] = category_shifts.get(shift_key, 0) + 1

            block_details.append({
                "block": r2.block, "district": r2.district,
                "old_cat": old_cat, "new_cat": new_cat,
                "ext_change": round(ext_change, 1), "type": change_type,
            })

    ext1_total = sum(r.groundwater_extraction for r in rows1)
    ext2_total = sum(r.groundwater_extraction for r in rows2)
    ext_change_pct = ((ext2_total - ext1_total) / ext1_total * 100) if ext1_total else 0

    avg_stage1 = sum(r.extraction_stage for r in rows1) / len(rows1)
    avg_stage2 = sum(r.extraction_stage for r in rows2) / len(rows2)

    if improvements > deteriorations:
        trend = "improving"
        trend_emoji = "📈"
    elif deteriorations > improvements:
        trend = "deteriorating"
        trend_emoji = "📉"
    else:
        trend = "stable"
        trend_emoji = "➡️"

    # Build reply
    lines = [
        f"**What Changed in {state} ({y1} → {y2})**\n",
        f"**Extraction:** {ext1_total:,.0f} → {ext2_total:,.0f} MCM ({ext_change_pct:+.1f}%)",
        f"**Avg Stage:** {avg_stage1:.1f}% → {avg_stage2:.1f}%\n",
        f"**{improvements}** blocks improved  |  **{deteriorations}** deteriorated  |  **{unchanged}** unchanged\n",
    ]

    if category_shifts:
        lines.append("**Category Shifts:**")
        for shift, count in sorted(category_shifts.items(), key=lambda x: -x[1]):
            lines.append(f"  - {shift}: {count} block{'s' if count > 1 else ''}")

    lines.append(f"\n**Overall Trend:** {trend_emoji} {trend.title()}")

    # Top changed blocks
    sorted_blocks = sorted(block_details, key=lambda x: -abs(x["ext_change"]))[:5]
    if sorted_blocks:
        lines.append("\n**Most Changed Blocks:**")
        for b in sorted_blocks:
            arrow = "↑" if b["ext_change"] > 0 else "↓" if b["ext_change"] < 0 else "="
            lines.append(f"  - {b['block']}, {b['district']}: {b['ext_change']:+.1f}% ({b['old_cat']} → {b['new_cat']})")

    reply = "\n".join(lines)
    reply += f"\n\n*Source: CGWB Groundwater Assessment ({y1} & {y2}) — compared {len(rows1) + len(rows2)} block records from `/api/analytics/what-changed`*"

    sources = [ChatSource(
        title=f"What Changed — {state} ({y1} vs {y2})",
        endpoint=f"/api/analytics/what-changed?state={state}&year1={y1}&year2={y2}",
        record_count=len(rows1) + len(rows2),
        data=[{"block": b["block"], "district": b["district"], "change": b["ext_change"]} for b in sorted_blocks],
    )]

    chart = ChartData(
        type="bar",
        title=f"Block-Level Extraction Change — {state} ({y1} → {y2})",
        data=[{"name": f"{b['block']}, {b['district']}", "change": b["ext_change"]} for b in sorted_blocks],
    )

    return ChatResponse(
        reply=reply,
        sources=sources,
        suggested_followups=[
            f"Show trend for {state}.",
            f"Compare {state} between {y1} and {y2}.",
        ],
        chart=chart,
        evidence=_evidence(
            year=y2,
            location=f"{state} ({y1} vs {y2})",
            records=len(rows1) + len(rows2),
            confidence=_confidence_from_records(len(rows1) + len(rows2)),
        ),
    )


# ─── Main Chat Endpoint ─────────────────────────────────────────────────────

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    # Parse structured intent
    parsed = parse_message(req.message)
    language = parsed.language

    intent = parsed.intent
    state = parsed.state
    years = parsed.comparison_years if intent in ("compare", "what_changed") else ([parsed.year] if parsed.year else [])

    # Build the parsed_intent for response
    pi = ParsedIntent(
        intent=parsed.intent,
        state=parsed.state,
        district=parsed.district,
        block=parsed.block,
        year=parsed.year,
        comparison_years=parsed.comparison_years,
        metric=parsed.metric,
        category=parsed.category,
        confidence=parsed.confidence,
        language=parsed.language,
    )

    if intent == "greeting":
        resp = _handle_greeting()
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    if intent == "status":
        if state:
            resp = _handle_status(db, state)
        else:
            resp = ChatResponse(
                reply=(
                    "Please specify a state. Example: `What is the groundwater status of Rajasthan?`\n\n"
                    f"Available states: {', '.join(KNOWN_STATES)}"
                ),
                sources=[],
                suggested_followups=[f"What is the groundwater status of {s}?" for s in KNOWN_STATES[:4]],
                evidence=_evidence(location="All India", records=500, confidence="High"),
            )
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    if intent == "compare":
        if state:
            resp = _handle_compare(db, state, parsed.comparison_years)
        else:
            resp = ChatResponse(
                reply=(
                    "Please specify a state and two years. Example:\n"
                    "`Compare Gujarat between 2020 and 2024.`"
                ),
                sources=[],
                suggested_followups=[f"Compare {s} between 2020 and 2024." for s in KNOWN_STATES[:3]],
                evidence=_evidence(location="All India", records=500, confidence="High"),
            )
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    if intent == "top_extraction":
        resp = _handle_top_extraction(db, state)
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    if intent == "critical_areas":
        resp = _handle_critical_areas(db, state)
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    if intent == "trend":
        resp = _handle_trend(db, state)
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    if intent == "category":
        resp = _handle_category(db, state)
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    if intent == "location":
        resp = _handle_location(db, state)
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    if intent == "what_changed":
        resp = _handle_what_changed(db, state, parsed.comparison_years)
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    # Fallback — try status if a state is mentioned, otherwise general help
    if state:
        resp = _handle_status(db, state)
        resp.parsed_intent = pi
        resp.reply = translate_reply(resp.reply, language)
        resp.suggested_followups = translate_followups(resp.suggested_followups, language)
        return resp

    categories = db.query(GroundWater.category, func.count()).group_by(GroundWater.category).all()
    cat_str = ", ".join(f"{c} ({n})" for c, n in categories)

    resp = ChatResponse(
        reply=(
            "I'm not sure I understood that question.\n\n"
            f"**Database Summary:** {cat_str}\n\n"
            "Try asking about:\n"
            "- A specific state's groundwater status\n"
            "- Year-over-year comparisons\n"
            "- Highest extraction regions\n"
            "- Critical or over-exploited areas\n"
            "- Extraction trends\n"
            "- Category distribution"
        ),
        sources=[],
        suggested_followups=[
            "What is the groundwater status of Rajasthan?",
            "Compare Gujarat between 2020 and 2024.",
            "Which districts have the highest extraction?",
            "Show over-exploited areas.",
        ],
        evidence=_evidence(location="All India", records=500, confidence="High"),
    )
    resp.parsed_intent = pi
    resp.reply = translate_reply(resp.reply, language)
    resp.suggested_followups = translate_followups(resp.suggested_followups, language)
    return resp


# ─── LLM Chat Endpoint ──────────────────────────────────────────────────────

class LLMChatRequest(BaseModel):
    message: str
    top_k: int = 5
    language: str = "english"  # "english" or "hindi"


class LLMSource(BaseModel):
    title: str
    relevance: float
    content_preview: str


class LLMChatResponse(BaseModel):
    reply: str
    sources: List[LLMSource]
    model: str = "llama3.1:8b"
    mode: str = "llm"


@app.post("/api/llm/chat", response_model=LLMChatResponse)
def llm_chat(req: LLMChatRequest):
    """LLM-powered chat using RAG pipeline with Ollama."""
    from rag import get_rag_engine, LLM_MODEL

    engine = get_rag_engine()
    result = engine.generate(req.message, top_k=req.top_k, language=req.language)

    sources = [
        LLMSource(
            title=s["title"],
            relevance=s["relevance"],
            content_preview=s["content_preview"],
        )
        for s in result.get("sources", [])
    ]

    return LLMChatResponse(
        reply=result["reply"],
        sources=sources,
        model=LLM_MODEL,
    )


@app.post("/api/llm/rebuild")
def rebuild_llm_knowledge():
    """Rebuild the RAG knowledge base (e.g. after DB update)."""
    from rag import rebuild_rag_engine
    rebuild_rag_engine()
    return {"status": "ok", "message": "Knowledge base rebuilt"}


@app.get("/api/llm/health")
def llm_health():
    """Check if Ollama is available and model is ready."""
    import subprocess as _sp
    try:
        result = _sp.run(
            [OLLAMA_BIN, "list"],
            capture_output=True, text=True, timeout=10,
        )
        models = result.stdout.strip()
        has_model = "llama3.1" in models
        return {
            "status": "ok" if has_model else "model_missing",
            "ollama_installed": True,
            "model_available": has_model,
            "model": LLM_MODEL,
            "models_list": models,
        }
    except FileNotFoundError:
        return {
            "status": "ollama_missing",
            "ollama_installed": False,
            "model_available": False,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/chat/parse")
def parse_only(req: ChatRequest):
    """Debug endpoint — returns parsed intent without querying the database."""
    parsed = parse_message(req.message)
    return {
        "intent": parsed.intent,
        "state": parsed.state,
        "district": parsed.district,
        "block": parsed.block,
        "year": parsed.year,
        "comparison_years": parsed.comparison_years,
        "metric": parsed.metric,
        "category": parsed.category,
        "confidence": parsed.confidence,
        "language": parsed.language,
        "raw_message": parsed.raw_message,
    }


# ─── Smart Chat Endpoints (Hybrid RAG + SQL) ──────────────────────────────────

class SmartChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    language: str = "english"


class SmartChatResponse(BaseModel):
    reply: str
    sources: list
    query_type: str
    entities: dict
    session_id: str
    route: str


@app.post("/api/smart/chat", response_model=SmartChatResponse)
def smart_chat_endpoint(req: SmartChatRequest):
    """Intelligent chat with SQL+RAG routing, geographic resolution, and conversation memory."""
    result = smart_chat(req.message, req.session_id, req.language)
    return SmartChatResponse(**result)


@app.post("/api/smart/chat/stream")
async def smart_chat_stream_endpoint(req: SmartChatRequest):
    """Streaming intelligent chat endpoint."""
    def generate():
        for chunk in smart_chat_streaming(req.message, req.session_id, req.language):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ─── Groundwater Data Endpoints ──────────────────────────────────────────────

@app.get("/api/groundwater/state/{state}")
def get_groundwater_state(state: str, year: int = Query(default=None)):
    """Get comprehensive groundwater data for a state."""
    from smart_chat import _fetch_state_latest, _fetch_state_data, _fetch_state_trend
    from config import LATEST_ASSESSMENT_YEAR

    resolved = resolve_state(state)
    if not resolved:
        return JSONResponse(status_code=404, content={"error": f"State '{state}' not found"})

    if year:
        data = _fetch_state_data(resolved, year)
    else:
        data = _fetch_state_latest(resolved)

    if not data:
        return JSONResponse(status_code=404, content={"error": f"No data for {resolved}"})

    trend = _fetch_state_trend(resolved)

    return {
        "state": resolved,
        "data": data,
        "trend": {
            "direction": trend.direction if trend else None,
            "total_change": trend.total_change if trend else None,
            "percentage_change": trend.percentage_change if trend else None,
        } if trend else None,
    }


@app.get("/api/groundwater/district/{state}")
def get_groundwater_districts(state: str, district: str = Query(default=None)):
    """Get district-level groundwater data."""
    from smart_chat import _fetch_district_data

    resolved = resolve_state(state)
    if not resolved:
        return JSONResponse(status_code=404, content={"error": f"State '{state}' not found"})

    data = _fetch_district_data(resolved, district)
    return {"state": resolved, "districts": data}


@app.get("/api/groundwater/block/{state}")
def get_groundwater_blocks(state: str, district: str = Query(default=None), block: str = Query(default=None)):
    """Get block-level groundwater data."""
    from smart_chat import _fetch_block_data

    resolved = resolve_state(state)
    if not resolved:
        return JSONResponse(status_code=404, content={"error": f"State '{state}' not found"})

    data = _fetch_block_data(resolved, district, block)
    return {"state": resolved, "blocks": data}


@app.get("/api/groundwater/compare")
def compare_groundwater(state_a: str = Query(...), state_b: str = Query(...), year: int = Query(default=None)):
    """Compare groundwater between two states."""
    from smart_chat import _fetch_state_comparison
    from config import LATEST_ASSESSMENT_YEAR

    resolved_a = resolve_state(state_a)
    resolved_b = resolve_state(state_b)

    if not resolved_a or not resolved_b:
        return JSONResponse(status_code=400, content={"error": "Invalid state name(s)"})

    result = _fetch_state_comparison(resolved_a, resolved_b, year or LATEST_ASSESSMENT_YEAR)
    return result


@app.get("/api/groundwater/rankings")
def get_rankings(metric: str = Query(default="extraction_stage"), limit: int = Query(default=10)):
    """Get state-level rankings."""
    from smart_chat import _fetch_rankings
    rankings = _fetch_rankings(metric, limit)
    return {"metric": metric, "rankings": rankings}


@app.get("/api/groundwater/trends/{state}")
def get_state_trends(state: str):
    """Get multi-year trend for a state."""
    from smart_chat import _fetch_state_trend

    resolved = resolve_state(state)
    if not resolved:
        return JSONResponse(status_code=404, content={"error": f"State '{state}' not found"})

    trend = _fetch_state_trend(resolved)
    if not trend:
        return JSONResponse(status_code=404, content={"error": f"Insufficient trend data for {resolved}"})

    return {
        "state": resolved,
        "metric": trend.metric,
        "direction": trend.direction,
        "total_change": trend.total_change,
        "percentage_change": trend.percentage_change,
        "avg_annual_change": trend.avg_annual_change,
        "points": [{"year": p.year, "value": p.value} for p in trend.points],
    }


@app.get("/api/groundwater/category")
def get_category(state: str = Query(default=None)):
    """Get category distribution."""
    from smart_chat import _fetch_category_distribution
    dist = _fetch_category_distribution(state)
    return dist


@app.get("/api/groundwater/overview")
def get_overview():
    """Get national groundwater overview."""
    from smart_chat import _fetch_overall_stats
    return _fetch_overall_stats()


@app.get("/api/groundwater/what-changed")
def what_changed(state: str = Query(...), year1: int = Query(...), year2: int = Query(...)):
    """Compare two years for a state."""
    from smart_chat import _fetch_what_changed

    resolved = resolve_state(state)
    if not resolved:
        return JSONResponse(status_code=404, content={"error": f"State '{state}' not found"})

    return _fetch_what_changed(resolved, year1, year2)


@app.get("/api/groundwater/over-exploited")
def get_over_exploited(state: str = Query(default=None), limit: int = Query(default=20)):
    """Get over-exploited blocks."""
    conn = __import__("sqlite3").connect(DB_PATH)
    conn.row_factory = __import__("sqlite3").Row
    c = conn.cursor()
    if state:
        resolved = resolve_state(state)
        c.execute("""
            SELECT block, district, state, extraction_stage, groundwater_extraction, assessment_year
            FROM groundwater WHERE category = 'Over-Exploited' AND state = ? AND block != ''
            ORDER BY extraction_stage DESC LIMIT ?
        """, (resolved, limit))
    else:
        c.execute("""
            SELECT block, district, state, extraction_stage, groundwater_extraction, assessment_year
            FROM groundwater WHERE category = 'Over-Exploited' AND block != ''
            ORDER BY extraction_stage DESC LIMIT ?
        """, (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"over_exploited": rows, "count": len(rows)}


@app.get("/api/states/all")
def get_all_states_list():
    """Get list of all Indian states and UTs."""
    return {"states": get_all_states()}


@app.get("/api/groundwater/quality")
def get_quality_info(state: str = Query(default=None)):
    """Get groundwater quality information."""
    return {
        "message": "Groundwater quality data is available through CGWB monitoring stations",
        "parameters": ["Fluoride", "Arsenic", "Nitrate", "Iron", "TDS", "EC", "pH", "Chloride", "Sulphate", "Hardness", "Uranium"],
        "state": state,
        "source": "CGWB Annual Groundwater Quality Reports",
    }


# ─── Data Ingestion Admin Endpoints ──────────────────────────────────────────

@app.post("/api/admin/ingest")
def ingest_data(dataset_key: str = Query(...)):
    """Trigger data ingestion for a dataset."""
    from ingestion import ingest_dataset
    result = ingest_dataset(dataset_key)
    return {
        "dataset_id": result.dataset_id,
        "status": result.status,
        "records_ingested": result.records_ingested,
        "records_rejected": result.records_rejected,
        "errors": result.errors[:10],
    }


@app.get("/api/admin/validation")
def validation_report():
    """Get data quality validation report."""
    from ingestion import run_validation_report
    return run_validation_report()


@app.get("/api/admin/datasets")
def list_datasets():
    """List all ingested datasets."""
    conn = __import__("sqlite3").connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM dataset_versions ORDER BY ingestion_date DESC")
        rows = [dict(r) for r in c.fetchall()]
    except Exception:
        rows = []
    conn.close()
    return {"datasets": rows}


# ─── Assessment Year Endpoints ───────────────────────────────────────────────

SUPPORTED_YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]


@app.get("/api/groundwater/assessment-years")
def get_assessment_years():
    """Return which assessment years are available in the database."""
    if USE_SUPABASE:
        from supabase_client import sb_select
        rows = sb_select("groundwater")
        available = set()
        for r in rows:
            yr = r.get("assessment_year")
            if yr:
                available.add(yr)
    else:
        conn = __import__("sqlite3").connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT DISTINCT assessment_year FROM groundwater WHERE assessment_year IS NOT NULL")
        available = {row[0] for row in c.fetchall()}
        conn.close()

    return {
        "requested_range": SUPPORTED_YEARS,
        "years": [
            {"year": y, "available": y in available, "record_count": 0}
            for y in SUPPORTED_YEARS
        ],
        "latest_verified": max((y for y in SUPPORTED_YEARS if y in available), default=None),
    }


@app.get("/api/groundwater/overview-year")
def get_overview_year(year: int = Query(default=None)):
    """Get year-specific national groundwater overview."""
    if USE_SUPABASE:
        from supabase_client import sb_select
        rows = sb_select("groundwater")
        blocks = [r for r in rows if r.get("block")]
        if year:
            blocks = [r for r in blocks if r.get("assessment_year") == year]
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if year:
            c.execute("""
                SELECT * FROM groundwater WHERE block != '' AND assessment_year = ?
            """, (year,))
        else:
            c.execute("SELECT * FROM groundwater WHERE block != ''")
        blocks = [dict(r) for r in c.fetchall()]
        conn.close()

    if not blocks:
        return {
            "total_extraction": 0, "total_recharge": 0, "avg_stage": 0,
            "states": 0, "districts": 0, "blocks": 0, "total_records": 0,
            "oe_blocks": 0, "critical_blocks": 0, "sc_blocks": 0, "safe_blocks": 0,
            "year": year, "data_available": False,
        }

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
        "year": year, "data_available": True,
    }


@app.get("/api/groundwater/year-compare")
def year_compare(state: str = Query(...), year1: int = Query(...), year2: int = Query(...)):
    """Compare two assessment years for a state with YoY metrics."""
    resolved = resolve_state(state)
    if not resolved:
        return JSONResponse(status_code=404, content={"error": f"State '{state}' not found"})

    if USE_SUPABASE:
        from supabase_client import sb_select
        rows = sb_select("groundwater", filters={"state": resolved})
        blocks = [r for r in rows if r.get("block")]
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT * FROM groundwater WHERE state = ? AND block != ''
            AND assessment_year IN (?, ?)
        """, (resolved, year1, year2))
        blocks = [dict(r) for r in c.fetchall()]
        conn.close()

    by_key = {}
    for r in blocks:
        key = (r.get("block", ""), r.get("district", ""))
        yr = r.get("assessment_year")
        if yr in (year1, year2):
            by_key.setdefault(key, {})[yr] = r

    block_changes = []
    for key, years_data in by_key.items():
        r1 = years_data.get(year1)
        r2 = years_data.get(year2)
        if r1 and r2:
            stage1 = r1.get("extraction_stage", 0) or 0
            stage2 = r2.get("extraction_stage", 0) or 0
            block_changes.append({
                "block": key[0], "district": key[1],
                "stage_y1": stage1, "stage_y2": stage2,
                "stage_change": round(stage2 - stage1, 2),
                "cat_y1": r1.get("category", ""), "cat_y2": r2.get("category", ""),
                "ext_y1": r1.get("groundwater_extraction", 0) or 0,
                "ext_y2": r2.get("groundwater_extraction", 0) or 0,
                "ext_change": round((r2.get("groundwater_extraction", 0) or 0) - (r1.get("groundwater_extraction", 0) or 0), 2),
                "rech_y1": r1.get("annual_groundwater_recharge", 0) or 0,
                "rech_y2": r2.get("annual_groundwater_recharge", 0) or 0,
            })

    blocks_y1 = [r for r in blocks if r.get("assessment_year") == year1 and r.get("block")]
    blocks_y2 = [r for r in blocks if r.get("assessment_year") == year2 and r.get("block")]

    avg_stage1 = sum(r.get("extraction_stage", 0) or 0 for r in blocks_y1) / max(len(blocks_y1), 1)
    avg_stage2 = sum(r.get("extraction_stage", 0) or 0 for r in blocks_y2) / max(len(blocks_y2), 1)
    total_ext1 = sum(r.get("groundwater_extraction", 0) or 0 for r in blocks_y1)
    total_ext2 = sum(r.get("groundwater_extraction", 0) or 0 for r in blocks_y2)
    total_rech1 = sum(r.get("annual_groundwater_recharge", 0) or 0 for r in blocks_y1)
    total_rech2 = sum(r.get("annual_groundwater_recharge", 0) or 0 for r in blocks_y2)

    improvements = sum(1 for b in block_changes if b["stage_change"] < -2)
    deteriorations = sum(1 for b in block_changes if b["stage_change"] > 2)
    unchanged = len(block_changes) - improvements - deteriorations

    improvements_cat = sum(1 for b in block_changes if b["cat_y2"] == "Safe" and b["cat_y1"] != "Safe")
    deteriorations_cat = sum(1 for b in block_changes
                             if b["cat_y1"] == "Safe" and b["cat_y2"] != "Safe"
                             or b["cat_y1"] == "Semi-Critical" and b["cat_y2"] in ("Critical", "Over-Exploited")
                             or b["cat_y1"] == "Critical" and b["cat_y2"] == "Over-Exploited")

    return {
        "state": resolved, "year1": year1, "year2": year2,
        "data_y1_available": len(blocks_y1) > 0,
        "data_y2_available": len(blocks_y2) > 0,
        "summary": {
            "avg_stage_y1": round(avg_stage1, 2),
            "avg_stage_y2": round(avg_stage2, 2),
            "stage_change": round(avg_stage2 - avg_stage1, 2),
            "pct_change": round(((avg_stage2 - avg_stage1) / max(avg_stage1, 0.01)) * 100, 2),
            "total_extraction_y1": round(total_ext1, 2),
            "total_extraction_y2": round(total_ext2, 2),
            "ext_change": round(total_ext2 - total_ext1, 2),
            "total_recharge_y1": round(total_rech1, 2),
            "total_recharge_y2": round(total_rech2, 2),
            "rech_change": round(total_rech2 - total_rech1, 2),
            "blocks_compared": len(block_changes),
            "improvements": improvements,
            "deteriorations": deteriorations,
            "unchanged": unchanged,
            "improvements_cat": improvements_cat,
            "deteriorations_cat": deteriorations_cat,
            "overall_trend": "improving" if avg_stage2 < avg_stage1 else "deteriorating" if avg_stage2 > avg_stage1 else "stable",
        },
        "block_changes": sorted(block_changes, key=lambda x: abs(x["stage_change"]), reverse=True),
    }


@app.get("/api/groundwater/status-transitions")
def status_transitions(state: str = Query(...)):
    """Calculate status transitions for a state across available years."""
    resolved = resolve_state(state)
    if not resolved:
        return JSONResponse(status_code=404, content={"error": f"State '{state}' not found"})

    if USE_SUPABASE:
        from supabase_client import sb_select
        rows = sb_select("groundwater", filters={"state": resolved})
        blocks = [r for r in rows if r.get("block")]
    else:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT * FROM groundwater WHERE state = ? AND block != ''
            ORDER BY assessment_year
        """, (resolved,))
        blocks = [dict(r) for r in c.fetchall()]
        conn.close()

    by_year = {}
    for r in blocks:
        yr = r.get("assessment_year")
        if yr:
            by_year.setdefault(yr, []).append(r)

    year_summaries = []
    for yr in sorted(by_year.keys()):
        yr_blocks = by_year[yr]
        cats = {}
        for b in yr_blocks:
            c = b.get("category", "No Data")
            cats[c] = cats.get(c, 0) + 1
        avg_stage = sum(b.get("extraction_stage", 0) or 0 for b in yr_blocks) / len(yr_blocks)
        dominant = max(cats, key=cats.get) if cats else "No Data"
        year_summaries.append({
            "year": yr,
            "blocks": len(yr_blocks),
            "avg_stage": round(avg_stage, 2),
            "categories": cats,
            "dominant_category": dominant,
        })

    transitions = []
    for i in range(1, len(year_summaries)):
        prev = year_summaries[i - 1]
        curr = year_summaries[i]
        prev_cat = prev["dominant_category"]
        curr_cat = curr["dominant_category"]
        cat_order = {"Safe": 0, "Semi-Critical": 1, "Critical": 2, "Over-Exploited": 3, "No Data": -1}
        prev_rank = cat_order.get(prev_cat, -1)
        curr_rank = cat_order.get(curr_cat, -1)
        if curr_rank < prev_rank:
            status = "improved"
        elif curr_rank > prev_rank:
            status = "deteriorated"
        else:
            status = "unchanged"
        transitions.append({
            "from_year": prev["year"],
            "to_year": curr["year"],
            "from_category": prev_cat,
            "to_category": curr_cat,
            "from_avg_stage": prev["avg_stage"],
            "to_avg_stage": curr["avg_stage"],
            "stage_change": round(curr["avg_stage"] - prev["avg_stage"], 2),
            "status": status,
        })

    return {
        "state": resolved,
        "year_summaries": year_summaries,
        "transitions": transitions,
        "years_available": [s["year"] for s in year_summaries],
    }


# --- Serve built frontend ---
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
