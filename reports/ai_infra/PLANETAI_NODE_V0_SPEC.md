# PLANETAI Node v0 — Bali reference spec (Serangan)

**What this is.** The Bali deployment we built (Making Sense Bali)
re-described in PLANETAI's own node / tier / agent language, so it stands as the
**reference Community-tier node** other pilots fork. It also scopes **Agent-1**
(the Bali air-quality response agent named in the core-ideas paper) against the
code we already have, and marks exists / to-build for the response coefficient ρ.

Reference: `PLANETAI_NODE_BLUEPRINT.md` (infra/ops detail), `CANONICAL_AI.md`
(AI serving), and the PLANETAI core-ideas paper (§"The node", §"Action agents").

> **Naming note.** This node is the technical substrate; the citizen-facing
> program is being renamed **Making Sense Bali** (method, tool-agnostic) with
> **Smart Citizen** retained as one sensor tool. The first hub instance is
> **Banjar Serangan**. Spec language below is name-neutral.

---

## 1. How our stack maps to the PLANETAI node

PLANETAI's Node v0 table (paper §"The node") vs. what's running in Bali today:

| Node v0 layer (paper) | Bali reference (built) | State |
|---|---|---|
| **Compute** — compact general-purpose, storage-rich, async-federated | Mac mini M4 (exo node + API), Synology NAS (services), MacBook M1 (burst cluster) | **live** |
| **Local intelligence** — quantised SLM over federated weights, MRL embeddings | **exo cluster running Gemma 4** (multimodal, OpenAI API at the mini's Tailscale IP); Gemini cloud fallback | **live** (MRL tier-slicing: not yet) |
| **Sensors** — campaign kit + environmental HAT + pilot add-ons | Smart Citizen Kits (house/office nodes) + DIY tiers; OpenAQ/Sensor.Community planned | **live** (campaign, not continuous fleet) |
| **Runtime** — Docker Compose: local UI, embedding layer, sensor broker, agent runtime | NAS docker: bot + vision worker + Evolution + Postgres/Redis + dashboard; exo on the mini | **live** (agent runtime: Agent-1 to build) |
| **Federation** — LAN-local + bioregion-server over opt-in overlay | Murmurations profiles (federated discovery) + Tailscale overlay; bioregion server (IT Del) | **partial** (Murmurations live; bioregion-server federation not wired) |
| **Sovereignty** — raw stays at node, only approved embeddings federate | **gap today** — sensor raw lives on the Barcelona Smart Citizen backend (see §4) | **to-fix** |
| **Enclosure** — fab-labable, OSHWA-track | n/a (using existing hardware) | n/a |

**The honest headline:** on compute + local multimodal intelligence + a working
**action channel** (the WhatsApp bot) + public surface + federation discovery, the
Bali node is *ahead* of the paper's "to-be-built" list. The two real gaps are
**(a) data sovereignty** (raw sensor data is on Barcelona's backend, §4) and
**(b) the agent runtime + ρ instrumentation** (§3). Everything else is a reframe,
not a build.

---

## 2. Tiers — one node, sliced (not five dashboards)

PLANETAI's Matryoshka principle: **one embedding space, sliced per tier** — you do
*not* build a separate product per scale. Today our public surface
(`mdg-bali.github.io/smartcitizenbali`) is effectively a Community/City view with
real data; PLANETAI's Serangan "hyperlocal dashboard" mockup is the same tier with
the trust-ring / FCI-strip IA but **mocked data**. These are the same node's face,
built twice. The node should emit one tier-sliced representation that renders:

- **Community (64-d)** — Banjar Serangan: live sensors, citizen reports, Agent-1
  advisories, fab-lab activity. This is where our stack already lives.
- **City (256-d)** — Denpasar/Badung reconstructed from **Bali Satu Data** (no
  Metroverse coverage; PITO/DIDO from provincial open data).
- **Region (512-d)** — Bali Province open data.
- **Bioregion (1024-d)** — IT Del-hosted server; community-council veto enforced here.
- **Planet (2048-d)** — the global observatory (`planetai.fab.city/observatory`).

**Implication for unification:** the live node becomes the *data + action engine*
behind the Serangan hyperlocal dashboard's IA — one surface, real data, PLANETAI
trust-ring/matryoshka front. We stop maintaining a mocked dashboard and a live map
in parallel. (Proposal detail in the chat thread / a separate IA note.)

---

## 3. Agent-1 — air-quality response, scoped against our code

**Paper spec (§Action agents):** *SmartCitizen sensors within 5 km of Fab Lab Bali
record PM2.5 above a community-agreed threshold for >60 min → agent pulls the
regional Aurora PM2.5 forecast → drafts a bilingual (ID/EN) advisory → surfaces an
OSHWA/OKH open-hardware air-filter shortlist fabricable on lab inventory → queues
for human approval at the Fab Lab Bali admin interface → every step timestamped.*
ρ_community sub-latency clock = **sensor-detection → approved advisory**.

### What already exists (reuse, don't rebuild)

| Capability needed | Where it is today |
|---|---|
| PM2.5 thresholds (WHO 5/15/35) + peak detection | `peaks.js` — `THRESHOLDS.pm25`, `detectPeaks()` (client-side; port to the agent) |
| Per-sensor PM2.5 + active-window logic | `data.js` — `classifyPM25()`, `isActive()` (14-day), `fetchAllSensors()` |
| Distance / locality math for the 5 km radius | `data.js` — `distanceKm()`, `BALI_LOCALITIES` (add a Fab Lab Bali anchor coord) |
| Bilingual drafting engine | **exo Gemma 4** (the node's own LLM) — drafts the ID/EN advisory locally |
| Human-in-the-loop approval pattern | the bot/operator dashboard already does draft→queue→approve for reports |
| Delivery channel to residents | the WhatsApp bot (Evolution API) — broadcast/advisory send |
| Event/record logging + federation | report JSON + Murmurations republish pattern (worker) |

### What's to build (the agent + the ρ clock)

1. **A node-side Agent-1 worker** (mirror the vision-worker pattern: a small Python
   service on the NAS/mini). Loop: pull sensor series → `detectPeaks(pm25)` within
   5 km of the Fab Lab Bali anchor, sustained ≥60 min → fire.
2. **Forecast pull** — regional PM2.5 forecast (paper says Aurora; v0 can start with
   the existing OpenAQ/Smart Citizen trend + a placeholder for the Aurora subscribe).
3. **Advisory drafting** — call exo Gemma with a fixed prompt → bilingual advisory.
4. **Filter shortlist** — a small curated **OSHWA/OKH air-filter catalog** (JSON in
   the repo) filtered by "fabricable on current lab inventory" tags. (No catalog
   exists yet — author it; start with 3–5 known open designs.)
5. **Approval queue** — reuse the operator-dashboard approve pattern; advisory is
   draft→queue→approve (never auto-sent: the paper's responsible-AI gate).
6. **ρ instrumentation (the point of the whole thing):** timestamp every step to a
   pre-registered log — `detected_at`, `forecast_at`, `drafted_at`, `approved_at`,
   `delivered_at`. Compute per the paper:
   - **Coverage** = fraction of pre-registered PM2.5 trigger events that produce a
     human-approved advisory within the latency budget.
   - **Speed** = median Δt(detected→approved) normalised against a pre-registered
     **policy-baseline latency** (the existing provincial AQ response time).
   - **ρ_community = Coverage × Speed**, reported with components shown, null
     publishable. Log format published (Apache 2.0) so other pilots' agents match.
7. **OSF pre-registration** of Agent-1's threshold, fitted-response definition,
   approver authority, latency budget — *before* counting events (the paper makes
   pre-registration the instrument's peer review).

### Effort read

Roughly **80% reuse, 20% new.** The new 20% is: the agent loop (port `peaks.js`
server-side + the 5 km/60-min gate), the OSHWA filter catalog (content, not code),
and — the actual deliverable — the **timestamp log + ρ computation**. The advisory
itself is "call the model we already run." This is a days-scale build, not a
platform build, and it produces the one thing the paper says nobody has: a real
ρ measurement against a policy baseline.

---

## 4. The sovereignty gap (the one that changes the architecture)

Today the Smart Citizen Kits report to the **Barcelona backend** (`api.smartcitizen.me`),
which the node reads from. That means **Bali's raw citizen-sensor data physically
lives in Barcelona** — directly counter to PLANETAI's Governance pillar (CARE,
"raw stays at the node, only approved embeddings federate", PKC sovereignty-by-
architecture at IT Del). Closing this is the highest-leverage move (it compounds
across the citizen project, Fab Island Bali autonomy, and PLANETAI's central claim).

**Deployed (2026-06-01).** A constraint shaped this: the NAS environment is
**allowlist-filtered** (HTTP 403 to `api.smartcitizen.me`, the worker proxy, Google,
and `ghcr.io` image pulls), while the **Mac mini has real egress** (it pulls models).
So the data has to enter via the mini. The sovereign store is therefore a **SQLite DB
on the mini** (`~/makingsense/store.db`), filled by a stdlib (urllib + sqlite3) ingest
that mirrors the Smart Citizen kits through the mini's egress — Bali now holds its own
authoritative copy; Barcelona is a source we mirror, not a backend we depend on.
SQLite is the right v0 at this volume; Postgres/Timescale on the NAS (`postgres:16-alpine`
is already local — no pull) is the later step if volume justifies. (Ingest note: the
Cloudflare worker 403s the default `Python-urllib` UA — set a custom User-Agent.)
Raw stays in Bali; only council-approved embeddings federate up. Prerequisite for
honest CARE governance.

**Gemini fallback rehomed.** Because the NAS worker is 403'd from Google, the cloud
fallback was non-functional from where it ran. Fixed by a tiny **stdlib proxy on the
mini** (`gemini_proxy.py`, `:8077`, launchd `com.fabcity.gemini-proxy`) that forwards
to Google over the mini's egress; the worker's `AQ_GEMINI_ENDPOINT` now points at
`http://100.112.110.7:8077/v1beta`. Bonus: the API key transits to the mini rather than
living on the NAS. Verified: worker → mini proxy reachable (HTTP 200); proxy → Google
pass-through confirmed.

---

## 5. Build order (smallest leverage-positive moves first)

1. **Reframe done** — this spec makes the live node the PLANETAI reference node.
2. **Agent-1 ρ skeleton — DONE (2026-06-01), on the mini.** stdlib agent reads the
   SQLite store, fires on the 5 km/60-min PM2.5 gate, drafts a bilingual advisory via
   local exo, queues for approval (never auto-sends), logs the ρ clock; `rho.py`
   computes Coverage × Speed. Verified end-to-end (real sensors → exo advisory →
   ρ-event). **To go from skeleton to live instrument:** run ingest + agent as launchd
   loops (so real PM2.5 history accumulates), and finalize `prereg.md` (real
   policy-baseline latency + named approver) before any ρ is *published*.
3. **Sovereign store — DONE (2026-06-01)** as SQLite-on-mini (see §4). Gemini fallback
   rehomed to the mini proxy.
4. **Unify surfaces** — the public surface target is **`bali.fab.city`** (§6), the
   multiscalar Fab City node face that embeds the PLANETAI principles, with Making
   Sense Bali as one experiment on it. (Mockup in progress.)
5. **Tier-slicing (MRL)** — emit the 64/256/512-d slices so City/Region render from
   the same node without separate builds.

> **Serangan parked (2026-06-01).** No sensor or PLANETAI node is deployed at Serangan
> yet. Plan: a couple of sensors first, then a Mac mini by end of year. Until then the
> live node is **Bukit / Fab Lab Bali**; Serangan stays a named future hub (coordinate
> still APPROX in `agent1/hubs.json`).

---

## 6. Naming & URL strategy (durable infrastructure vs project brand)

Four layers, kept distinct so the durable identity outlives the funded project:

| Layer | Name | Lives at | Lifespan |
|---|---|---|---|
| Infrastructure / institutional | **Fab City** (per-city node) | **`bali.fab.city`** (per-city subdomain pattern: `barcelona.fab.city`, `boston.fab.city`, …) | durable |
| Citizen campaign / program | **Making Sense Bali** (method; Smart Citizen is one tool) | hosted on the Bali node, surfaced under `bali.fab.city` | durable |
| Research instrument / funder brand | **PLANETAI** (Google-funded application) — global observatory, Planet-tier aggregation, the H₀-T/H₀-A instrument | `planetai.fab.city/observatory` | **transitional → folds into Fab City infrastructure** |
| Sensor tool | **Smart Citizen** (kit + platform) | a data source, not a brand | n/a |

**The rule:** per-city Fab City subdomains (`bali.fab.city`) are the long-term public
home of each node. **PLANETAI is a project brand, not the lasting one** — it is the
funded research instrument that federates the per-city nodes at the Planet tier, and
it should resolve into plain Fab City infrastructure over time, not a permanent
parallel brand. So the surface-unification target (§2, build-order item 4) is
**`bali.fab.city`**, not `planetai.fab.city/local-hubs/…` and not the
`mdg-bali.github.io/smartcitizenbali` GitHub-Pages slug. The slug rename is deferred
precisely because the real destination is the per-city Fab City subdomain, reached
during unification — there is no point renaming the github.io slug on the way.

For replication: each new pilot is `<city>.fab.city` (Fab City node) running its own
citizen campaign name (the local equivalent of "Making Sense Bali"), federating up to
the PLANETAI observatory at the Planet tier. One pattern, per-city addressable.

---

## 7. Scale model & sovereignty placement (decided 2026-06-01)

Resolving three architecture questions against the PLANETAI paper — without breaking
the canonical model:

**Five global tiers, kept intact.** The paper's scales are MRL dimensional slices
(Community 64 → City 256 → Region 512 → Bioregion 1024 → Planet 2048), and "one
taxonomy across all pilots" is a named novelty. We do **not** add a sixth global tier
(it would break the dimensional doubling and cross-pilot comparability). Sub-city
granularity is handled by *local instantiation*, not a new scale.

**Bali instantiation of the Community tier = Desa Adat.** The customary village is the
**governance anchor**: the CARE-veto holder, the Tri Hita Karana sign-off authority,
and Agent-1's hub catchment. (A *banjar* is the finer customary unit within a desa; if
hyperlocal views need it, render banjar↔desa as two zoom levels *within* Community, not
a new tier.) `agent1/hubs.json` should carry the desa adat name for the hub.

**PKC = the sovereignty substrate (the floor), not a tier.** Per the paper, PKC (Ben
Koo, operational at IT Del) is the individual-scale antecedent; "PLANETAI's smallest
*measurement* unit is the community." The *resident* is the PKC individual. PKC's
triadic pattern maps onto our stack:
- content-addressed immutable records → the sovereign SQLite store (today local but
  **not** yet hash-verified/append-only — PKC would make it so);
- mediation layer → MRL embeddings (**TODO**, the tier-slicing item);
- authorization gate → council-gated federation (today only `sender_hash` + consent —
  the **Desa Adat** CARE veto is the gate to build).
So the sub-city texture is the **individual (PKC) ↔ desa (Community)** relationship —
the citizen↔council relation — not a scale ring. In the public surface, PKC is the
foundation of the matryoshka + the "you own your record" through-line.

**Flower = the federated-learning roof, distinct from Murmurations.** Two federations,
don't conflate them:
- **Murmurations (live)** = federated *discovery* (org/node profiles, "who's out there").
- **Flower (planned)** = federated *learning* — model deltas flow up to the bioregion,
  **raw never leaves**; Flower + causal discovery across the four bioregions is the
  paper's federated-causal-inference novelty.
We have the sovereignty *floor* (raw stays local), not the learning *roof*. Flower = a
client on the mini + a server at IT Del's bioregion, over MRL embeddings. Depends on
(a) the bioregion server, (b) MRL slicing, (c) ≥1 peer — none stood up yet.

**Status: PKC and Flower are represented, not built.** Placed correctly in the
architecture + the `bali.fab.city` surface (live-vs-planned labelled); real builds are
sequenced after MRL + the IT Del bioregion server, and PKC is a relationship to
activate with Ben Koo, not just code.
