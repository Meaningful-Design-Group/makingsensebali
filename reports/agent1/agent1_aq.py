#!/usr/bin/env python3
"""
Agent-1 — air-quality response agent (Making Sense Bali / PLANETAI node).

Scoped against PLANETAI_NODE_V0_SPEC.md §3 and the core-ideas paper
(§"Action agents"). This is the node-side response agent: it watches the
community PM2.5 series around one or more hub anchors, and when a hub's
PM2.5 stays above a community-agreed threshold for a sustained window, it
drafts a bilingual (Bahasa Indonesia + English) advisory, attaches a short
list of fabricable open-hardware air filters, and QUEUES it for human
approval. It NEVER auto-sends — the human approval gate is the paper's
responsible-AI requirement. Delivery (WhatsApp/Evolution) happens only after
an operator approves, and is done by the existing channel, not by this agent.

The whole point of the agent is the ρ (response coefficient) clock: every
step is timestamped to a pre-registered log (rho_log.jsonl) so rho.py can
compute Coverage × Speed against a policy baseline. See prereg.md.

Design mirrors m1_vision_worker.py:
  - stdlib + requests only (psycopg2 optional, lazy, never required)
  - env-config with the AQ_* prefix
  - structured logging, signal-safe stop
  - never crashes the loop: every cycle is wrapped, failures are logged

Series source (two modes):
  - WITH AQ_AGENT_STORE_DSN  -> read the true PM2.5 history from the local
    sovereign TimescaleDB store (reports/sovereign_store/schema.sql, table
    `readings(device_id, ts, metric, value, lat, lng, source)`). This gives
    a real sustained-window measurement.
  - WITHOUT a DSN            -> poll the Smart Citizen worker-proxy for
    current values each cycle and maintain an in-memory rolling window across
    polls. Sustained-history is then only as long as the agent has been up,
    and is APPROXIMATE — this is logged loudly. Use the store for real runs.

Run
---
    # normal loop (needs network / store + exo)
    python3 agent1_aq.py

    # one cycle, offline, no model call — writes a rho_log line + queue file
    python3 agent1_aq.py --dry-run --no-exo

Env
---
    AQ_OPENAI_ENDPOINT     exo OpenAI-compatible base   (default http://100.112.110.7:52415/v1)
    AQ_OPENAI_MODEL        model id                     (default mlx-community/gemma-4-e4b-it-6bit)
    AQ_OPENAI_KEY          exo needs none; set if hosted
    AQ_AGENT_STORE_DSN     TimescaleDB DSN (optional). If set, read series from it.
    AQ_SCK_PROXY           Smart Citizen worker-proxy   (default https://scb-bali.tomas-74b.workers.dev/sck)
    AQ_PM25_THRESHOLD      community-agreed µg/m³        (default 35; WHO 24h is 15)
    AQ_SUSTAIN_MIN         sustained minutes to fire     (default 60)
    AQ_RADIUS_KM           hub radius                    (default 5)
    AQ_POLL_INTERVAL       loop seconds                  (default 600)
    AQ_COOLDOWN_HOURS      no refire per hub within      (default 3)
    AQ_REQUEST_TIMEOUT     exo HTTP timeout seconds      (default 90)
    AQ_AGENT_DIR           where hubs.json / queue / logs live (default: this file's dir)
    AQ_LOG_LEVEL           INFO/DEBUG                    (default INFO)
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# --- Paths -----------------------------------------------------------------

AGENT_DIR = Path(os.environ.get("AQ_AGENT_DIR", str(Path(__file__).resolve().parent)))
HUBS_FILE = AGENT_DIR / "hubs.json"
FILTERS_FILE = AGENT_DIR / "air_filters.json"
QUEUE_DIR = AGENT_DIR / "queue"
RHO_LOG = AGENT_DIR / "rho_log.jsonl"

QUEUE_DIR.mkdir(parents=True, exist_ok=True)

# --- Config ----------------------------------------------------------------

OPENAI_ENDPOINT = os.environ.get("AQ_OPENAI_ENDPOINT", "http://100.112.110.7:52415/v1")
OPENAI_MODEL = os.environ.get("AQ_OPENAI_MODEL", "mlx-community/gemma-4-e4b-it-6bit")
OPENAI_KEY = os.environ.get("AQ_OPENAI_KEY", "")

STORE_DSN = os.environ.get("AQ_AGENT_STORE_DSN", "").strip()
SCK_PROXY = os.environ.get("AQ_SCK_PROXY", "https://scb-bali.tomas-74b.workers.dev/sck").rstrip("/")

PM25_THRESHOLD = float(os.environ.get("AQ_PM25_THRESHOLD", "35"))
SUSTAIN_MIN = float(os.environ.get("AQ_SUSTAIN_MIN", "60"))
RADIUS_KM = float(os.environ.get("AQ_RADIUS_KM", "5"))
POLL_INTERVAL = float(os.environ.get("AQ_POLL_INTERVAL", "600"))
COOLDOWN_HOURS = float(os.environ.get("AQ_COOLDOWN_HOURS", "3"))
REQUEST_TIMEOUT = float(os.environ.get("AQ_REQUEST_TIMEOUT", "90"))

# WHO 2021 24h PM2.5 air-quality guideline, kept for the advisory context. The
# community threshold (PM25_THRESHOLD) is deliberately separate and configurable
# per spec — it is NOT the WHO value.
WHO_24H_PM25 = 15.0

logging.basicConfig(
    level=os.environ.get("AQ_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("agent1-aq")

_running = True


def _stop(*_: Any) -> None:
    global _running
    _running = False
    log.info("stopping after current cycle")


signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


# --- Geo (port of data.js / peaks.js distanceKm — haversine, km) ----------

def distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance in km. Direct port of peaks.js distanceKm()."""
    import math
    R = 6371.0
    to_rad = lambda d: d * math.pi / 180.0
    d_lat = to_rad(lat2 - lat1)
    d_lng = to_rad(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(d_lng / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


# --- Hubs ------------------------------------------------------------------

def load_hubs() -> List[Dict[str, Any]]:
    """Load hub anchors. Each hub: {name, lat, lng, ...}. Never raises."""
    try:
        raw = json.loads(HUBS_FILE.read_text())
        hubs = raw.get("hubs", []) if isinstance(raw, dict) else raw
        out = []
        for h in hubs:
            if not isinstance(h, dict):
                continue
            if "lat" not in h or "lng" not in h or "name" not in h:
                continue
            h.setdefault("slug", _slug(h["name"]))
            out.append(h)
        if not out:
            log.error("hubs.json had no usable hubs")
        return out
    except (OSError, json.JSONDecodeError) as e:
        log.error("could not load hubs.json (%s) — no hubs to run", e)
        return []


def _slug(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")


# --- Filters ---------------------------------------------------------------

def load_filters(lab_tags: Optional[set] = None, limit: int = 3) -> List[Dict[str, Any]]:
    """Load the OSHWA filter shortlist and pick up to `limit` fabricable ones.

    If lab_tags is given, prefer filters whose `fabricable_with` is a subset of
    (or overlaps) the lab inventory. With no tags we just take the first few
    (the catalog is hand-ordered easiest-first). Never raises.
    """
    try:
        raw = json.loads(FILTERS_FILE.read_text())
        items = raw.get("filters", []) if isinstance(raw, dict) else raw
    except (OSError, json.JSONDecodeError) as e:
        log.warning("could not load air_filters.json (%s)", e)
        return []

    if lab_tags:
        scored = []
        for f in items:
            tags = set(f.get("fabricable_with", []))
            overlap = len(tags & lab_tags)
            scored.append((overlap, f))
        scored.sort(key=lambda t: t[0], reverse=True)
        picked = [f for _, f in scored[:limit]]
    else:
        picked = items[:limit]

    # Return a compact projection for the advisory package
    return [
        {
            "id": f.get("id"),
            "name": f.get("name"),
            "url": f.get("url"),
            "type": f.get("type"),
            "fabricable_with": f.get("fabricable_with", []),
        }
        for f in picked
    ]


# --- Series sources --------------------------------------------------------
# A "series" is a list of (datetime, value) tuples, oldest..newest, of PM2.5
# readings from sensors within RADIUS_KM of a hub.

# In-memory rolling window for the no-DSN mode. Keyed by hub slug; each value
# is a list of (datetime, mean_pm25) appended once per poll. Trimmed to the
# sustain window + a margin so it can't grow unbounded.
_rolling: Dict[str, List[Tuple[datetime, float]]] = {}
_ROLLING_KEEP = timedelta(minutes=0)  # set in main() from SUSTAIN_MIN


def series_from_store(hub: Dict[str, Any], window_min: float) -> Optional[List[Tuple[datetime, float]]]:
    """Read the PM2.5 series for sensors within RADIUS_KM from the sovereign
    store. Returns None if the store is unavailable (so the caller can fall
    back). Never raises.

    Schema (reports/sovereign_store/schema.sql, authored in parallel):
        readings(device_id TEXT, ts TIMESTAMPTZ, metric TEXT,
                 value DOUBLE PRECISION, lat DOUBLE PRECISION,
                 lng DOUBLE PRECISION, source TEXT)
    We do the radius filter in SQL with the haversine formula so we don't pull
    the whole table. Readings are averaged into 1-minute buckets across all
    in-radius sensors to form a single hub series.
    """
    if not STORE_DSN:
        return None
    try:
        import psycopg2  # type: ignore
    except ImportError:
        log.warning("AQ_AGENT_STORE_DSN set but psycopg2 not installed — "
                    "falling back to proxy polling. `pip install psycopg2-binary`.")
        return None

    since = _now() - timedelta(minutes=window_min)
    # Haversine in SQL: 6371 * 2 * asin(sqrt(...)). %s params: lat, lat, lng, lat.
    sql = """
        SELECT date_trunc('minute', ts) AS minute, avg(value) AS pm25
        FROM readings
        WHERE metric = 'pm25'
          AND ts >= %s
          AND (
            6371 * 2 * asin(sqrt(
              power(sin(radians(lat - %s) / 2), 2)
              + cos(radians(%s)) * cos(radians(lat))
                * power(sin(radians(lng - %s) / 2), 2)
            ))
          ) <= %s
        GROUP BY minute
        ORDER BY minute ASC;
    """
    try:
        conn = psycopg2.connect(STORE_DSN)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (since, hub["lat"], hub["lat"], hub["lng"], RADIUS_KM))
                rows = cur.fetchall()
        finally:
            conn.close()
    except Exception as e:  # noqa: BLE001 — store down must not crash the agent
        log.warning("store query failed for hub %s (%s) — falling back to proxy", hub.get("name"), e)
        return None

    series: List[Tuple[datetime, float]] = []
    for minute, pm25 in rows:
        if pm25 is None:
            continue
        if minute.tzinfo is None:
            minute = minute.replace(tzinfo=timezone.utc)
        series.append((minute, float(pm25)))
    return series


def poll_proxy_current(hub: Dict[str, Any]) -> Optional[float]:
    """Poll the Smart Citizen worker-proxy for current PM2.5 of in-radius
    sensors and return their mean (or None if no in-radius reading). Never
    raises.

    Uses the same proxy + world_map discovery shape as data.js. We list devices
    via /devices/world_map (paged once — Bali is a tiny slice), keep those in
    radius, then read each device's current PM 2.5 sensor value from its detail.
    """
    try:
        # One page is plenty for the Bali bbox; mirror data.js per_page sizing.
        wm = _sck_get("/devices/world_map?per_page=500&page=1")
        if not isinstance(wm, list):
            return None
    except Exception as e:  # noqa: BLE001
        log.warning("proxy world_map failed (%s)", e)
        return None

    in_radius_ids = []
    for d in wm:
        lat = d.get("latitude", d.get("lat"))
        lng = d.get("longitude", d.get("lng", d.get("lon")))
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            continue
        if distance_km(hub["lat"], hub["lng"], lat, lng) <= RADIUS_KM:
            did = d.get("id")
            if did is not None:
                in_radius_ids.append(did)

    if not in_radius_ids:
        log.debug("hub %s: no SCK devices within %.1f km", hub.get("name"), RADIUS_KM)
        return None

    vals: List[float] = []
    for did in in_radius_ids:
        try:
            detail = _sck_get(f"/devices/{did}")
        except Exception as e:  # noqa: BLE001
            log.debug("device %s detail failed (%s)", did, e)
            continue
        v = _extract_pm25(detail)
        if v is not None:
            vals.append(v)

    if not vals:
        return None
    return sum(vals) / len(vals)


def _sck_get(path: str) -> Any:
    url = SCK_PROXY + path
    r = requests.get(url, headers={"Accept": "application/json"}, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _extract_pm25(detail: Dict[str, Any]) -> Optional[float]:
    """Pull a current PM2.5 value from a SCK device detail (data.js shape)."""
    if not isinstance(detail, dict):
        return None
    sensors = (detail.get("data") or {}).get("sensors") or detail.get("sensors") or []
    for s in sensors:
        name = (s.get("name") or "")
        if "PM 2.5" in name or "PM2.5" in name:
            v = s.get("value")
            if isinstance(v, (int, float)):
                return float(v)
    return None


def get_series(hub: Dict[str, Any], window_min: float, approximate_holder: Dict[str, bool]) -> List[Tuple[datetime, float]]:
    """Return the hub PM2.5 series for the sustain window. Prefers the store;
    otherwise updates and returns the in-memory rolling window from a fresh
    proxy poll. Sets approximate_holder['v'] True when running without the store.
    """
    s = series_from_store(hub, window_min)
    if s is not None:
        approximate_holder["v"] = False
        return s

    # No-DSN mode: poll current, append to rolling window, trim, return.
    approximate_holder["v"] = True
    slug = hub["slug"]
    cur = poll_proxy_current(hub)
    buf = _rolling.setdefault(slug, [])
    if cur is not None:
        buf.append((_now(), cur))
    # Trim to keep only the sustain window + a margin
    cutoff = _now() - (_ROLLING_KEEP if _ROLLING_KEEP > timedelta(0)
                       else timedelta(minutes=window_min * 2))
    _rolling[slug] = [(t, v) for (t, v) in buf if t >= cutoff]
    return list(_rolling[slug])


# --- Trigger ---------------------------------------------------------------

def sustained_exceedance(series: List[Tuple[datetime, float]],
                         threshold: float,
                         sustain_min: float) -> Tuple[bool, Optional[float]]:
    """True if the LATEST contiguous run above `threshold` spans >= sustain_min
    minutes. Returns (fired, latest_value).

    "Sustained" = from the most recent reading, walking backwards, every point
    is above threshold, and the span (newest_ts - oldest_in_run_ts) covers the
    window. We measure the time span of the above-threshold tail rather than
    counting points, so it's robust to irregular sampling.
    """
    if not series:
        return False, None
    series = sorted(series, key=lambda p: p[0])
    latest_ts, latest_val = series[-1]
    if latest_val <= threshold:
        return False, latest_val

    run_start_ts = latest_ts
    for ts, val in reversed(series):
        if val > threshold:
            run_start_ts = ts
        else:
            break
    span_min = (latest_ts - run_start_ts).total_seconds() / 60.0
    return (span_min >= sustain_min), latest_val


def _last_fired_at(hub_slug: str) -> Optional[datetime]:
    """Most recent detected_at for this hub from the rho_log, for cooldown."""
    if not RHO_LOG.exists():
        return None
    last: Optional[datetime] = None
    try:
        for line in RHO_LOG.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("hub") != hub_slug:
                continue
            det = ev.get("detected_at")
            if not det:
                continue
            try:
                t = datetime.fromisoformat(det)
            except ValueError:
                continue
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            if last is None or t > last:
                last = t
    except OSError:
        return None
    return last


def in_cooldown(hub_slug: str) -> bool:
    last = _last_fired_at(hub_slug)
    if last is None:
        return False
    return (_now() - last) < timedelta(hours=COOLDOWN_HOURS)


# --- Forecast stub ---------------------------------------------------------

def pull_forecast(hub: Dict[str, Any]) -> Dict[str, Any]:
    """Regional PM2.5 forecast. The paper specifies Aurora; v0 is a stub.
    Returns a dict; `available` is False until the Aurora subscribe is wired.
    """
    return {"available": False, "note": "Aurora subscribe TODO", "hub": hub.get("name")}


# --- Advisory drafting (exo, text-only) ------------------------------------

def _advisory_prompt(hub_name: str, pm25: float, threshold: float) -> str:
    return f"""You are the community air-quality assistant for {hub_name}, a
neighbourhood (banjar) in Bali, Indonesia. Local citizen PM2.5 sensors have
measured fine-particle pollution at about {pm25:.0f} µg/m³, which is above the
community alert threshold of {threshold:.0f} µg/m³ (for reference, the WHO 24h
guideline is {WHO_24H_PM25:.0f} µg/m³).

Write a SHORT community air-quality advisory, BILINGUAL: first in Bahasa
Indonesia, then in English. Keep each version to 3-4 short sentences.

Must include, in plain language (no jargon):
- the place name ({hub_name}) and that PM2.5 is currently elevated (~{pm25:.0f} µg/m³),
- practical guidance: vulnerable groups (children, elderly, pregnant people,
  those with asthma/heart conditions) should limit outdoor activity and wear a
  well-fitting mask (N95/KN95 if available); everyone should close windows and
  run an air filter indoors if they have one,
- a calm, non-alarming tone; this is guidance, not an emergency order.

Output ONLY the advisory text. Start with "PERINGATAN KUALITAS UDARA" for the
Indonesian section and "AIR QUALITY ADVISORY" for the English section. No
preamble, no notes, no markdown headers."""


def draft_advisory(hub: Dict[str, Any], pm25: float, threshold: float) -> Tuple[str, str]:
    """Call exo (OpenAI chat, text-only) to draft the bilingual advisory.
    Returns (advisory_text, model_label). Never raises — on failure returns a
    safe templated fallback so the queue item is still actionable by a human.

    Mirrors vision_analyzer._analyze_via_openai but text-only.
    """
    prompt = _advisory_prompt(hub["name"], pm25, threshold)
    headers = {"Content-Type": "application/json"}
    if OPENAI_KEY:
        headers["Authorization"] = f"Bearer {OPENAI_KEY}"
    try:
        resp = requests.post(
            f"{OPENAI_ENDPOINT.rstrip('/')}/chat/completions",
            headers=headers,
            json={
                "model": OPENAI_MODEL,
                # Gemma 4 is a reasoning model — give headroom (see vision_analyzer note).
                "max_tokens": 768,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        body = resp.json()
        text = (body["choices"][0]["message"]["content"] or "").strip()
        model_label = f"exo:{OPENAI_MODEL.split('/')[-1]}"
        if not text:
            log.warning("exo returned empty advisory — using fallback template")
            return _fallback_advisory(hub["name"], pm25, threshold), f"{model_label}:empty-fallback"
        return text, model_label
    except requests.RequestException as e:
        log.warning("exo advisory call failed (%s) — using fallback template", e)
        return _fallback_advisory(hub["name"], pm25, threshold), "fallback-template:exo-down"
    except (KeyError, IndexError, TypeError) as e:
        log.warning("exo response malformed (%s) — using fallback template", e)
        return _fallback_advisory(hub["name"], pm25, threshold), "fallback-template:bad-response"


def _fallback_advisory(hub_name: str, pm25: float, threshold: float) -> str:
    """Deterministic bilingual advisory used when the model is unavailable.
    Keeps the human-approval queue actionable offline."""
    return (
        f"PERINGATAN KUALITAS UDARA — {hub_name}\n"
        f"Sensor warga menunjukkan PM2.5 sekitar {pm25:.0f} µg/m³, di atas ambang "
        f"komunitas {threshold:.0f} µg/m³. Kelompok rentan (anak-anak, lansia, ibu "
        f"hamil, penderita asma/jantung) sebaiknya mengurangi aktivitas di luar dan "
        f"memakai masker (N95/KN95 bila ada). Tutup jendela dan nyalakan penyaring "
        f"udara di dalam ruangan jika tersedia.\n\n"
        f"AIR QUALITY ADVISORY — {hub_name}\n"
        f"Community sensors show PM2.5 around {pm25:.0f} µg/m³, above the community "
        f"threshold of {threshold:.0f} µg/m³. Vulnerable groups (children, the "
        f"elderly, pregnant people, those with asthma/heart conditions) should limit "
        f"outdoor activity and wear a well-fitting mask (N95/KN95 if available). "
        f"Close windows and run an indoor air filter if you have one."
    )


# --- Queue + rho_log -------------------------------------------------------

def write_queue_item(event_id: str, hub: Dict[str, Any], pm25: float,
                     advisory_text: str, model_label: str,
                     filters: List[Dict[str, Any]], forecast: Dict[str, Any],
                     detected_at: str, dry_run: bool) -> Path:
    """Write the advisory package to queue/AQ1_<slug>_<ts>.json, status pending."""
    ts_compact = datetime.fromisoformat(detected_at).strftime("%Y%m%d_%H%M%S")
    fname = f"AQ1_{hub['slug']}_{ts_compact}.json"
    path = QUEUE_DIR / fname
    pkg = {
        "event_id": event_id,
        "hub": hub["name"],
        "hub_slug": hub["slug"],
        "hub_coord": {"lat": hub["lat"], "lng": hub["lng"],
                      "coord_status": hub.get("coord_status", "unknown")},
        "detected_at": detected_at,
        "pm25": round(pm25, 1),
        "threshold": PM25_THRESHOLD,
        "who_24h_pm25": WHO_24H_PM25,
        "radius_km": RADIUS_KM,
        "sustain_min": SUSTAIN_MIN,
        "forecast": forecast,
        "advisory_text": advisory_text,
        "advisory_model": model_label,
        "filters": filters,
        "status": "pending_approval",
        "approved_at": None,
        "delivered_at": None,
        "dry_run": dry_run,
    }
    path.write_text(json.dumps(pkg, indent=2, ensure_ascii=False))
    return path


def append_rho_event(event_id: str, hub: Dict[str, Any], detected_at: str,
                     forecast_at: str, drafted_at: str, pm25: float,
                     dry_run: bool, approximate_window: bool) -> None:
    """Append one ρ-event line to rho_log.jsonl. approved_at / delivered_at
    start null and are stamped later by approve_agent1.py (or the dashboard)."""
    ev = {
        "event_id": event_id,
        "hub": hub["slug"],
        "hub_name": hub["name"],
        "detected_at": detected_at,
        "forecast_at": forecast_at,
        "drafted_at": drafted_at,
        "approved_at": None,
        "delivered_at": None,
        "pm25": round(pm25, 1),
        "threshold": PM25_THRESHOLD,
        "dry_run": dry_run,
        "window_approximate": approximate_window,
    }
    try:
        with RHO_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    except OSError as e:
        log.error("could not append rho_log event %s (%s)", event_id, e)


# --- Per-hub cycle ---------------------------------------------------------

def process_hub(hub: Dict[str, Any], dry_run: bool, use_exo: bool) -> bool:
    """Run the trigger for one hub. Returns True if it fired. Never raises."""
    name = hub["name"]
    if hub.get("coord_status") == "APPROX":
        log.info("hub %s uses an APPROX coordinate — confirm before production", name)

    approx_holder = {"v": False}
    try:
        series = get_series(hub, SUSTAIN_MIN, approx_holder)
    except Exception as e:  # noqa: BLE001
        log.exception("get_series failed for hub %s (%s)", name, e)
        return False

    if approx_holder["v"]:
        log.warning("hub %s: NO STORE DSN — sustained-window history is APPROXIMATE "
                    "(in-memory rolling window only, %d point(s) so far)", name, len(series))

    fired, latest_val = sustained_exceedance(series, PM25_THRESHOLD, SUSTAIN_MIN)
    log.info("hub %s: latest PM2.5=%s µg/m³, threshold=%.0f, points=%d → fired=%s",
             name, f"{latest_val:.1f}" if latest_val is not None else "n/a",
             PM25_THRESHOLD, len(series), fired)

    # In dry-run with no real data, force one synthetic firing so we exercise
    # the full draft→queue→rho_log path offline (clearly marked dry_run).
    synthetic = False
    if dry_run and not fired:
        synthetic = True
        latest_val = max(latest_val or 0.0, PM25_THRESHOLD + 10.0)
        log.info("hub %s: --dry-run with no live exceedance → synthesizing a "
                 "trigger at PM2.5=%.0f to exercise the pipeline", name, latest_val)
        fired = True

    if not fired:
        return False

    if not dry_run and in_cooldown(hub["slug"]):
        log.info("hub %s: in cooldown (<%.0fh since last event) — skipping", name, COOLDOWN_HOURS)
        return False

    # ---- FIRE ----
    event_id = uuid.uuid4().hex[:12]
    detected_at = _iso(_now())

    forecast = pull_forecast(hub)
    forecast_at = _iso(_now())

    pm25 = float(latest_val)
    if use_exo:
        advisory_text, model_label = draft_advisory(hub, pm25, PM25_THRESHOLD)
    else:
        advisory_text = _fallback_advisory(name, pm25, PM25_THRESHOLD)
        model_label = "no-exo:fallback-template"
        log.info("hub %s: --no-exo → using deterministic fallback advisory", name)
    drafted_at = _iso(_now())

    filters = load_filters(limit=3)

    queue_path = write_queue_item(
        event_id, hub, pm25, advisory_text, model_label, filters, forecast,
        detected_at, dry_run or synthetic,
    )
    append_rho_event(
        event_id, hub, detected_at, forecast_at, drafted_at, pm25,
        dry_run or synthetic, approx_holder["v"],
    )

    log.info("hub %s: FIRED event %s → queued %s (status=pending_approval, NOT sent)",
             name, event_id, queue_path.name)
    if dry_run:
        log.info("  [dry-run] would draft advisory (model=%s), attach %d filter(s): %s",
                 model_label, len(filters), ", ".join(f.get("name", "?") for f in filters))
        log.info("  [dry-run] advisory preview: %s", advisory_text.replace("\n", " ")[:160])
    return True


# --- Main loop -------------------------------------------------------------

def run_cycle(dry_run: bool, use_exo: bool) -> None:
    hubs = load_hubs()
    if not hubs:
        log.warning("no hubs configured — nothing to do this cycle")
        return
    for hub in hubs:
        if not _running:
            break
        try:
            process_hub(hub, dry_run, use_exo)
        except Exception as e:  # noqa: BLE001 — one bad hub must not stop the rest
            log.exception("unhandled error processing hub %s (%s)", hub.get("name"), e)


def main() -> None:
    global _ROLLING_KEEP
    parser = argparse.ArgumentParser(description="Agent-1 air-quality response agent")
    parser.add_argument("--dry-run", action="store_true",
                        help="run ONE cycle, force a synthetic trigger, write rho_log + "
                             "queue (marked dry_run), then exit")
    parser.add_argument("--no-exo", action="store_true",
                        help="skip the exo model call; use the deterministic fallback "
                             "advisory (lets --dry-run run fully offline)")
    args = parser.parse_args()

    use_exo = not args.no_exo
    _ROLLING_KEEP = timedelta(minutes=SUSTAIN_MIN * 2)

    log.info("Agent-1 starting — dir=%s threshold=%.0f µg/m³ sustain=%.0fmin radius=%.1fkm",
             AGENT_DIR, PM25_THRESHOLD, SUSTAIN_MIN, RADIUS_KM)
    log.info("series source: %s", "TimescaleDB store (DSN set)" if STORE_DSN
             else "Smart Citizen proxy + in-memory rolling window (APPROX sustained history)")
    log.info("exo: %s @ %s | exo-call=%s", OPENAI_MODEL, OPENAI_ENDPOINT, use_exo)

    if args.dry_run:
        log.info("DRY RUN — one cycle, no network required if --no-exo also set")
        run_cycle(dry_run=True, use_exo=use_exo)
        log.info("dry run complete — see %s and %s", RHO_LOG, QUEUE_DIR)
        return

    while _running:
        try:
            run_cycle(dry_run=False, use_exo=use_exo)
        except Exception as e:  # noqa: BLE001
            log.exception("cycle error (%s)", e)
        # Sleep in short slices so SIGTERM is responsive.
        slept = 0.0
        while _running and slept < POLL_INTERVAL:
            time.sleep(min(2.0, POLL_INTERVAL - slept))
            slept += 2.0

    log.info("Agent-1 stopped")


if __name__ == "__main__":
    main()
