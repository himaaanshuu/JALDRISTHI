from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
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
    resource_ids = Column(Text)  # JSON list of CKAN resource IDs


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
    category = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    is_demo_data = Column(Integer, default=1)
    source_id = Column(Integer, nullable=True)  # FK to data_sources.id


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


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
