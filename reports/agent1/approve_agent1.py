#!/usr/bin/env python3
"""
approve_agent1.py — operator CLI for Agent-1's draft→queue→approve→deliver flow.

This is the SKELETON stand-in for the operator dashboard. In production the
Fab Lab Bali admin dashboard performs these same actions (it already does
draft→queue→approve for citizen reports); this CLI exists so the loop is
testable without the dashboard and so the responsible-AI gate (human approval
before any send) is always present.

It does three things, all idempotent-ish and never auto-sending:
  list                       show pending (and optionally all) queue items
  approve <event_id>         set the queue item status to 'approved' and stamp
                             approved_at (UTC ISO) into BOTH the queue file and
                             the matching rho_log.jsonl line
  mark-delivered <event_id>  stamp delivered_at into the queue file and the
                             matching rho_log line (call this AFTER the existing
                             WhatsApp/Evolution channel has actually sent it)

Approval is what feeds Coverage/Speed in rho.py — nothing counts as a fitted
response until a human approves it here (or in the dashboard).

Env
---
    AQ_AGENT_DIR   dir holding queue/ and rho_log.jsonl (default: this file's dir)

Usage
-----
    python3 approve_agent1.py list
    python3 approve_agent1.py list --all
    python3 approve_agent1.py approve <event_id>
    python3 approve_agent1.py mark-delivered <event_id>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

AGENT_DIR = Path(os.environ.get("AQ_AGENT_DIR", str(Path(__file__).resolve().parent)))
QUEUE_DIR = AGENT_DIR / "queue"
RHO_LOG = AGENT_DIR / "rho_log.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_queue_items() -> List[Tuple[Path, Dict[str, Any]]]:
    items: List[Tuple[Path, Dict[str, Any]]] = []
    if not QUEUE_DIR.exists():
        return items
    for p in sorted(QUEUE_DIR.glob("AQ1_*.json")):
        try:
            items.append((p, json.loads(p.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError) as e:
            print(f"  ! could not read {p.name}: {e}", file=sys.stderr)
    return items


def _find_by_event(event_id: str) -> Optional[Tuple[Path, Dict[str, Any]]]:
    for p, pkg in _load_queue_items():
        if pkg.get("event_id") == event_id:
            return p, pkg
    return None


def _stamp_rho_log(event_id: str, field: str, value: str) -> bool:
    """Set `field` = value on the rho_log line whose event_id matches.
    Rewrites the file. Returns True if a line was updated."""
    if not RHO_LOG.exists():
        print(f"  ! rho_log not found at {RHO_LOG}", file=sys.stderr)
        return False
    lines = RHO_LOG.read_text(encoding="utf-8").splitlines()
    updated = False
    out: List[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        try:
            ev = json.loads(s)
        except json.JSONDecodeError:
            out.append(line)  # preserve unparseable lines verbatim
            continue
        if ev.get("event_id") == event_id:
            ev[field] = value
            updated = True
            out.append(json.dumps(ev, ensure_ascii=False))
        else:
            out.append(json.dumps(ev, ensure_ascii=False))
    if updated:
        RHO_LOG.write_text("\n".join(out) + "\n", encoding="utf-8")
    return updated


# --- Commands --------------------------------------------------------------

def cmd_list(show_all: bool) -> int:
    items = _load_queue_items()
    if not items:
        print("No queue items.")
        return 0
    shown = 0
    for p, pkg in items:
        status = pkg.get("status", "?")
        if not show_all and status != "pending_approval":
            continue
        shown += 1
        flag = " [DRY-RUN]" if pkg.get("dry_run") else ""
        print(f"- {pkg.get('event_id','?')}  {pkg.get('hub','?')}  "
              f"PM2.5={pkg.get('pm25','?')} µg/m³  status={status}{flag}")
        print(f"    detected_at: {pkg.get('detected_at','?')}")
        if pkg.get("approved_at"):
            print(f"    approved_at: {pkg['approved_at']}")
        if pkg.get("delivered_at"):
            print(f"    delivered_at: {pkg['delivered_at']}")
        filt = ", ".join(f.get("name", "?") for f in pkg.get("filters", []))
        if filt:
            print(f"    filters: {filt}")
        print(f"    file: {p.name}")
    if shown == 0:
        print("No pending items (use --all to see approved/delivered).")
    return 0


def cmd_approve(event_id: str) -> int:
    found = _find_by_event(event_id)
    if not found:
        print(f"No queue item with event_id {event_id}", file=sys.stderr)
        return 1
    p, pkg = found
    if pkg.get("status") == "approved" or pkg.get("approved_at"):
        print(f"{event_id} already approved at {pkg.get('approved_at')}")
        return 0
    ts = _now_iso()
    pkg["status"] = "approved"
    pkg["approved_at"] = ts
    try:
        p.write_text(json.dumps(pkg, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        print(f"  ! could not write queue file {p.name}: {e}", file=sys.stderr)
        return 1
    stamped = _stamp_rho_log(event_id, "approved_at", ts)
    print(f"Approved {event_id} at {ts}")
    print(f"  queue: {p.name} → status=approved")
    print(f"  rho_log: {'stamped approved_at' if stamped else 'NO matching line found (check rho_log)'}")
    print("  NOTE: this does NOT send anything. Deliver via the WhatsApp/Evolution")
    print("        channel, then run: approve_agent1.py mark-delivered " + event_id)
    return 0 if stamped else 2


def cmd_mark_delivered(event_id: str) -> int:
    found = _find_by_event(event_id)
    if not found:
        print(f"No queue item with event_id {event_id}", file=sys.stderr)
        return 1
    p, pkg = found
    if not pkg.get("approved_at"):
        print(f"  ! {event_id} is not approved yet — approve it first.", file=sys.stderr)
        return 1
    if pkg.get("delivered_at"):
        print(f"{event_id} already marked delivered at {pkg['delivered_at']}")
        return 0
    ts = _now_iso()
    pkg["delivered_at"] = ts
    pkg["status"] = "delivered"
    try:
        p.write_text(json.dumps(pkg, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        print(f"  ! could not write queue file {p.name}: {e}", file=sys.stderr)
        return 1
    stamped = _stamp_rho_log(event_id, "delivered_at", ts)
    print(f"Marked delivered {event_id} at {ts}")
    print(f"  rho_log: {'stamped delivered_at' if stamped else 'NO matching line found'}")
    return 0 if stamped else 2


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent-1 operator approval CLI (skeleton)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list pending queue items")
    p_list.add_argument("--all", action="store_true", help="include approved/delivered")

    p_app = sub.add_parser("approve", help="approve an event and stamp approved_at")
    p_app.add_argument("event_id")

    p_del = sub.add_parser("mark-delivered", help="stamp delivered_at after sending")
    p_del.add_argument("event_id")

    args = parser.parse_args()
    if args.cmd == "list":
        sys.exit(cmd_list(args.all))
    elif args.cmd == "approve":
        sys.exit(cmd_approve(args.event_id))
    elif args.cmd == "mark-delivered":
        sys.exit(cmd_mark_delivered(args.event_id))


if __name__ == "__main__":
    main()
