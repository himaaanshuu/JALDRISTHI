-- ============================================================
-- JAL-DRISHTI Supabase Migration
-- Run this in: Supabase Dashboard → SQL Editor
-- ============================================================

-- Enable UUID extension (usually enabled by default)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Data Sources ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS data_sources (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(200) NOT NULL,
    source_url VARCHAR(500),
    organization VARCHAR(200),
    assessment_year INTEGER,
    publication_year INTEGER,
    retrieved_at VARCHAR(50),
    dataset_description TEXT,
    resource_ids TEXT
);

-- ─── Core Groundwater Assessment Data ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS groundwater (
    id BIGSERIAL PRIMARY KEY,
    state VARCHAR(100),
    district VARCHAR(100),
    block VARCHAR(100),
    assessment_year INTEGER,
    annual_groundwater_recharge DOUBLE PRECISION,
    extractable_groundwater_resource DOUBLE PRECISION,
    groundwater_extraction DOUBLE PRECISION,
    extraction_stage DOUBLE PRECISION,
    category VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_demo_data INTEGER DEFAULT 1,
    source_id INTEGER
);

CREATE INDEX IF NOT EXISTS ix_gw_state ON groundwater(state);
CREATE INDEX IF NOT EXISTS ix_gw_district ON groundwater(district);
CREATE INDEX IF NOT EXISTS ix_gw_block ON groundwater(block);
CREATE INDEX IF NOT EXISTS ix_gw_year ON groundwater(assessment_year);
CREATE INDEX IF NOT EXISTS ix_gw_category ON groundwater(category);
CREATE INDEX IF NOT EXISTS ix_gw_state_year ON groundwater(state, assessment_year);
CREATE INDEX IF NOT EXISTS ix_gw_district_year ON groundwater(district, assessment_year);
CREATE INDEX IF NOT EXISTS ix_gw_category_state ON groundwater(category, state);

-- ─── Groundwater Quality ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS groundwater_quality (
    id BIGSERIAL PRIMARY KEY,
    state VARCHAR(100),
    district VARCHAR(100),
    block VARCHAR(100),
    station_id VARCHAR(50),
    assessment_year INTEGER,
    fluoride_mg_l DOUBLE PRECISION,
    arsenic_ug_l DOUBLE PRECISION,
    nitrate_mg_l DOUBLE PRECISION,
    iron_mg_l DOUBLE PRECISION,
    tds_mg_l DOUBLE PRECISION,
    ec_umho_cm DOUBLE PRECISION,
    ph DOUBLE PRECISION,
    chloride_mg_l DOUBLE PRECISION,
    sulphate_mg_l DOUBLE PRECISION,
    hardness_mg_l DOUBLE PRECISION,
    uranium_ug_l DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    source_id INTEGER
);

CREATE INDEX IF NOT EXISTS ix_gwq_state ON groundwater_quality(state);
CREATE INDEX IF NOT EXISTS ix_gwq_year ON groundwater_quality(assessment_year);
CREATE INDEX IF NOT EXISTS ix_gwq_district ON groundwater_quality(district);

-- ─── Groundwater Levels ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS groundwater_levels (
    id BIGSERIAL PRIMARY KEY,
    state VARCHAR(100),
    district VARCHAR(100),
    block VARCHAR(100),
    station_id VARCHAR(50),
    assessment_year INTEGER,
    pre_monsoon_level_m DOUBLE PRECISION,
    post_monsoon_level_m DOUBLE PRECISION,
    annual_fluctuation_m DOUBLE PRECISION,
    groundwater_status VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    source_id INTEGER
);

CREATE INDEX IF NOT EXISTS ix_gwl_state ON groundwater_levels(state);
CREATE INDEX IF NOT EXISTS ix_gwl_year ON groundwater_levels(assessment_year);

-- ─── Water Readings (Sensor Data) ───────────────────────────────────────────

CREATE TABLE IF NOT EXISTS water_readings (
    id BIGSERIAL PRIMARY KEY,
    station_id VARCHAR(50),
    water_level DOUBLE PRECISION,
    rainfall_mm DOUBLE PRECISION,
    ph_level DOUBLE PRECISION,
    turbidity DOUBLE PRECISION,
    "timestamp" TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'normal'
);

-- ─── Conversation Memory ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS conversation_history (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(50),
    role VARCHAR(10),
    message TEXT,
    "timestamp" TIMESTAMP DEFAULT NOW(),
    query_type VARCHAR(50),
    entities TEXT
);

CREATE INDEX IF NOT EXISTS ix_conv_session ON conversation_history(session_id);

-- ─── Dataset Tracking ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dataset_versions (
    id BIGSERIAL PRIMARY KEY,
    dataset_id VARCHAR(100) UNIQUE,
    dataset_name VARCHAR(200),
    year INTEGER,
    geographic_scope VARCHAR(100),
    ingestion_date TIMESTAMP DEFAULT NOW(),
    version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    record_count INTEGER DEFAULT 0,
    quality_status VARCHAR(20) DEFAULT 'unchecked'
);

-- ─── Row Level Security (RLS) ───────────────────────────────────────────────
-- Enable RLS on all tables (allows public read via anon key)

ALTER TABLE data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE groundwater ENABLE ROW LEVEL SECURITY;
ALTER TABLE groundwater_quality ENABLE ROW LEVEL SECURITY;
ALTER TABLE groundwater_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE water_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE dataset_versions ENABLE ROW LEVEL SECURITY;

-- Public read policies (anon key can read all data)
CREATE POLICY "Public read on data_sources" ON data_sources FOR SELECT USING (true);
CREATE POLICY "Public read on groundwater" ON groundwater FOR SELECT USING (true);
CREATE POLICY "Public read on groundwater_quality" ON groundwater_quality FOR SELECT USING (true);
CREATE POLICY "Public read on groundwater_levels" ON groundwater_levels FOR SELECT USING (true);
CREATE POLICY "Public read on water_readings" ON water_readings FOR SELECT USING (true);
CREATE POLICY "Public read on conversation_history" ON conversation_history FOR SELECT USING (true);
CREATE POLICY "Public read on dataset_versions" ON dataset_versions FOR SELECT USING (true);

-- Public insert policies (anon key can insert)
CREATE POLICY "Public insert on groundwater" ON groundwater FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert on water_readings" ON water_readings FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert on data_sources" ON data_sources FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert on groundwater_quality" ON groundwater_quality FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert on groundwater_levels" ON groundwater_levels FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert on conversation_history" ON conversation_history FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert on dataset_versions" ON dataset_versions FOR INSERT WITH CHECK (true);

-- Public update policies
CREATE POLICY "Public update on groundwater" ON groundwater FOR UPDATE USING (true);
CREATE POLICY "Public update on dataset_versions" ON dataset_versions FOR UPDATE USING (true);
CREATE POLICY "Public update on water_readings" ON water_readings FOR UPDATE USING (true);

-- Public delete policies
CREATE POLICY "Public delete on groundwater" ON groundwater FOR DELETE USING (true);
CREATE POLICY "Public delete on water_readings" ON water_readings FOR DELETE USING (true);
CREATE POLICY "Public delete on conversation_history" ON conversation_history FOR DELETE USING (true);
