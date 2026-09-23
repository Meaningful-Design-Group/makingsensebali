-- ============================================================================
-- Making Sense Bali / PLANETAI node — Sovereign local time-series store
-- TimescaleDB schema
-- ============================================================================
--
-- WHAT THIS IS
--   The authoritative, Bali-resident copy of the Smart Citizen sensor readings.
--   Today the kits report to the Barcelona backend (api.smartcitizen.me) and the
--   node merely reads from it — i.e. Bali's raw citizen-sensor data physically
--   lives in Barcelona, directly counter to PLANETAI's Governance pillar (CARE:
--   "raw stays at the node, only approved embeddings federate"). See
--   reports/ai_infra/PLANETAI_NODE_V0_SPEC.md §4.
--
--   This schema is the local store that closes that gap. The companion ingest.py
--   MIRRORS current readings from the worker proxy into here so Bali holds its own
--   copy. Later, the SC kit firmware / a local collector points directly at a Bali
--   endpoint and Smart Citizen becomes a *peer to federate to*, not a backend to
--   depend on — at which point the proxy mirror is no longer load-bearing.
--
-- WHY TIMESCALEDB
--   Sensor data is append-mostly time-series. TimescaleDB is Postgres + native
--   hypertables (transparent time-partitioning), which is also the paper's
--   bioregion-server choice. Anything that speaks Postgres (the dashboard,
--   Agent-1, psql) reads it with no special client.
--
-- HOW TO APPLY
--   psql "$AQ_STORE_DSN" -f schema.sql
--   (or: psql -h localhost -U msb -d msb -f schema.sql)
--   Idempotent: safe to re-run — uses IF NOT EXISTS / create_hypertable(if_not_exists).
--
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Extension. Must exist before create_hypertable() is called. On the
--    timescale/timescaledb image this is preloaded; CREATE EXTENSION just
--    registers it into this database.
-- ----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS timescaledb;


-- ----------------------------------------------------------------------------
-- 2. readings — one row per (device, timestamp, metric).
--
--    This is the raw, narrow ("long"/EAV) fact table: every observation is its
--    own row keyed by metric name, rather than a wide column-per-metric table.
--    That keeps the schema stable as kits gain/lose sensors and lets us mix
--    sources (Smart Citizen now; OpenAQ / Sensor.Community / a direct local
--    collector later) into one timeline without migrations.
--
--    Columns:
--      device_id  text   — stable per-device id. We store the Smart Citizen
--                          numeric kit id as text (e.g. '19236') so non-SC
--                          sources can use their own id scheme without a type clash.
--      ts         timestamptz — the reading's own timestamp (the sensor's
--                          last_reading_at), NOT ingest wall-clock. timestamptz so
--                          everything is unambiguous UTC regardless of server tz.
--      metric     text   — canonical metric name: 'pm25' | 'pm10' | 'temp' |
--                          'humidity' | 'noise'. (Mapping from SC default_key in
--                          ingest.py: pm_avg_2.5→pm25, pm_avg_10→pm10, t→temp,
--                          h→humidity, noise_dba→noise.)
--      value      double precision — the measured value in the sensor's native unit
--                          (µg/m³, °C, %RH, dBA).
--      lat,lng    double precision — device location at time of reading, denormalised
--                          onto the row so a single readings scan can map points
--                          without joining devices (kits can move; this records where
--                          it was when the reading landed).
--      source     text   — provenance, e.g. 'smartcitizen'. Lets us tell a mirrored
--                          reading apart from a future direct-from-kit reading and
--                          federate selectively.
--
--    PRIMARY KEY (device_id, ts, metric) — the natural key of an observation and
--    the idempotency guarantee: re-ingesting the same reading is a no-op via
--    ON CONFLICT DO NOTHING in ingest.py. A device cannot have two different
--    values for the same metric at the same instant.
--
--    NOTE (TimescaleDB constraint): a hypertable's PRIMARY KEY / UNIQUE indexes
--    MUST include the partitioning column (ts). It does — (device_id, ts, metric).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS readings (
    device_id   text             NOT NULL,
    ts          timestamptz      NOT NULL,
    metric      text             NOT NULL,
    value       double precision,
    lat         double precision,
    lng         double precision,
    source      text,
    PRIMARY KEY (device_id, ts, metric)
);

-- Promote readings to a hypertable partitioned on ts. if_not_exists keeps this
-- idempotent so the whole file can be re-applied. Default chunk interval (7 days)
-- is fine for this volume (a handful of kits, ~5 metrics, sub-hourly).
SELECT create_hypertable('readings', 'ts', if_not_exists => TRUE);


-- ----------------------------------------------------------------------------
-- 3. devices — current state / registry, one row per device (latest snapshot).
--
--    Small, mutable companion to the append-only readings table. Powers the map
--    pins and "is this kit alive?" checks without scanning the time-series.
--    last_seen is the freshest reading timestamp we've ingested for the device,
--    used for the dashboard's 14-day "active" window (see data.js isActive()).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS devices (
    device_id   text PRIMARY KEY,
    name        text,
    lat         double precision,
    lng         double precision,
    source      text,
    last_seen   timestamptz
);


-- ----------------------------------------------------------------------------
-- 4. Indexes.
--
--    The hypertable already gives an index on ts. The dominant read pattern is
--    "latest / recent values for one device + one metric" (dashboard time-series,
--    Agent-1's per-sensor PM2.5 peak detection within a window). This composite
--    index with ts DESC serves exactly that — newest-first range scans per
--    (device, metric) — and also covers the (device_id, metric) prefix.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS readings_device_metric_ts_idx
    ON readings (device_id, metric, ts DESC);

-- Cross-device "all readings for a metric in a time window" (e.g. region-wide
-- PM2.5 for a given hour) — metric-first so the scan isn't device-bound.
CREATE INDEX IF NOT EXISTS readings_metric_ts_idx
    ON readings (metric, ts DESC);
