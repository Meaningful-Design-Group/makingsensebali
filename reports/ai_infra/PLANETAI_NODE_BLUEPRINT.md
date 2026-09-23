# PlanetAI Node Blueprint — Making Sense Bali (Fab City) reference deployment

**Purpose.** This documents the local infrastructure built for Making Sense Bali
(under Fab Lab Bali / Fab City) so it can be **replicated as a PlanetAI node** in
other bioregions. It is written as a blueprint, not a changelog: what the pieces
are, where they run, what depends on what, how to deploy, and what is site-specific
vs. portable.

**Status:** live and verified (2026-05-31). Citizen photo reports flow end-to-end
through local AI on the cluster, with a cloud fallback.

Companion files in this folder:
- `CANONICAL_AI.md` — the canonical local-AI serving design + the exo/vision details.
- `vision.env` — canonical environment for the reporter's vision worker.
- `exo-ensure.sh`, `com.fabcity.*.plist` — the mini-side auto-start/supervision.

---

## 1. What this node is

A community environmental-reporting system + a local AI serving layer, all
self-hosted on hardware in one location:

- Residents send a photo + location of a pollution issue over **WhatsApp**.
- A bot guides them (multilingual) and queues the report.
- A **local multimodal LLM (Gemma 4 on an exo cluster)** classifies the photo.
- Results publish anonymously to a **public map** (GitHub Pages) and a federated
  **Murmurations** profile.
- The same local AI endpoint backs a **chat UI (open-webui)** and other internal
  agents (telegram bot, morning digest).

The design goal that shapes everything: **local-first AI, addressed so the
hardware can move** (a laptop can leave; the always-on box keeps serving), with a
**cloud fallback** so citizen-facing service never hard-stops.

---

## 2. Hardware & network topology

| Role | Device | Notes |
|---|---|---|
| Always-on AI host | **Mac mini (Apple M4, 16 GB)** | Runs exo; hosts the canonical model endpoint. The box that must stay. |
| Burst/cluster compute | **MacBook Pro (M1 Pro, 16 GB)** | Second exo node over Thunderbolt → **32 GiB pooled**. **Removable** (see §6). |
| Services host | **Synology NAS** | Docker stack: the reporter pipeline + the agentic-os stack. Always-on. |

**Networking — the load-bearing rule:** everything addresses other machines by
**Tailscale IP**, never by LAN IP and never `localhost` across machines. The mini
is `100.112.110.7`. This survived a double-NAT fix (ISP router + mesh AP) that
changed the LAN — because nothing referenced the LAN address. **Replication rule:
put all nodes on a tailnet and address by tailnet IP/name.**

---

## 3. The AI serving layer (exo + Gemma 4)

- **Engine:** exo (EXO Labs desktop app, v1.0.71) running on the Mac mini, joined
  with the MacBook into one cluster over a Thunderbolt bridge. OpenAI-compatible
  API at `http://100.112.110.7:52415/v1`.
- **Model:** **Gemma 4** — multimodal, so a *single model does text and vision*.
  - `gemma-4-e4b-it-6bit` (~6.7 GB) is the canonical always-on model: it fits the
    **mini alone**, so it does not depend on the MacBook.
  - Larger `gemma-4-31b-it-4bit` (~17 GB) / `gemma-4-26b-a4b-it-8bit` (MoE) are
    on-demand models for the **32 GiB pool** when the MacBook is connected.
- **exo vision gotcha (documented in detail in `CANONICAL_AI.md`):** exo only feeds
  an image to the model if the *loaded instance's* model-card has a non-null vision
  config. A freshly placed Gemma-4 instance autodetects this from the model's
  `config.json`; an instance frozen *before* the config finished downloading
  silently drops images (HTTP 200, plausible text, wrong answer). **Detection:** an
  image should add ~256–280 prompt tokens; if the delta is ~0, reload the instance
  (`DELETE /instance/{id}` then `POST /place_instance`). Verified working: 25 → 281
  tokens, correct classification.
- **Fallback:** **Google Gemini** (`gemini-2.0-flash`, Generative Language API) is
  the cloud fallback when the local cluster is unreachable. exo demonstrated it can
  fall over under vision load on 16 GB, so the fallback is **mandatory, not
  optional**. Key lives in container env, never in git.

---

## 4. The reporting pipeline

