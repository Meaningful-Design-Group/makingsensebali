# Agent-1 — pre-registration (OSF-style stub)

**Status:** stub for review (Tomas + Fab Lab Bali community). NOT yet locked.
**Instrument:** Agent-1 air-quality response agent, Making Sense Bali / PLANETAI
node (`bali.fab.city`). **Commit:** this pre-registration is locked *before* any
event is counted toward a published ρ. Per the PLANETAI core-ideas paper,
pre-registration is the instrument's peer review — changing the trigger,
budget, or baseline after counting starts voids the run and starts a new one.

References: `reports/ai_infra/PLANETAI_NODE_V0_SPEC.md` §3; PLANETAI core-ideas
paper §"Action agents". Code: `agent1_aq.py`, `rho.py`, `approve_agent1.py`.

---

## Hypothesis (H₀-A)

**H₀-A (null):** a node-local, human-gated air-quality response agent does **not**
reduce the detection→response latency for community PM2.5 exceedances relative to
the existing provincial air-quality response baseline (i.e. ρ_community ≈ 0, or
Speed ≤ baseline).

**Alternative:** Agent-1 produces human-approved community advisories for
pre-registered PM2.5 trigger events faster than the provincial baseline and for a
meaningful fraction of events (ρ_community > 0, materially).

We publish the result **either way** — an explicit commitment to publish a null
(see below). ρ is reported with components shown, never as a single opaque number.

---

## Exact trigger (frozen parameters)

A trigger event fires for a hub when **all** hold:

| Parameter | Value | Env | Note |
|---|---|---|---|
| Metric | PM2.5 | — | fine particulate, µg/m³ |
| Threshold | **35 µg/m³** | `AQ_PM25_THRESHOLD` | community-agreed; **not** the WHO value. WHO 2021 24h guideline is 15 µg/m³ and is carried only as advisory context. |
| Sustain window | **≥ 60 min** | `AQ_SUSTAIN_MIN` | the latest contiguous above-threshold run must span ≥ 60 min (measured by time span of the above-threshold tail, robust to irregular sampling). |
| Radius | **5 km** | `AQ_RADIUS_KM` | haversine from the hub anchor (ported from `peaks.js` `distanceKm`). |
| Sensors | community PM2.5 sensors in radius | — | Smart Citizen / OpenAQ via the local sovereign store, or proxy poll. Hub series = mean of in-radius sensors per 1-min bucket. |
| Hubs | per-hub, independent | `hubs.json` | each banjar/hub runs the trigger separately. |

**Source-of-truth for the series:** the local sovereign TimescaleDB store
(`AQ_AGENT_STORE_DSN`) when present (true sustained-window history). Without it,
the agent polls current values and builds an in-memory rolling window —
sustained history is then **approximate** and every such event is flagged
`window_approximate: true` in the log. **Published ρ must come from store-backed
events** (`window_approximate: false`); approximate events are excluded or
reported separately.

### Dedup / cooldown

One event per hub per **cooldown window** of **3 h** (`AQ_COOLDOWN_HOURS`). A new
exceedance within 3 h of a hub's last `detected_at` does **not** create a second
event. This prevents a single multi-hour episode from inflating the event count.

---

## Fitted-response definition

An event is a **fitted response** iff a human approves its drafted advisory, i.e.
`approved_at` is set and `approved_at ≥ detected_at`. Approval is performed by the
authorised approver (below) via the operator dashboard (prod) or
`approve_agent1.py` (skeleton). Drafting and queuing alone do **not** constitute a
response — only human approval does. This is the responsible-AI gate: **nothing is
ever auto-sent.**

---

## Approver authority

Approval authority rests with a **Fab Lab Bali operator** designated by the
community (the same role that approves citizen reports today). Only a designated
approver may set `approved_at`. The approver may edit advisory text before
approving. `delivered_at` is stamped after the advisory is actually sent on the
existing WhatsApp/Evolution channel. (To confirm with Tomas: named approver(s)
and whether community-council sign-off is required for the first N advisories.)

---

## Latency budget (Coverage gate)

`AQ_LATENCY_BUDGET` — the maximum detection→approval latency for an event to count
toward Coverage. **Placeholder: 86 400 s (24 h).** This is the pilot's
self-imposed SLA and must be set to the pre-registered community commitment before
counting. It is distinct from the policy baseline below.

---

## Policy-baseline latency (Speed yardstick) — definition + how measured

`AQ_POLICY_BASELINE_LATENCY` — the detection→public-response latency of the
**status quo** (existing provincial AQ response). **Placeholder: 86 400 s (24 h),
to be replaced by a real measurement.**

**How it will be measured (to pre-register before counting):** identify a set of
recent provincial/official air-quality responses (e.g. haze/burning advisories,
ISPU-based public notices) and measure the elapsed time from the air-quality
exceedance becoming detectable to the official public response/advisory. Take the
**median** over that reference set as the baseline. Document the source incidents,
the detectability definition, and the sample in this file before locking.
Sensitivity: report ρ at the chosen baseline ±1 plausible alternative.

---

## ρ formulas (as implemented in `rho.py`)

- **Coverage** = (# events with `0 ≤ approved_at − detected_at ≤ AQ_LATENCY_BUDGET`)
  ÷ (# events).
- **Speed** = `AQ_POLICY_BASELINE_LATENCY` ÷ median Δt(`detected_at`→`approved_at`)
  over fitted responses, **clamped to [0, 1]** (faster-than-baseline → toward 1;
  at/over baseline → < 1; a single very fast response cannot push ρ above its
  ceiling).
- **ρ_community = Coverage × Speed**, in **[0, 1]**, components always shown.
- **Null** (no fitted responses) → ρ = 0 with all components printed.

Event counting excludes `dry_run` events by default
(`AQ_RHO_INCLUDE_DRYRUN=0`).

---

## Commitment to publish a null

We commit to publishing the ρ result **and its components** whether or not it
supports the alternative — including a flat **ρ = 0 / null** — together with the
event log format (Apache 2.0) so other pilots' agents can be compared on the same
instrument. A null is a valid, publishable measurement of the gap between a
node-local agent and the policy baseline, not a failure to report.

---

## Open items for Tomas / community review

1. Confirm the **35 µg/m³** community threshold (vs WHO 15) with the banjar.
2. Confirm the **Serangan** hub anchor coordinate (currently APPROX in `hubs.json`).
3. Name the **approver(s)** and any council sign-off requirement.
4. **Measure** the policy baseline (replace the 24 h placeholder) and set the
   latency budget to the agreed SLA.
5. Lock this file (freeze parameters) before counting events toward published ρ.
