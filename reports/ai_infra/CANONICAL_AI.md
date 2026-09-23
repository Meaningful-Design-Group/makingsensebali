# Canonical Local AI — Home Infrastructure

**Owner:** Tomas · **Scope:** all local AI across the home stack (Mac mini + MacBook Pro + Synology NAS)
**Updated:** 2026-05-31 · **Status:** live — AQ reporter vision running on exo, verified end-to-end

Single source of truth for where local AI runs, what serves what, and how
consumers address it. Supersedes the earlier Ollama-based draft (Ollama is not
used — Gemma 4 on exo does text *and* vision in one model).

---

## 1. The decision, in one line

**exo runs Gemma 4 on the Mac mini and serves a single multimodal model for
both text and vision. Google Gemini is the cloud fallback. Everything is
addressed by Tailscale, never by LAN IP.**

This came out of fixing the AQ image-analysis tool, which was down. The
investigation found three serving layers (MLX, Ollama, exo) with no shared
contract — now collapsed to one (exo, OpenAI-compatible) plus a cloud fallback.

---

## 2. Topology (measured, not assumed)

| Role | Engine | Address | Notes |
|---|---|---|---|
| **Text + Vision** | exo (EXO.app 1.0.71) on the Mac mini | `http://100.112.110.7:52415/v1` (Tailscale, OpenAI-compatible) | Gemma 4 is multimodal — one model, both jobs. |
| **Cloud fallback** | Google Gemini (`gemini-2.0-flash`) | Generative Language API + key | Used only when exo is unreachable. Key in env, never in git. |

**Cluster:** Mac mini (Apple M4, 16 GB) + MacBook Pro (M1 Pro, 16 GB) =
**32 GiB pooled over Thunderbolt** via exo. But the MacBook is a laptop — when
it's closed or away, the cluster is just the 16 GB mini. So:

- **Always-on reporter model:** `gemma-4-e4b-it-6bit` (~7 GB) — fits the **mini
  alone**, so citizen-report vision works 24/7 without the laptop.
- **Most-capable, on-demand:** a `gemma-4-31b` / `26b-a4b` across the 32 GiB pool
  for interactive/heavy work, only when the MacBook is connected and RAM is freed.

**Addressing rule:** consumers use the mini's **Tailscale IP `100.112.110.7`**,
never a LAN IP and never localhost. This survived a double-NAT fix (ISP router +
Deco → Deco as AP) on 2026-05-31 that changed the LAN — Tailscale didn't care.
That's the whole point: address by Tailscale and home-network reshuffles never
break the stack.

---

## 3. The exo vision gotcha (read this before debugging "no vision")

exo 1.0.71 **does** do vision — but only when the *loaded instance's* model-card
has a non-null vision config. A Gemma-4 instance autodetects it from the model's
`config.json`. The failure mode that bit us: an instance created **before** its
`config.json` finished downloading froze a card with `vision: null`, after which
it **silently dropped every image** (HTTP 200, plausible text, no error).

**How to tell:** send an image and compare `prompt_tokens` with vs without it.
A real Gemma image adds ~256–280 tokens. If the delta is ~0, the image is being
dropped — the card is stale.

**The fix:** reload the instance so the card rebuilds.
```bash
# on the mini (or via the exo API over Tailscale)
curl -X DELETE http://localhost:52415/instance/{instance_id}
curl -X POST http://localhost:52415/place_instance \
  -H 'Content-Type: application/json' \
  -d '{"model_id":"mlx-community/gemma-4-e4b-it-6bit","min_nodes":1}'
```
Verified working: after reload, an image jumped `prompt_tokens` 25 → 281 and the
model named the test colour. Real citizen photos classify correctly
(`construction` 0.90, `trash` 0.90 with detailed indicators).

