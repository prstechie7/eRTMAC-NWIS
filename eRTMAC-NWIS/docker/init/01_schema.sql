-- ═══════════════════════════════════════════════════════════════════════════
-- eRTMAC-NWIS Database Schema
-- Runs automatically on first PostgreSQL container start
-- Extensions: PostGIS 3D, TimescaleDB, pgvector
-- ═══════════════════════════════════════════════════════════════════════════

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. WELLS MASTER TABLE
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wells (
    well_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    well_name       VARCHAR(128) NOT NULL,               -- e.g., 'SYN-NHK-01' (Synthetic)
    display_name    VARCHAR(128),                        -- e.g., 'Nahorkatiya Synthetic 01'
    field_name      VARCHAR(128) NOT NULL,               -- e.g., 'Nahorkatiya'
    operator        VARCHAR(64)  DEFAULT 'Oil India Limited',
    data_source     VARCHAR(64)  DEFAULT 'SYNTHETIC',    -- 'SYNTHETIC' | 'VOLVE_PROXY' | 'LIVE'
    -- Surface location: WGS84 lat/lon with elevation (EPSG:4326)
    surface_lat     NUMERIC(10,7) NOT NULL,
    surface_lon     NUMERIC(10,7) NOT NULL,
    surface_location GEOMETRY(PointZ, 4326),             -- Populated by trigger
    kb_elevation_m  NUMERIC(7,2) NOT NULL DEFAULT 112.0, -- Kelly Bushing elevation, ~112m typical NHK
    spud_date       DATE,
    total_depth_m   NUMERIC(8,2),
    status          VARCHAR(32)  DEFAULT 'COMPLETED',    -- 'DRILLING' | 'COMPLETED' | 'ABANDONED'
    notes           TEXT,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Auto-populate geometry from lat/lon
CREATE OR REPLACE FUNCTION populate_well_geometry()
RETURNS TRIGGER AS $$
BEGIN
    NEW.surface_location = ST_SetSRID(
        ST_MakePoint(NEW.surface_lon, NEW.surface_lat, COALESCE(NEW.kb_elevation_m, 0)),
        4326
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_well_geometry ON wells;
CREATE TRIGGER trg_well_geometry
BEFORE INSERT OR UPDATE ON wells
FOR EACH ROW EXECUTE FUNCTION populate_well_geometry();

CREATE UNIQUE INDEX IF NOT EXISTS idx_wells_name ON wells(well_name);
CREATE INDEX IF NOT EXISTS idx_wells_surface ON wells USING GIST(surface_location);
CREATE INDEX IF NOT EXISTS idx_wells_field   ON wells(field_name);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. 3D TRAJECTORY STATIONS (Minimum Curvature Method computed)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trajectory_stations (
    station_id  BIGSERIAL PRIMARY KEY,
    well_id     UUID NOT NULL REFERENCES wells(well_id) ON DELETE CASCADE,
    md_m        NUMERIC(8,2) NOT NULL,     -- Measured Depth
    inc_deg     NUMERIC(6,3) NOT NULL,     -- Inclination (deg from vertical)
    azi_deg     NUMERIC(6,3) NOT NULL,     -- Azimuth (deg from North, TN)
    -- MCM-computed positions (stored for fast spatial queries)
    tvd_m       NUMERIC(8,2) NOT NULL,     -- True Vertical Depth
    tvdss_m     NUMERIC(8,2) NOT NULL,     -- True Vertical Depth Subsea (TVD - KB elevation)
    north_m     NUMERIC(10,3) NOT NULL,    -- Northing from well origin (metres)
    east_m      NUMERIC(10,3) NOT NULL,    -- Easting from well origin (metres)
    -- 3D geometry in EPSG:3857 (Web Mercator) for PostGIS 3D distance queries
    geom_3d     GEOMETRY(PointZ, 3857) NOT NULL,
    dogleg_deg_per_30m NUMERIC(5,3)        -- Computed dogleg severity
);

CREATE INDEX IF NOT EXISTS idx_traj_well   ON trajectory_stations(well_id, md_m);
CREATE INDEX IF NOT EXISTS idx_traj_geom3d ON trajectory_stations USING GIST(geom_3d);
CREATE INDEX IF NOT EXISTS idx_traj_tvdss  ON trajectory_stations(tvdss_m);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. ASSAM BASIN STRATIGRAPHIC TOPS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS formation_tops (
    top_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    well_id         UUID NOT NULL REFERENCES wells(well_id) ON DELETE CASCADE,
    formation_name  VARCHAR(128) NOT NULL,   -- e.g., 'Tipam Sandstone (Upper)'
    formation_code  VARCHAR(32),             -- e.g., 'TIPAM_U', 'BARAIL', 'KOPILI'
    top_md_m        NUMERIC(8,2) NOT NULL,
    top_tvdss_m     NUMERIC(8,2) NOT NULL,
    base_md_m       NUMERIC(8,2),
    base_tvdss_m    NUMERIC(8,2),
    dip_angle_deg   NUMERIC(4,1) DEFAULT 0.0,     -- Local structural dip
    dip_azimuth_deg NUMERIC(5,1) DEFAULT 0.0,     -- Dip direction (azimuth)
    lithology_desc  VARCHAR(128),
    pore_pressure_sg NUMERIC(4,3),               -- Formation PP in SG EMW
    frac_gradient_sg NUMERIC(4,3),               -- Fracture gradient in SG EMW
    data_confidence VARCHAR(16) DEFAULT 'SYNTHETIC' -- 'SYNTHETIC' | 'PUBLISHED' | 'MEASURED'
);

CREATE INDEX IF NOT EXISTS idx_tops_well      ON formation_tops(well_id);
CREATE INDEX IF NOT EXISTS idx_tops_formation ON formation_tops(formation_code);
CREATE INDEX IF NOT EXISTS idx_tops_tvdss     ON formation_tops(top_tvdss_m);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. DRILLING HAZARDS & NPT EVENTS (Core knowledge base)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS drilling_hazards (
    hazard_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    well_id          UUID NOT NULL REFERENCES wells(well_id) ON DELETE CASCADE,
    formation_name   VARCHAR(128) NOT NULL,
    formation_code   VARCHAR(32),
    -- Depths
    depth_md_m       NUMERIC(8,2) NOT NULL,
    depth_tvdss_m    NUMERIC(8,2) NOT NULL,
    -- Classification
    hazard_type      VARCHAR(64) NOT NULL,  -- see CHECK constraint below
    hazard_subtype   VARCHAR(64),           -- e.g., 'DIFFERENTIAL' | 'MECHANICAL' for STUCK_PIPE
    severity_level   INT CHECK (severity_level BETWEEN 1 AND 5),
    npt_hours        NUMERIC(6,2),
    -- Drilling parameters at time of event
    mud_density_sg   NUMERIC(4,3),
    ecd_sg           NUMERIC(4,3),
    wob_klbs         NUMERIC(5,1),
    rpm              NUMERIC(5,1),
    rop_mhr          NUMERIC(5,2),
    -- Narrative (human-readable; used for semantic search)
    failure_cause    TEXT NOT NULL,
    mitigation_action TEXT NOT NULL,
    outcome          TEXT,
    report_reference VARCHAR(256),           -- e.g., 'DDR-NHK-114-Day-47' or 'WCR-MORAN-042'
    -- AI embedding for semantic similarity (generated by sentence-transformers all-MiniLM-L6-v2)
    -- Dimension: 384 (lightweight, no API key needed, runs CPU)
    narrative_embedding VECTOR(384),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_hazard_type CHECK (hazard_type IN (
        'DIFFERENTIAL_STICKING', 'MECHANICAL_STICKING', 'LOST_CIRCULATION',
        'GAS_KICK', 'WELLBORE_INSTABILITY', 'PACK_OFF', 'BIT_BALLING',
        'WASHOUT', 'MOTOR_FAILURE', 'CASING_WEAR', 'MUD_LOSSES', 'BLOWOUT'
    ))
);

-- NOTE: Using flat cosine search (no HNSW) — correct choice for <1000 records.
-- HNSW index can be added later: CREATE INDEX ... USING hnsw (narrative_embedding vector_cosine_ops)
CREATE INDEX IF NOT EXISTS idx_hazard_well      ON drilling_hazards(well_id);
CREATE INDEX IF NOT EXISTS idx_hazard_type      ON drilling_hazards(hazard_type);
CREATE INDEX IF NOT EXISTS idx_hazard_tvdss     ON drilling_hazards(depth_tvdss_m);
CREATE INDEX IF NOT EXISTS idx_hazard_formation ON drilling_hazards(formation_code);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. LIVE TELEMETRY (TimescaleDB Hypertable — 1 Hz WITSML sensor stream)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS live_telemetry (
    time                    TIMESTAMPTZ     NOT NULL,
    well_id                 UUID            NOT NULL,
    bit_depth_md_m          NUMERIC(8,2)    NOT NULL,
    hook_load_klbs          NUMERIC(6,1),
    wob_klbs                NUMERIC(5,1),
    surface_torque_kftlb    NUMERIC(6,2),
    rpm                     NUMERIC(5,1),
    standpipe_pressure_psi  NUMERIC(7,1),
    flow_rate_gpm           NUMERIC(6,1),
    rop_mhr                 NUMERIC(5,2),
    mud_density_in_sg       NUMERIC(4,3),
    mud_density_out_sg      NUMERIC(4,3),
    ecd_downhole_sg         NUMERIC(4,3),
    annular_temp_c          NUMERIC(5,1),
    gas_total_pct           NUMERIC(5,2),
    gas_c1_pct              NUMERIC(5,2),   -- Methane
    gas_c2_pct              NUMERIC(5,3),   -- Ethane
    pit_volume_gain_bbls    NUMERIC(7,1),   -- Flow check indicator
    flow_out_pct            NUMERIC(5,1)    -- % of flow in; <95% = potential loss; >105% = kick
);

-- Convert to TimescaleDB hypertable (time-partitioned, with compression)
SELECT create_hypertable('live_telemetry', 'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Compress chunks older than 7 days
ALTER TABLE live_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'time DESC',
    timescaledb.compress_segmentby = 'well_id'
);

CREATE INDEX IF NOT EXISTS idx_telemetry_well_time ON live_telemetry(well_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_depth     ON live_telemetry(bit_depth_md_m);

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. LOOK-AHEAD ALERTS (Persisted alert log)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS look_ahead_alerts (
    alert_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    active_well_id   UUID REFERENCES wells(well_id),
    triggered_at     TIMESTAMPTZ DEFAULT NOW(),
    current_bit_md   NUMERIC(8,2) NOT NULL,
    current_tvdss    NUMERIC(8,2) NOT NULL,
    lookahead_tvdss  NUMERIC(8,2) NOT NULL,      -- TVDSS depth of projected hazard
    risk_index       NUMERIC(6,2),               -- R_H score (0-100)
    risk_level       VARCHAR(16),                -- 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
    hazard_type      VARCHAR(64),
    formation_code   VARCHAR(32),
    evidence_well_ids UUID[],                    -- Array of offset wells that triggered alert
    alert_json       JSONB,                      -- Full structured advisory card as JSON
    acknowledged     BOOLEAN DEFAULT FALSE,
    acknowledged_by  VARCHAR(128),
    pdf_exported     BOOLEAN DEFAULT FALSE
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. KEY SPATIAL QUERY: Find offset wells within 3D radius of current bit position
-- ─────────────────────────────────────────────────────────────────────────────
-- USAGE: Find all trajectory stations within 5km surface radius AND
--        within ±200m TVDSS of the current bit position
-- This is the core spatial engine for offset well selection.

CREATE OR REPLACE FUNCTION find_offset_wells(
    p_active_well_id    UUID,
    p_bit_lat           DOUBLE PRECISION,    -- Active bit surface location (approx)
    p_bit_lon           DOUBLE PRECISION,
    p_bit_tvdss         DOUBLE PRECISION,    -- Current bit TVDSS (metres)
    p_surface_radius_m  DOUBLE PRECISION DEFAULT 5000,  -- 5 km surface radius
    p_tvdss_window_m    DOUBLE PRECISION DEFAULT 200    -- ±200m TVDSS window
)
RETURNS TABLE (
    well_id         UUID,
    well_name       VARCHAR,
    field_name      VARCHAR,
    data_source     VARCHAR,
    surface_dist_m  DOUBLE PRECISION,
    min_tvdss_m     DOUBLE PRECISION,
    max_tvdss_m     DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        w.well_id,
        w.well_name,
        w.field_name,
        w.data_source,
        ST_Distance(
            w.surface_location::geography,
            ST_SetSRID(ST_MakePoint(p_bit_lon, p_bit_lat), 4326)::geography
        ) AS surface_dist_m,
        (MIN(ts.tvdss_m) OVER (PARTITION BY w.well_id))::DOUBLE PRECISION AS min_tvdss_m,
        (MAX(ts.tvdss_m) OVER (PARTITION BY w.well_id))::DOUBLE PRECISION AS max_tvdss_m
    FROM wells w
    JOIN trajectory_stations ts ON w.well_id = ts.well_id
    WHERE
        (p_active_well_id IS NULL OR w.well_id != p_active_well_id)
        AND w.status = 'COMPLETED'
        -- Surface radius filter (fast, uses geography index)
        AND ST_DWithin(
            w.surface_location::geography,
            ST_SetSRID(ST_MakePoint(p_bit_lon, p_bit_lat), 4326)::geography,
            p_surface_radius_m
        )
        -- TVDSS window filter (offset well must have data near current bit depth)
        AND ts.tvdss_m BETWEEN (p_bit_tvdss - p_tvdss_window_m)
                            AND (p_bit_tvdss + p_tvdss_window_m)
    ORDER BY surface_dist_m ASC;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions to application user nwis
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nwis;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nwis;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO nwis;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO nwis;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO nwis;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO nwis;
