# Agent-1 — air-quality response agent (skeleton)

Node-side response agent for **Making Sense Bali / PLANETAI node**
(`bali.fab.city`). It watches community PM2.5 around one or more hub anchors and,
on a sustained exceedance, **drafts a bilingual (Bahasa Indonesia + English)
advisory**, attaches a short list of fabricable open-hardware air filters, and
**queues it for human approval**. It **never auto-sends**. Every step is
timestamped to a pre-registered log so `rho.py` can compute the response
coefficient **ρ_community** against a policy baseline.

Scope + rationale: `reports/ai_infra/PLANETAI_NODE_V0_SPEC.md` §3 and the PLANETAI
core-ideas paper §"Action agents". Pre-registration: [`prereg.md`](./prereg.md).

> This is a **skeleton**. It does not deploy anything. The forecast pull is a stub
> (Aurora TODO). The operator dashboard does the approval in production; the
> `approve_agent1.py` CLI here stands in for it so the loop is testable.

---

## Files

| File | What it is |
|---|---|
| `agent1_aq.py` | the agent: trigger loop, advisory draft (exo), queue + ρ-log writer |
| `rho.py` | reads `rho_log.jsonl`, computes Coverage / Speed / ρ (components always shown) |
| `approve_agent1.py` | operator CLI: list / approve / mark-delivered (dashboard stand-in) |
| `hubs.json` | hub anchors (multi-banjar). Seeded with Bukit/Fab Lab Bali + Serangan |
| `air_filters.json` | OSHWA/OKH open-hardware filter shortlist (+ one open sensor companion) |
| `prereg.md` | OSF-style pre-registration stub (hypothesis, trigger, ρ, null commitment) |
| `queue/AQ1_<hub>_<ts>.json` | one advisory package per fired event (`status: pending_approval`) |
| `rho_log.jsonl` | one ρ-event per line: detected/forecast/drafted/approved/delivered timestamps |

---

## The flow: draft → queue → approve → deliver

```
PM2.5 sustained > threshold in radius (per hub)
        │
        ▼  agent1_aq.py
   detected_at ─► pull_forecast() (stub) ─► draft advisory via exo (ID/EN)
        │                                         │
        │                                   pick 2-3 fabricable filters
        ▼                                         ▼
   append rho_log line                  write queue/AQ1_<hub>_<ts>.json
   (approved_at: null)                  (status: pending_approval)
        │
        ▼  HUMAN GATE — operator dashboard (prod) / approve_agent1.py (here)
   approve  ─► stamps approved_at (queue + rho_log)   ← this is the responsible-AI gate
        │
        ▼  delivery on the EXISTING WhatsApp/Evolution channel (NOT this agent)
   mark-delivered ─► stamps delivered_at
        │
        ▼  rho.py
   Coverage × Speed = ρ_community  (components shown; null publishable)
```

**Responsible-AI gate:** the agent only ever *drafts and queues*. A designated
Fab Lab Bali operator must approve before anything is sent. In production the
operator dashboard performs the approve/deliver actions (the same pattern it
already uses for citizen reports); `approve_agent1.py` is the CLI stand-in for the
skeleton. **Delivery uses the existing WhatsApp/Evolution channel** — Agent-1 does
not send messages itself.

---

## Run it

### Dry-run (offline, no model, no network)

```bash
python3 agent1_aq.py --dry-run --no-exo
```

Runs **one** cycle. With no live exceedance it synthesizes a trigger (clearly
marked `dry_run: true`) so the full draft→queue→ρ-log path is exercised, writes a
`rho_log.jsonl` line and a `queue/AQ1_*.json` file, and exits. No exo call, no
sensor fetch required.

### Real loop

```bash
# point at the sovereign store for true sustained-window history (recommended)
export AQ_AGENT_STORE_DSN="postgresql://user:pass@nas:5432/sovereign"
python3 agent1_aq.py
```

