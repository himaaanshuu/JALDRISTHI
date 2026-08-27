"""
Database Models for JAL-DRISHTI Groundwater Intelligence.
Includes structured groundwater data, quality, levels, and conversation memory.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Index, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime
import os


class Base(DeclarativeBase):
    pass


DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'jaldrishti.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Data Sources ────────────────────────────────────────────────────────────

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(200), nullable=False)
    source_url = Column(String(500))
    organization = Column(String(200))
    assessment_year = Column(Integer)
    publication_year = Column(Integer)
    retrieved_at = Column(String(50))
    dataset_description = Column(Text)
    resource_ids = Column(Text)


# ─── Core Groundwater Assessment Data ────────────────────────────────────────

class GroundWater(Base):
    __tablename__ = "groundwater"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(100), index=True)
    district = Column(String(100), index=True)
    block = Column(String(100), index=True)
    assessment_year = Column(Integer, index=True)
    annual_groundwater_recharge = Column(Float)
    extractable_groundwater_resource = Column(Float)
    groundwater_extraction = Column(Float)
    extraction_stage = Column(Float)
    category = Column(String(20), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    is_demo_data = Column(Integer, default=1)
    source_id = Column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_gw_state_year", "state", "assessment_year"),
        Index("ix_gw_district_year", "district", "assessment_year"),
        Index("ix_gw_category_state", "category", "state"),
    )


# ─── Groundwater Quality ────────────────────────────────────────────────────

class GroundwaterQuality(Base):
    __tablename__ = "groundwater_quality"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(100), index=True)
    district = Column(String(100), index=True)
    block = Column(String(100), index=True)
    station_id = Column(String(50), index=True)
    assessment_year = Column(Integer, index=True)
    fluoride_mg_l = Column(Float)
    arsenic_ug_l = Column(Float)
    nitrate_mg_l = Column(Float)
    iron_mg_l = Column(Float)
    tds_mg_l = Column(Float)
    ec_umho_cm = Column(Float)
    ph = Column(Float)
    chloride_mg_l = Column(Float)
    sulphate_mg_l = Column(Float)
    hardness_mg_l = Column(Float)
    uranium_ug_l = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    source_id = Column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_gwq_state_year", "state", "assessment_year"),
        Index("ix_gwq_district", "district"),
    )


# ─── Groundwater Levels ─────────────────────────────────────────────────────

class GroundwaterLevel(Base):
    __tablename__ = "groundwater_levels"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(100), index=True)
    district = Column(String(100), index=True)
    block = Column(String(100), index=True)
    station_id = Column(String(50), index=True)
    assessment_year = Column(Integer, index=True)
    pre_monsoon_level_m = Column(Float)
    post_monsoon_level_m = Column(Float)
    annual_fluctuation_m = Column(Float)
    groundwater_status = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    source_id = Column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_gwl_state_year", "state", "assessment_year"),
    )


# ─── Water Readings (Sensor Data) ───────────────────────────────────────────

class WaterReading(Base):
    __tablename__ = "water_readings"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), index=True)
    water_level = Column(Float)
    rainfall_mm = Column(Float)
    ph_level = Column(Float)
    turbidity = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="normal")


# ─── Conversation Memory ────────────────────────────────────────────────────

class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True)
    role = Column(String(10))  # "user" or "assistant"
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    query_type = Column(String(50))
    entities = Column(Text)  # JSON


# ─── Dataset Tracking ───────────────────────────────────────────────────────

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String(100), unique=True)
    dataset_name = Column(String(200))
    year = Column(Integer)
    geographic_scope = Column(String(100))
    ingestion_date = Column(DateTime, default=datetime.utcnow)
    version = Column(String(20))
    status = Column(String(20), default="pending")
    record_count = Column(Integer, default=0)
    quality_status = Column(String(20), default="unchecked")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
