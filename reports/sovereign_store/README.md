# Sovereign data store — Making Sense Bali / PLANETAI node

A **local, Bali-resident TimescaleDB** plus an ingest that **mirrors the Smart
Citizen sensor data into it**, so the Bali node holds its **own authoritative copy**
of citizen-sensor readings instead of depending on the Barcelona Smart Citizen
backend (`api.smartcitizen.me`).

## Why this exists (the sovereignty / CARE rationale)

Today the Smart Citizen Kits report to the Barcelona backend, and the node merely
reads from it — which means **Bali's raw citizen-sensor data physically lives in
Barcelona**. That is directly counter to PLANETAI's Governance pillar (**CARE:
"raw stays at the node, only approved embeddings federate"**, PKC
sovereignty-by-architecture). See `reports/ai_infra/PLANETAI_NODE_V0_SPEC.md` §4 —
this is called out there as the one gap that changes the architecture, and the
prerequisite for honest CARE governance and the Serangan trust-ring model.

This store closes that gap:

- **Raw stays in Bali.** The authoritative time-series lives in a local TimescaleDB
  on the NAS, port-bound to loopback only.
- **Smart Citizen becomes a *peer to federate to*, not a backend to depend on.** We
  stop being a read client of Barcelona for our own data.
- **Only council-approved MRL embeddings federate up** to the bioregion server —
  never the raw readings.

## What's here

| File | What it is |
|---|---|
| `schema.sql` | TimescaleDB schema: `readings` hypertable (long/EAV: one row per device·ts·metric), `devices` registry, indexes. Idempotent. |
| `ingest.py` | stdlib + `requests` + `psycopg2`/`psycopg`. Pulls current readings from the worker proxy and upserts them. `--once` or loop. Never-crash per device. |
| `docker-compose.snippet.yml` | TimescaleDB service snippet (NOT auto-applied). Loopback-only, named volume, joins the `aq-reporter` network. |
| `requirements.txt` | `requests`, `psycopg2-binary` (or `psycopg[binary]`). |

## Metrics mirrored

Each SC sensor object carries a stable `default_key`; ingest matches on that first
(then a `name` substring fallback, mirroring `data.js`):

| Canonical metric | SC `default_key` | Unit |
|---|---|---|
| `pm25` | `pm_avg_2.5` | µg/m³ (primary AQ metric) |
| `pm10` | `pm_avg_10` | µg/m³ |
| `temp` | `t` | °C |
| `humidity` | `h` | %RH |
| `noise` | `noise_dba` | dBA |

Per sensor we read `value` + `last_reading_at`, and the device's
`location.latitude` / `location.longitude` (denormalised onto each reading row).

## Configuration (all env — no secrets in the repo)

| Env var | Default | Notes |
|---|---|---|
| `AQ_STORE_DSN` | _(unset)_ | **Required to write.** e.g. `postgresql://msb:PASS@localhost:5432/msb`. Password lives only here, injected at deploy from a non-git NAS env file. |
| `AQ_SCK_PROXY` | `https://scb-bali.tomas-74b.workers.dev/sck` | Worker-proxy base. |
| `AQ_SCK_DEVICES` | `19236,19600,19618,19651` | SC device ids: house `19236`, office `19600`, plus `19618` / `19651`. |
| `AQ_INGEST_INTERVAL` | `600` | Loop sleep seconds. |
| `AQ_HTTP_TIMEOUT` | `20` | Per-request HTTP timeout. |

**No secret is stored in this repo.** The DB password is supplied only through
`AQ_STORE_DSN` (ingest) and `${TIMESCALE_PASSWORD}` (compose), both sourced at
deploy time from an env file kept outside git on the NAS.

## Deploy (by hand — nothing here auto-deploys)

1. **Run TimescaleDB.** Merge `docker-compose.snippet.yml`'s `timescaledb` service
   into the NAS aq-reporter compose, set `TIMESCALE_PASSWORD` from the non-git env
   file, and bring it up. The port stays bound to `127.0.0.1` only.
2. **Apply the schema.**
   ```bash
   psql "$AQ_STORE_DSN" -f schema.sql
   ```
3. **Set the DSN + run the ingest.**
   ```bash
   export AQ_STORE_DSN='postgresql://msb:REAL_PW@localhost:5432/msb'
   python3 ingest.py --once          # one pass (smoke test / backfill)
   python3 ingest.py                 # loop (default 600s) — run as a container/service
   ```
   In production the ingest runs as a small sidecar container on the
   `aq-reporter` network (same pattern as the vision worker), reaching the DB as
   host `timescaledb`.

## How the dashboard / Agent-1 read from it

- **Dashboard:** instead of (or in addition to) calling the SC proxy in `data.js`,
  the map/time-series can read the local store — latest value per device·metric for
  pins, and `(device_id, metric, ts)` range scans for charts. The
  `readings_device_metric_ts_idx` index serves exactly that, newest-first.
- **Agent-1** (the air-quality response agent, spec §3) reads PM2.5 series straight
  from `readings` for its 5 km / 60-min sustained-peak gate — against Bali's own
  copy, no Barcelona round-trip, and with full local history regardless of SC API
  availability.

## Later — fully cut the Barcelona dependency

**For now this MIRRORS via the proxy** — it gives Bali a complete local copy
immediately, with zero firmware changes, but the kits still publish to Barcelona
first. The next step is to **point the SC kit firmware (or a small local collector
on the LAN) directly at a Bali endpoint** so readings land in this store *first*,
making Smart Citizen a true downstream peer we choose to federate to rather than a
backend we depend on. At that point the proxy mirror is no longer load-bearing and
the sovereignty gap in §4 is fully closed.
