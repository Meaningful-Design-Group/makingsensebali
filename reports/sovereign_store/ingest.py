#!/usr/bin/env python3
"""
ingest.py — Making Sense Bali / PLANETAI node · sovereign-store ingest

Mirrors current Smart Citizen sensor readings into the LOCAL TimescaleDB store
(schema.sql) so Bali holds its own authoritative copy instead of depending on the
Barcelona Smart Citizen backend. See reports/ai_infra/PLANETAI_NODE_V0_SPEC.md §4
(the sovereignty gap) and reports/sovereign_store/README.md.

WHAT IT DOES
  For each known SC device it GETs /sck/devices/{id} from the worker proxy, walks
  the device's sensor array, reads each sensor's `value` + `last_reading_at`, and
  upserts one row per metric into `readings` (ON CONFLICT DO NOTHING — idempotent),
  then updates the `devices` registry row. The device's
  location.latitude/longitude is denormalised onto every reading.

WHY THE PROXY (for now)
  This MIRRORS via the same Cloudflare worker proxy the dashboard uses. It does NOT
  yet cut the Barcelona dependency — that is the *later* step (point kit firmware /
  a local collector directly at a Bali endpoint). Mirroring first means Bali has a
  full local copy immediately, with zero firmware changes, while keeping Smart
  Citizen as a peer to federate to rather than a backend to depend on.

METRICS MIRRORED  (canonical name  ←  SC sensor default_key)
  pm25      ← pm_avg_2.5      (µg/m³, PM2.5 — the dashboard's primary AQ metric)
  pm10      ← pm_avg_10       (µg/m³, PM10)
  temp      ← t               (°C, air temperature)
  humidity  ← h               (%RH, relative humidity)
  noise     ← noise_dba       (dBA)

  We match on the sensor's `default_key` first (the stable machine key), then fall
  back to a case-insensitive `name` substring match (e.g. "PM 2.5") because the SC
  API has shipped both shapes over the years (mirrors data.js's defensive parsing).

CONFIG (all via env — NO SECRETS IN THE REPO)
  AQ_STORE_DSN        Postgres/Timescale DSN. REQUIRED to actually write.
                      e.g. postgresql://msb:PASS@localhost:5432/msb
                      The password lives only in this env var (injected at deploy
                      from a NAS-side env file outside git) — never hard-coded here.
  AQ_SCK_PROXY        Worker proxy base. Default the workers.dev/sck base below.
  AQ_SCK_DEVICES      Comma-separated SC device ids. Default "19236,19600,19618,19651"
                      (house 19236, office 19600, plus 19618 / 19651).
  AQ_INGEST_INTERVAL  Loop sleep seconds (loop mode only). Default 600 (10 min).
  AQ_HTTP_TIMEOUT     Per-request HTTP timeout seconds. Default 20.

MODES
  --once   run a single pass and exit (cron / smoke test / first backfill)
  (default) loop forever, sleeping AQ_INGEST_INTERVAL between passes

DESIGN NOTES
  - The DB connection is opened LAZILY inside run_once()/main() — importing this
    module or running `--help` never touches a database (none exists at build time).
  - Never-crash per device: one bad device/HTTP error is logged and skipped; the
    pass continues and the loop keeps running.
  - Idempotent: re-ingesting the same (device_id, ts, metric) is a no-op.

Requires: requests, and one of psycopg2(-binary) / psycopg[binary]. See requirements.txt.
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timezone

import requests

# ---------------------------------------------------------------------------
# Defaults / config (env-overridable). Read at call time, not import time, so
# tests and --help don't depend on the environment being set up.
# ---------------------------------------------------------------------------
DEFAULT_PROXY_BASE = "https://scb-bali.tomas-74b.workers.dev/sck"
DEFAULT_DEVICES = "19236,19600,19618,19651"
DEFAULT_INTERVAL = 600          # seconds between loop passes
DEFAULT_HTTP_TIMEOUT = 20       # seconds per HTTP request

# Canonical metric  ->  (SC sensor default_key, [name substrings for fallback match]).
# default_key is the stable machine key on each sensor object; the name fallbacks
# mirror data.js so we still catch a reading if the key shape ever changes.
METRIC_MAP = {
    "pm25":     ("pm_avg_2.5", ["pm 2.5", "pm2.5"]),
    "pm10":     ("pm_avg_10",  ["pm 10", "pm10"]),
    "temp":     ("t",          ["air temperature", "temperature"]),
    "humidity": ("h",          ["relative humidity", "humidity"]),
    "noise":    ("noise_dba",  ["noise"]),
}

SOURCE = "smartcitizen"

log = logging.getLogger("sovereign_ingest")


# ---------------------------------------------------------------------------
# psycopg import shim — support either psycopg2 (classic) or psycopg v3.
# Imported lazily inside connect() so module import never requires a driver.
# ---------------------------------------------------------------------------
def _import_psycopg():
    """Return (module, flavor) where flavor is 'psycopg2' or 'psycopg3'."""
    try:
        import psycopg2  # type: ignore
        return psycopg2, "psycopg2"
    except ImportError:
        pass
    try:
        import psycopg  # type: ignore  (psycopg v3)
        return psycopg, "psycopg3"
    except ImportError:
        pass
    raise RuntimeError(
        "No Postgres driver found. Install one:\n"
        "  pip install psycopg2-binary   (or)   pip install 'psycopg[binary]'"
    )


def connect(dsn):
    """Open a DB connection. Lazy: only called inside the run path."""
    driver, _flavor = _import_psycopg()
    conn = driver.connect(dsn)
    conn.autocommit = False
    return conn


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
def fetch_device(proxy_base, device_id, timeout):
    """GET /sck/devices/{id} via the proxy. Returns parsed JSON dict or raises."""
    url = f"{proxy_base.rstrip('/')}/devices/{device_id}"
    r = requests.get(url, headers={"Accept": "application/json"}, timeout=timeout)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Parsing helpers (pure; no I/O — easy to reason about / test)
# ---------------------------------------------------------------------------
def _extract_coords(detail):
    """Pull (lat, lng) from a device detail, tolerating SC's several shapes."""
    loc = detail.get("location") or {}
    candidates = [
        (loc.get("latitude"), loc.get("longitude")),
        (loc.get("lat"), loc.get("lng")),
        (detail.get("latitude"), detail.get("longitude")),
        (detail.get("lat"), detail.get("lng")),
    ]
    for la, ln in candidates:
        try:
            laf = float(la)
            lnf = float(ln)
        except (TypeError, ValueError):
            continue
        return laf, lnf
    return None, None