```
resident WhatsApp photo + location
  → Evolution API (WhatsApp gateway, NAS docker: aq-evolution)
  → aq-bot (NAS docker): guides the flow, writes a report + queues a vision job
       reports → /app/reports (bind-mounted), images → /app/images,
       job → /app/vision_queue/AQ_*.json
  → aq-vision-worker (NAS docker sidecar): drains the queue
       → exo Gemma-4 vision over Tailscale  (fallback: Gemini)
       → writes ai_analysis into the report JSON
       → republishes the anonymized Murmurations profile → public map
  → public site (GitHub Pages: mdg-bali.github.io/smartcitizenbali)
```

**Bot conversation flow (current):** language pick (EN / ID / ES) → consent (in
chosen language) → issue type → **photo** → **location** (WhatsApp pin, Google
Maps link, or pasted `lat,lng`) → optional comment → confirm. Post-submit menu:
report another · learn more (site URL) · give feedback (anonymous, stored to
`reports/feedback.jsonl`).

**Privacy model (preserve on replication):** phone numbers are **never stored**;
senders are tracked only by a one-way `sender_hash`; reports publish anonymously;
consent is explicit (`consent.json`) with `/optout`.

---

## 5. Component inventory (what runs where)

**Synology NAS — `aq-reporter` docker project** (`/volume1/docker/aq-reporter`):
| Container | Role | AI dependency |
|---|---|---|
| `aq-bot` | WhatsApp bot / report flow | none direct (enqueues) |
| `aq-vision-worker` | queue drainer → vision | exo (mini, Tailscale) + Gemini |
| `aq-evolution` | WhatsApp gateway (Baileys) | — |
| `aq-postgres`, `aq-redis` | Evolution's stores | — |
| `aq-dashboard` | operator review UI | — |

**Synology NAS — `agentic-os` docker project** (`/volume2/docker_1/agentic-os`):
| Container | Role | AI dependency |
|---|---|---|
| `open-webui` | chat UI + RAG | exo (mini, Tailscale) |
| `telegram-bot`, `morning-digest` | internal agents | via open-webui |
| `whisper` | speech-to-text | — |
| `tika` | document extraction | — |
| `exo-nas` | exo coordinator | part of the cluster |

**Mac mini:** EXO.app (exo node + API endpoint), supervised by launchd
(`com.fabcity.exo-ensure` → `exo-ensure.sh`).

**MacBook Pro:** EXO.app (second exo node). Nothing else depends on it.

---

## 6. Portability — taking the MacBook away

**Question answered:** *can the MacBook Pro be unplugged and taken without
breaking the local infrastructure?* **Yes.**

What depends on the MacBook: **only exo's pooled compute/RAM** (models that need
>16 GB). Everything operational addresses the **mini's** Tailscale endpoint:
- the reporter worker → `100.112.110.7:52415`
- open-webui → `100.112.110.7:52415`
- telegram-bot / morning-digest → open-webui → mini

The mini hosts the API endpoint and has the e4b weights cached locally, so the
endpoint stays up when the MacBook leaves.

**What happens on disconnect:**
1. Big pooled models (31b/26b) become unavailable — expected; they need the pool.
2. The e4b instance (exo may schedule it on the MacBook) disappears. The
   **`exo-ensure` agent** (every 5 min) pings e4b, finds it not serving, clears the
   ghost, and re-places it — with only the mini present it lands on the **mini**,
   loading from the cached weights (~30–40 s).
3. During that gap, the reporter's **Gemini fallback** handles photos, so citizen
   reports never stop.

**Known limitation:** exo's `place_instance` API does not expose node pinning, so
e4b cannot be *proactively* pinned to the mini — it self-heals there on disconnect
rather than always living there. The graceful-degradation pattern (cached weights +
ensure agent + cloud fallback) is the portable answer, and is arguably the right
design for replication anyway.

**Before taking the MacBook for the first time:** confirm the mini has the model
weights cached (`ls ~/.exo/models` on the mini — should list the e4b model). Then
disconnect is safe.

---

## 7. Deployment mechanics (and constraints)

- **Docker on the NAS is fronted by a socket-proxy** that **blocks image pulls and
  `docker compose`/builds** (returns `403 Forbidden`). Consequence: you cannot
  `docker pull`/`compose`/build through the automation path — those must be done on
  the NAS directly (Synology Container Manager or host SSH). Container *create/run/
  exec/cp* and file writes are allowed.
