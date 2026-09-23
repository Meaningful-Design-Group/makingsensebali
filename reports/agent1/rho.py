#!/usr/bin/env python3
r"""
rho.py — compute the community response coefficient ρ_community from rho_log.jsonl.

This is the instrument the whole Agent-1 skeleton exists to produce. It reads
the pre-registered timestamp log written by agent1_aq.py and computes, per the
PLANETAI core-ideas paper (§"Action agents") and PLANETAI_NODE_V0_SPEC.md §3:

    Coverage  = (# events with a human approval within the latency budget)
                ----------------------------------------------------------
                (# events)

                i.e. the fraction of pre-registered PM2.5 trigger events that
                produced a human-approved advisory within AQ_LATENCY_BUDGET of
                detection. An event counts toward Coverage only if
                    0 <= (approved_at - detected_at) <= AQ_LATENCY_BUDGET.

    Speed     = AQ_POLICY_BASELINE_LATENCY / median Δt(detected_at→approved_at)
                clamped to [0, 1].

                Δt is the detection→approval latency of the FITTED responses
                (events that did get approved). Normalised against a
                pre-registered policy-baseline latency (the existing
                provincial AQ response time). Faster-than-baseline → Speed
                closer to 1; at/over baseline → Speed < 1, capped at 1 so a
                single very fast response cannot push ρ above its ceiling.

    ρ_community = Coverage × Speed,  in [0, 1].

A null result (no approvals yet) yields ρ = 0 with ALL components printed —
the paper makes the null publishable, so we never hide it and never collapse
the components into a single opaque number.

Latency budget vs policy baseline — two different clocks, don't conflate:
  - AQ_LATENCY_BUDGET           = how fast WE commit to approving (the SLA the
                                  pilot pre-registers). Gates Coverage.
  - AQ_POLICY_BASELINE_LATENCY  = how fast the STATUS QUO (provincial response)
                                  acts. The yardstick Speed is measured against.

Env
---
    AQ_AGENT_DIR                 dir holding rho_log.jsonl (default: this file's dir)
    AQ_LATENCY_BUDGET            seconds; Coverage window (default 86400 = 24h placeholder)
    AQ_POLICY_BASELINE_LATENCY   seconds; provincial baseline (default 86400 = 24h placeholder)
    AQ_RHO_INCLUDE_DRYRUN        "1" to include dry_run events (default 0 — excluded)

Both default latencies are 24h PLACEHOLDERS pending the pre-registered field
measurement (see prereg.md §policy-baseline). They MUST be set from a real
measured baseline before any ρ figure is published.

Usage
-----
    python3 rho.py
    python3 rho.py --json        # machine-readable, components included
"""

import argparse
import json
import os
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

AGENT_DIR = Path(os.environ.get("AQ_AGENT_DIR", str(Path(__file__).resolve().parent)))
RHO_LOG = AGENT_DIR / "rho_log.jsonl"

LATENCY_BUDGET = float(os.environ.get("AQ_LATENCY_BUDGET", "86400"))            # 24h placeholder
POLICY_BASELINE = float(os.environ.get("AQ_POLICY_BASELINE_LATENCY", "86400"))  # 24h placeholder
INCLUDE_DRYRUN = os.environ.get("AQ_RHO_INCLUDE_DRYRUN", "0") == "1"


def _parse_ts(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        t = datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t


def load_events() -> List[Dict[str, Any]]:
    if not RHO_LOG.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in RHO_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not INCLUDE_DRYRUN and ev.get("dry_run"):
            continue
        out.append(ev)
    return out


def compute_rho(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return all components + ρ. Never hides components; null → ρ=0."""
    n_events = len(events)

    # Detection→approval latencies (seconds) for events that were approved.
    fitted_latencies: List[float] = []
    n_within_budget = 0
    for ev in events:
        det = _parse_ts(ev.get("detected_at"))
        app = _parse_ts(ev.get("approved_at"))
        if det is None or app is None:
            continue
        dt = (app - det).total_seconds()
        if dt < 0:
            # Clock skew / bad data — don't credit it.
            continue
        fitted_latencies.append(dt)
        if dt <= LATENCY_BUDGET:
            n_within_budget += 1

    n_fitted = len(fitted_latencies)

    coverage = (n_within_budget / n_events) if n_events else 0.0

    median_dt: Optional[float] = statistics.median(fitted_latencies) if fitted_latencies else None

    if median_dt is None or median_dt <= 0:
        speed = 0.0
    else:
        # Faster than baseline → >1 before clamp; cap at 1 so ρ stays in [0,1].
        speed = min(1.0, POLICY_BASELINE / median_dt)

    rho = coverage * speed

    return {
        "rho_community": round(rho, 4),
        "coverage": round(coverage, 4),
        "speed": round(speed, 4),
        "median_dt_seconds": round(median_dt, 1) if median_dt is not None else None,
        "median_dt_hours": round(median_dt / 3600.0, 3) if median_dt is not None else None,
        "n_events": n_events,
        "n_fitted_responses": n_fitted,
        "n_within_latency_budget": n_within_budget,
        "latency_budget_seconds": LATENCY_BUDGET,
        "policy_baseline_seconds": POLICY_BASELINE,
        "include_dry_run": INCLUDE_DRYRUN,
        "is_null": n_fitted == 0,
    }


def _fmt_secs(s: Optional[float]) -> str:
    if s is None:
        return "n/a"
    if s >= 3600:
        return f"{s/3600:.2f}h ({s:.0f}s)"
    if s >= 60:
        return f"{s/60:.1f}min ({s:.0f}s)"
    return f"{s:.0f}s"


def print_human(r: Dict[str, Any]) -> None:
    print("=" * 60)
    print("Agent-1 ρ_community — response coefficient")
    print("=" * 60)
    print(f"  log file:                 {RHO_LOG}")
    print(f"  events (n):               {r['n_events']}"
          + ("" if r['include_dry_run'] else "   (dry_run excluded)"))
    print(f"  fitted responses (approved): {r['n_fitted_responses']}")
    print(f"  within latency budget:    {r['n_within_latency_budget']}")
    print("  ----------------------------------------------------------")
    print(f"  latency budget:           {_fmt_secs(r['latency_budget_seconds'])}  (Coverage gate)")
    print(f"  policy baseline:          {_fmt_secs(r['policy_baseline_seconds'])}  (Speed yardstick)")
    print(f"  median Δt(detected→approved): {_fmt_secs(r['median_dt_seconds'])}")
    print("  ----------------------------------------------------------")
    print(f"  Coverage  = {r['coverage']:.4f}   (within-budget approvals / events)")
    print(f"  Speed     = {r['speed']:.4f}   (baseline / median Δt, clamped [0,1])")
    print(f"  ρ_community = Coverage × Speed = {r['rho_community']:.4f}")
    print("=" * 60)
    if r["is_null"]:
        print("NULL RESULT: no human-approved advisories yet → ρ = 0.")
        print("Components are shown above and this null is publishable (per the paper).")
    if r["latency_budget_seconds"] == 86400 or r["policy_baseline_seconds"] == 86400:
        print("NOTE: latency budget and/or policy baseline are 24h PLACEHOLDERS.")
        print("      Set AQ_LATENCY_BUDGET and AQ_POLICY_BASELINE_LATENCY from the")
        print("      pre-registered field measurement before publishing ρ (see prereg.md).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute Agent-1 ρ_community")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    events = load_events()
    result = compute_rho(events)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