def _parse_ts(raw):
    """Parse an ISO-8601 timestamp to an aware UTC datetime, or None.

    Accepts trailing 'Z' (mapped to +00:00). Naive timestamps are assumed UTC.
    """
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _sensor_matches(sensor, default_key, name_subs):
    """True if this sensor object is the one for a given metric."""
    key = (sensor.get("default_key") or "").strip().lower()
    if key and key == default_key.lower():
        return True
    name = (sensor.get("name") or "").lower()
    return any(sub in name for sub in name_subs)


def extract_readings(detail, device_id):
    """Turn one device detail JSON into a list of reading rows.

    Returns (rows, device_meta) where:
      rows         = [(device_id, ts, metric, value, lat, lng, source), ...]
      device_meta  = {name, lat, lng, last_seen}  for the devices registry upsert
    Pure: no DB, no network. Reading-level errors are skipped, never raised.
    """
    sensors = (detail.get("data") or {}).get("sensors") or detail.get("sensors") or []
    lat, lng = _extract_coords(detail)
    name = detail.get("name") or f"Device {device_id}"

    rows = []
    last_seen = None
    for metric, (default_key, name_subs) in METRIC_MAP.items():
        sensor = next(
            (s for s in sensors if _sensor_matches(s, default_key, name_subs)),
            None,
        )
        if sensor is None:
            continue

        value = sensor.get("value")
        if value is None:
            continue
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        # Prefer the sensor's own last_reading_at; fall back to the device-level
        # recorded_at / last_reading_at so a reading still lands if the per-sensor
        # field is absent.
        ts = _parse_ts(sensor.get("last_reading_at"))
        if ts is None:
            ts = _parse_ts(
                (detail.get("data") or {}).get("recorded_at")
                or detail.get("last_reading_at")
            )
        if ts is None:
            continue  # no trustworthy timestamp -> skip (PK needs ts)

        rows.append((device_id, ts, metric, value, lat, lng, SOURCE))
        if last_seen is None or ts > last_seen:
            last_seen = ts

    device_meta = {"name": name, "lat": lat, "lng": lng, "last_seen": last_seen}
    return rows, device_meta


# ---------------------------------------------------------------------------
# DB writes
# ---------------------------------------------------------------------------
INSERT_READING_SQL = """
    INSERT INTO readings (device_id, ts, metric, value, lat, lng, source)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (device_id, ts, metric) DO NOTHING
"""

UPSERT_DEVICE_SQL = """
    INSERT INTO devices (device_id, name, lat, lng, source, last_seen)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (device_id) DO UPDATE SET
        name      = EXCLUDED.name,
        lat       = COALESCE(EXCLUDED.lat, devices.lat),
        lng       = COALESCE(EXCLUDED.lng, devices.lng),
        source    = EXCLUDED.source,
        -- only move last_seen forward
        last_seen = GREATEST(devices.last_seen, EXCLUDED.last_seen)
"""