**Stability caveat:** exo's API has fallen over under vision load on the 16 GB
mini. If `:52415` stops responding (even on the mini's own localhost) while the
EXO.app GUI process is still alive, the API child died — restart it:
```bash
killall EXO; sleep 4; open -a EXO    # in the mini's logged-in GUI session
# then re-place the instance (above)
```
This is exactly why the Gemini fallback is **mandatory, not optional**.

---

## 4. The AQ reporter pipeline (live)

```
citizen WhatsApp photo
  → aq-bot (NAS, docker)  writes job to data/vision_queue/ + image to data/images/
  → aq-vision-worker (NAS, docker sidecar)  drains the queue
       → exo Gemma-4 vision over Tailscale   (fallback: Gemini)
       → writes ai_analysis into data/reports/<id>.json
       → republishes the Murmurations profile → public dashboard
```

**The worker** is a sidecar container off the same image as aq-bot:
```bash
docker run -d --name aq-vision-worker --restart unless-stopped \
  --network aq-reporter_default \          # reaches Tailscale, like aq-bot
  --volumes-from aq-bot \                   # shares the queue/images/reports
  -v /volume2/docker_1/agentic-os/aq-vision-worker/m1_vision_worker.py:/app/m1_vision_worker.py:ro \
  -v /volume2/docker_1/agentic-os/aq-vision-worker/vision_analyzer.py:/app/vision_analyzer.py:ro \
  -e AQ_VISION_BACKEND=openai \
  -e AQ_VISION_FALLBACK=gemini \
  -e AQ_GEMINI_KEY=<google-key>  \          # container env only — NOT in git
  -e AQ_OPENAI_ENDPOINT=http://100.112.110.7:52415/v1 \
  -e AQ_OPENAI_MODEL=mlx-community/gemma-4-e4b-it-6bit \
  -e AQ_REPO=/app -e AQ_POLL_INTERVAL=5 -e AQ_VISION_TIMEOUT=90 \
  aq-reporter-aq-bot python3 /app/m1_vision_worker.py
```
Worker code lives on the NAS at `/volume2/docker_1/agentic-os/aq-vision-worker/`
(host path) and is bind-mounted in. `AQ_REPO=/app` because `--volumes-from` puts
the queue/images/reports at the same `/app/...` paths the bot uses.

**Robustness:** the worker backs off before requeueing a failed job
(`sleep min(60, 10×retries)`) so a downed backend can't burn a real report
through all retries in milliseconds. Inference is ~40 s/photo on the mini —
fine for async citizen reports.

**Recover stuck/failed jobs:**
```bash
docker exec aq-bot sh -lc 'mv /app/vision_queue/failed/AQ_*.json /app/vision_queue/'
```

---

## 5. Code (in this repo)

- `reports/vision_analyzer.py` — backends: **openai (exo, default)**, **gemini
  (fallback)**, mlx, ollama, haiku, mock. Primary→fallback chain; never raises.
  Gemma 4 is a reasoning model → `max_tokens=768` so the JSON isn't starved.
- `reports/m1_vision_worker.py` — queue drainer (now with retry backoff).
- `reports/ai_infra/vision.env` — canonical env (exo primary, gemini fallback).
  The Gemini key is referenced but **not stored** here.

---

## 6. Consumer rewiring map

| Consumer | Was | Canonical target |
|---|---|---|
| AQ vision worker | MLX `localhost:8000` (dead) | exo `100.112.110.7:52415` + Gemini fallback ✅ live |
| open-webui (NAS) | `192.168.68.112:11434` (dead LAN IP) | exo `100.112.110.7:52415` (Tailscale) — **still to do** |
| telegram-bot (NAS) | (unverified) | exo `100.112.110.7:52415` — **still to do** |
| morning-digest (NAS) | (unverified) | exo `100.112.110.7:52415` — **still to do** |

The non-reporter consumers still point at the dead LAN-IP Ollama. Repoint them
to the exo Tailscale endpoint in a follow-up (grep their compose/env for
`11434`, `192.168.`, `OLLAMA`, `OPENAI`).

---

## 7. Open / follow-ups

- **Auto-start exo + restore the instance on boot.** EXO.app should relaunch at
  login; confirm the e4b instance is re-placed automatically (or add a small
  launchd/login hook). Until then a mini reboot needs a manual re-place.
- **`aq-bot` shows "unhealthy"** — false alarm: its healthcheck calls `wget`,
  which isn't in the container. Fix the healthcheck (use python/curl) or remove it.
- **Repoint open-webui / telegram-bot / morning-digest** to the exo Tailscale
  endpoint (section 6).
- **Big-model tier:** pick the most capable Gemma 4 that fits 32 GiB across the
  pool for interactive use, downloaded once the ISP speed is sorted.