- **Code deploys use a bind-mount overlay** (no rebuild): edited files are staged on
  the NAS and bind-mounted over the image's `/app`, then the container is recreated.
  Example — the bot:
  ```
  docker run -d --name aq-bot --restart unless-stopped --no-healthcheck \
    --network aq-reporter_default \
    -e AQ_VISION_BACKEND=mock -e AQ_EVOLUTION_KEY=… -e AQ_BOT_PORT=5055 \
    -v /volume1/docker/aq-reporter/data/<each>:/app/<each>  (images, reports, …) \
    -v <nas>/aq-bot-overlay/bot_murmurations.py:/app/bot_murmurations.py:ro \
    -v <nas>/aq-bot-overlay/messages.py:/app/messages.py:ro \
    -v <nas>/aq-bot-overlay/sessions.py:/app/sessions.py:ro \
    aq-reporter-aq-bot
  ```
  The vision worker is deployed the same way (`--volumes-from aq-bot` for the data,
  overlay for `m1_vision_worker.py` + `vision_analyzer.py`, env for exo + Gemini).
  **For permanence, bake the code into the image** (rebuild on the NAS) so it
  survives independent of the overlay.
- **Mini auto-start** is launchd LaunchAgents (`com.fabcity.exo-ensure`). exo itself
  relaunches at login; the agent re-places the model.
- **Directory permissions matter:** bind-mounted dirs the container writes to must be
  owned/writable by the container user (uid 1000 here). A root-owned `profile_photos`
  dir caused approval 500s until `chown`ed — watch for this on replication.

---

## 8. Replication guide — portable vs site-specific

**Portable (the pattern):** Tailscale addressing · exo + a multimodal Gemma model ·
the OpenAI-compatible contract · the queue→worker→vision→publish pipeline · the
overlay-deploy + launchd-supervision approach · primary-local + cloud-fallback
resilience · the privacy model (no phone numbers, hash + consent).

**Site-specific (the knobs to change per bioregion):**
| Knob | Where | Bali value |
|---|---|---|
| WhatsApp business number | bot config | (production number) |
| Languages | `messages.py` `MESSAGES` (EN/ID/ES) | English / Bahasa / Spanish |
| Issue categories | `messages.py` `CATEGORY_MENU_ITEMS` + `vision_analyzer.CATEGORIES` | burning, trash, water, … |
| Survey / "learn more" URL | bot + site | mdg-bali.github.io/smartcitizenbali |
| Public site | GitHub Pages repo | mdg-bali/smartcitizenbali |
| Murmurations node id / bioregion | `config.json` | bali.fab.city / indo_pacific_coral_triangle |
| Model choice | `vision.env` / exo | gemma-4-e4b (always-on), 31b (pool) |
| Tailnet IP of the always-on host | `vision.env`, open-webui env | 100.112.110.7 |

---

## 9. Operations runbook (quick reference)

- **Restart exo / recover the API:** on the mini — `killall EXO; sleep 4; open -a EXO`,
  then re-place the model (the `exo-ensure` agent does this automatically within 5 min).
- **Re-place the reporter model:** `POST /place_instance {"model_id":"…e4b…","min_nodes":1}`.
- **Load the big model (MacBook connected, RAM free):**
  `POST /place_instance {"model_id":"mlx-community/gemma-4-31b-it-4bit","min_nodes":2}`.
- **Recover failed/stuck vision jobs:** `mv vision_queue/failed/AQ_*.json vision_queue/`.
- **Verify vision actually ingests images:** send an image, check `prompt_tokens`
  jumps ~+280; if not, reload the instance.
- **open-webui image update** (proxy-blocked here): do on the NAS via Container Manager.
- **Approval 500s:** check the writable dirs are owned by the container user (uid 1000).

---

## 10. Open items / hardening for the next site

- Bake bot + worker code into the images (retire the overlay) for clean reproducibility.
- Proactive model pinning to the always-on node (exo API limitation today).
- RAG embeddings in open-webui (moved to local default after Ollama retired; existing
  Chroma vectors were nomic-embedded — consider re-indexing).
- `telegram-bot` / `morning-digest` request model name lives in an env_file — point at
  an exo model when those are next deployed.
- Confirm exo auto-restores the placed instance on a full mini reboot (agent covers it,
  but verify end-to-end once).