def write_device(conn, device_id, rows, device_meta):
    """Insert reading rows + upsert the device row for ONE device in a txn.

    Returns the number of reading rows actually inserted (conflicts excluded).
    Commits on success; rolls back this device's txn on any error and re-raises
    to the caller, which logs and moves on (per-device isolation).
    """
    inserted = 0
    cur = conn.cursor()
    try:
        for row in rows:
            cur.execute(INSERT_READING_SQL, row)
            # rowcount is 1 on insert, 0 when the ON CONFLICT skipped it
            if cur.rowcount and cur.rowcount > 0:
                inserted += cur.rowcount
        cur.execute(
            UPSERT_DEVICE_SQL,
            (
                device_id,
                device_meta["name"],
                device_meta["lat"],
                device_meta["lng"],
                SOURCE,
                device_meta["last_seen"],
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
    return inserted


# ---------------------------------------------------------------------------
# One pass over all devices
# ---------------------------------------------------------------------------
def run_once(dsn, proxy_base, device_ids, http_timeout):
    """Run a single ingest pass. Opens the DB connection lazily here.

    Returns total reading rows inserted across all devices.
    """
    if not dsn:
        raise RuntimeError(
            "AQ_STORE_DSN is not set. Set it to your TimescaleDB DSN, e.g.\n"
            "  export AQ_STORE_DSN='postgresql://msb:PASS@localhost:5432/msb'"
        )

    log.info(
        "ingest pass start | devices=%s | proxy=%s",
        ",".join(device_ids), proxy_base,
    )
    conn = connect(dsn)
    total_inserted = 0
    try:
        for device_id in device_ids:
            # Never-crash per device: isolate fetch + parse + write.
            try:
                detail = fetch_device(proxy_base, device_id, http_timeout)
            except Exception as e:  # noqa: BLE001 — intentional broad catch per device
                log.warning("device %s fetch failed: %s", device_id, e)
                continue

            try:
                rows, device_meta = extract_readings(detail, device_id)
            except Exception as e:  # noqa: BLE001
                log.warning("device %s parse failed: %s", device_id, e)
                continue

            if not rows:
                log.info("device %s: no current readings to mirror", device_id)
                # Still record presence/coords if we have them.
                if device_meta["lat"] is not None:
                    try:
                        write_device(conn, device_id, [], device_meta)
                    except Exception as e:  # noqa: BLE001
                        log.warning("device %s registry update failed: %s", device_id, e)
                continue

            try:
                n = write_device(conn, device_id, rows, device_meta)
            except Exception as e:  # noqa: BLE001
                log.warning("device %s write failed: %s", device_id, e)
                continue

            total_inserted += n
            log.info(
                "device %s: %d/%d reading row(s) inserted (rest already present) | last_seen=%s",
                device_id, n, len(rows),
                device_meta["last_seen"].isoformat() if device_meta["last_seen"] else "n/a",
            )
    finally:
        conn.close()

    log.info("ingest pass done | total rows inserted=%d", total_inserted)
    return total_inserted


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def _parse_device_list(raw):
    return [d.strip() for d in (raw or "").split(",") if d.strip()]


def _env_int(name, default):
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        log.warning("%s=%r is not an int; using default %d", name, raw, default)
        return default


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ingest.py",
        description="Mirror Smart Citizen sensor readings into the local "
                    "TimescaleDB sovereign store (Making Sense Bali / PLANETAI node).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single ingest pass and exit (default: loop forever).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help=f"Loop sleep seconds (overrides AQ_INGEST_INTERVAL, default {DEFAULT_INTERVAL}).",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Config resolved here (call time), not at import.
    dsn = os.environ.get("AQ_STORE_DSN", "")
    proxy_base = os.environ.get("AQ_SCK_PROXY", DEFAULT_PROXY_BASE)
    device_ids = _parse_device_list(os.environ.get("AQ_SCK_DEVICES", DEFAULT_DEVICES))
    http_timeout = _env_int("AQ_HTTP_TIMEOUT", DEFAULT_HTTP_TIMEOUT)
    interval = args.interval if args.interval is not None else _env_int(
        "AQ_INGEST_INTERVAL", DEFAULT_INTERVAL
    )

    if not device_ids:
        log.error("No devices to ingest (AQ_SCK_DEVICES empty). Nothing to do.")
        return 2

    if args.once:
        run_once(dsn, proxy_base, device_ids, http_timeout)
        return 0

    # Loop mode. Top-level guard so a pass-level failure never kills the daemon.
    log.info("starting ingest loop | interval=%ds", interval)
    while True:
        try:
            run_once(dsn, proxy_base, device_ids, http_timeout)
        except Exception as e:  # noqa: BLE001 — keep the daemon alive across pass failures
            log.error("ingest pass crashed (will retry next interval): %s", e)
        time.sleep(interval)


if __name__ == "__main__":
    sys.exit(main())