Without `AQ_AGENT_STORE_DSN` the agent polls the Smart Citizen proxy each cycle
and builds an **in-memory rolling window** — sustained history is then only as
long as the agent has been up and is **approximate** (logged loudly; events
flagged `window_approximate: true`). Use the store for any run whose ρ you intend
to publish.

### Approve / deliver (skeleton CLI)

```bash
python3 approve_agent1.py list                 # show pending
python3 approve_agent1.py list --all           # include approved/delivered
python3 approve_agent1.py approve <event_id>   # stamps approved_at (queue + rho_log)
python3 approve_agent1.py mark-delivered <event_id>  # AFTER the channel sent it
```

### Compute ρ

```bash
python3 rho.py            # human-readable, components + ρ
python3 rho.py --json     # machine-readable
```

With no approvals you get **ρ = 0 / null with components shown** — that is the
correct, publishable result, not an error.

---

## Environment variables

### `agent1_aq.py`

| Var | Default | Meaning |
|---|---|---|
| `AQ_OPENAI_ENDPOINT` | `http://100.112.110.7:52415/v1` | exo OpenAI-compatible base (Gemma 4) |
| `AQ_OPENAI_MODEL` | `mlx-community/gemma-4-e4b-it-6bit` | model id |
| `AQ_OPENAI_KEY` | _(empty)_ | exo needs none; set if hosted |
| `AQ_AGENT_STORE_DSN` | _(empty)_ | TimescaleDB DSN; if set, read series from the sovereign store |
| `AQ_SCK_PROXY` | `https://scb-bali.tomas-74b.workers.dev/sck` | Smart Citizen worker-proxy |
| `AQ_PM25_THRESHOLD` | `35` | community-agreed µg/m³ (WHO 24h is 15) |
| `AQ_SUSTAIN_MIN` | `60` | sustained minutes above threshold to fire |
| `AQ_RADIUS_KM` | `5` | hub radius (haversine) |
| `AQ_POLL_INTERVAL` | `600` | loop seconds |
| `AQ_COOLDOWN_HOURS` | `3` | no refire per hub within this window |
| `AQ_REQUEST_TIMEOUT` | `90` | exo / proxy HTTP timeout seconds |
| `AQ_AGENT_DIR` | _(this dir)_ | where `hubs.json` / `queue/` / logs live |
| `AQ_LOG_LEVEL` | `INFO` | `INFO` / `DEBUG` |

### `rho.py`

| Var | Default | Meaning |
|---|---|---|
| `AQ_LATENCY_BUDGET` | `86400` (24h **placeholder**) | Coverage gate: max detected→approved latency to count |
| `AQ_POLICY_BASELINE_LATENCY` | `86400` (24h **placeholder**) | Speed yardstick: provincial baseline latency |
| `AQ_RHO_INCLUDE_DRYRUN` | `0` | `1` to include `dry_run` events |

> Both latency defaults are **24 h placeholders**. Set them from the
> pre-registered field measurement (see `prereg.md`) before publishing any ρ.

---

## ρ in one paragraph

`Coverage` = fraction of trigger events that got a human approval within the
latency budget. `Speed` = policy baseline ÷ median detection→approval latency,
clamped to `[0,1]` (faster than the status quo → closer to 1). `ρ_community =
Coverage × Speed`, in `[0,1]`, **always reported with its components**, and a null
(no approvals) is a valid published result. The log format is intended to be
shared (Apache 2.0) so other pilots' agents are measured on the same instrument.

---

## What's stubbed / to-do

- **Forecast:** `pull_forecast()` returns `{"available": false}` — Aurora subscribe TODO.
- **Store:** reads `readings(device_id, ts, metric, value, lat, lng, source)` from
  `reports/sovereign_store/` (authored in parallel). Degrades to proxy polling if
  the DSN is unset or `psycopg2` is missing.
- **Serangan hub coordinate** is **APPROX** in `hubs.json` — confirm before prod.
- **Delivery** is intentionally **not** implemented here: prod sends via the
  existing WhatsApp/Evolution channel after approval.
- **Pre-registration** must be locked (`prereg.md`) before counting events toward
  a published ρ.
