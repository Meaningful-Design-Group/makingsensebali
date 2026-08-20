# Beyond PM2.5 — what to measure for waste burning, and when to raise an alert

*Making Sense Bali · 20 August 2026*

> **Status: working document, grounded in our own data.** Everything numeric
> below comes from the Making Sense Bali report archive (46 moderator-approved
> reports) and 44 days of 15-minute readings from Smart Citizen kit 19236.
> Where the evidence is thin — and in one important place it is very thin —
> that is stated rather than smoothed over.

---

## The short version

PM2.5 tells you *that* something burned. It does not tell you *what*, and in
Bali that distinction is the whole argument.

We set out to test the obvious next step — use the particle-size ratios we
already collect to separate combustion smoke from road dust — against a
confirmed burning event 150 m from one of our own sensors. **It does not
work.** On low-cost optical sensors the size channels are derived from an
assumed distribution, not measured. During a fourfold-plus PM2.5 excursion,
every ratio stayed inside its normal range.

What did work: an anomaly-plus-rate-of-rise detector on PM2.5 alone flagged
that event **47 minutes before the first human reported it**.

So the honest recommendation is not a shopping list. It is:

1. Stop discarding the channels we already measure. Twelve AirGradient nodes
   in Bali — including one 54 m from our most-reported burning site — publish
   CO2, VOC index and NOx index every few minutes. Our pipeline kept PM2.5,
   PM10, temperature and humidity, and threw the rest away.
2. Archive at native resolution. Hourly averaging nearly erased the one event
   we can verify.
3. The only genuinely missing channel in the entire network is **CO**. Add it
   to three nodes at chronic sites, not to sixteen everywhere.
4. Fix the coverage mismatch before buying anything. It is the binding
   constraint, not sensor chemistry.

---

## 1. What the reports say

46 approved reports. Classifying as burning on category **or** the reporter's
own words gives **35 burning events**; 37 if the AI image description is also
counted. `category` alone gives 30.

**The category field misses 14% of them** (19% on the wider definition).
Five approved reports describing burning in the reporter's own text are filed
as something else:

| File | Stored category | What the reporter wrote |
|---|---|---|
| `AQ_20260709_002636_239` | `vehicle` | "Trash burning" |
| `AQ_20260713_145129_608` | `none` | "Construction site burning trash" |
| `AQ_20260808_031931_758` | `none` | "Rubbish burning in side of river…" |
| `AQ_20260808_032048_677` | `none` | "Local house burning rubbish at the front of the house…" |
| `AQ_20260812_052717_068` | `construction` | "Construction site burning trash regularly." |

Two more (`AQ_20260520_094139_034` "Illegal landfill", `AQ_20260515_093532_702`
"Lots of trash next to the roads") are flagged as burning only by the AI image
description, not by the reporter — those are the 35→37 difference and are
excluded from the figures below.

This matters beyond tidiness: `areas.json` and any alert logic keyed on
`category` inherit a ~14% false-negative rate on the burning class. Until the
classifier improves, **derive the burning flag from category OR description
text**, which is what the analysis here does.

### Where the events are

Against the twelve AirGradient nodes (fixed third-party locations, stable
history), n = 35:

| Distance to nearest sensor | Events | Share |
|---|---|---|
| ≤ 500 m | 17 / 35 | 49% |
| ≤ 1 km | 24 / 35 | 69% |
| ≤ 2 km | 27 / 35 | 77% |
| ≤ 5 km | 31 / 35 | 89% |
| max | | 7.2 km |

Nearest-node tally: **Kuwum, Bali** 29, Padang2 Uluwatu 5, Nyambu 1.

Counting our own four Smart Citizen kits as well — restored to the feed today
(section 6) — coverage improves to 57% / 77% / 91% / 100%, max 4.9 km. Treat
that as the *current* picture, not the historical one: the kits move, and we
have no record of where they were on any given past date.

The concentration is extreme. **Ten reports share one exact coordinate
(−8.661515, 115.161636), 54 m from the AirGradient node at Kuwum** — a
chronic, repeatedly-reported site with a full-spec sensor effectively on top
of it. Three more coordinates carry two reports each, two of them within 400 m
of the same node.

That is the single most valuable fact in this document. We do not need a
network to characterise waste burning. We need one instrumented site, run
properly, for a season.

### Two data-quality problems in the report timestamps

**Timing cannot currently be trusted.** Most events carry
`incident_time_basis: "now"` — the incident time is just the submission time.
So the hour-of-day distribution below is a picture of *when people report*,
not when things burn:

```
incident by block  : night 1 · morning 7 · midday 12 · afternoon 6 · evening 11
```

It is bimodal — midday and evening — but that is a reporting pattern. Any
claim that burning peaks in the evening is not supported by this dataset.
(An earlier working assumption of an evening peak was wrong and is retracted
here.)

**Four of the eight user-supplied incident times are in the future** relative
to submission, by +0.73 h to +5.32 h:

```
AQ_20260603_091053  submitted 17:12  incident 17:56  +0.73 h
AQ_20260604_091729  submitted 17:19  incident 19:31  +2.20 h
AQ_20260604_092557  submitted 17:27  incident 22:46  +5.32 h
AQ_20260708_093642  submitted 17:37  incident 20:10  +2.54 h
```

Either the bot's time parser is mishandling WITA, or reporters are entering a
recurring schedule ("they burn at 19:30 every night") rather than an
observation. Both are plausible; neither is currently distinguishable.
**Fix: reject or re-prompt on any incident time later than submission**, and
add an explicit "this happens regularly at…" field if that is what people
mean.

---

## 2. What the sensors say

Backtest source: **Smart Citizen kit 19236** (Sensirion SEN5X, outdoor,
Kuta Selatan −8.81983, 115.16657), 6 July – 19 August 2026, **4,306 fifteen-
minute points**.

### Baseline structure

```
PM2.5 µg/m³   min 2.3 · p25 6.5 · median 9.1 · p75 13.4 · p95 22.7 · max 63.6
MAD 3.25      stdev 6.64
```

Use MAD, not standard deviation — standard deviation is inflated by exactly
the excursions you are trying to detect.

Hour-of-day medians (WITA) show a clear double traffic signature: morning
peak 12.4 at 07:00, afternoon trough 7.4 at 14:00, evening peak 12.2 at
18:00. **A flat threshold cannot see through this. Baseline per hour of day.**

Note this site is comparatively clean — median 9.1 µg/m³. Kerobokan, where
most reports come from, is not comparable and must be baselined separately.

### Why absolute thresholds fail

| Rule | Fires | Rate |
|---|---|---|
| hourly PM2.5 > 15 (WHO 24h guideline) | 200 of 1080 h | **4.55 / day** |
| hourly PM2.5 > 55 | 2 | 0.05 / day |
| hourly PM2.5 > 150 | 0 | 0 |

An alert that fires four times a day is wallpaper. One that never fires is
decoration. Neither is a detector.

### The one event we can verify

**25 July 2026, report 150 m from the kit, 09:17 WITA.**

```
 time    PM2.5   z(MAD)   Δ60min
 07:30    10.1   -0.48     +1.8
 07:45    13.4   +0.25     +4.8
 08:00    16.2   +0.92     +7.9
 08:15    21.9   +2.16    +12.9
 08:30    32.7   +4.54    +22.6      <-- z crosses 4
 08:45    42.5   +6.70    +29.1      <-- peak
 09:00    32.0   +6.03    +15.8
 09:15    35.9   +7.10    +14.0      <-- report submitted
 09:30    38.1   +7.71     +5.4
 10:15    22.8   +3.38    -13.0
 10:45    18.5   +2.24    -15.1
```

Onset ~07:30, peak 42.5 µg/m³ at 08:45 — four to five times the pre-onset
level of 8–10 — then decay over ~2 h. The sensor peaked **about half an hour
before the report was submitted**, and crossed a 4-MAD anomaly threshold
**47 minutes before it**. That lead time is the entire operational case for
the sensor network.

The second report within 3 km (27 July, 1.56 km away) produced z = +0.84 —
nothing. At 1.5 km a neighbourhood fire is already lost in the noise.

> **The honest limitation: n = 1.** Two approved burning reports fall within
> 3 km of the only online kit in the 44-day window. One is clearly detected,
> one is not. That is the entire co-located evidence base. No detection rate,
> no false-positive rate, and no threshold in this document is statistically
> established. Section 5 is how that changes.

### The negative result that matters

The plan was to gate alerts on particle-size composition — combustion aerosol
is sub-micron, mechanical dust is coarse, so PM1/PM2.5 high and PM2.5/PM10
high should mean "something burned". Measured against the confirmed event:

| Ratio | 44-day baseline | At the event peak | Moved? |
|---|---|---|---|
| PM2.5 / PM10 | median 0.99 (p10 0.96) | **0.983** | no |
| PM1 / PM2.5 | median 0.94 (p10 0.92, p90 0.95) | **0.941** | no |
| PN0.5 / PN10 | median 0.8566 (p05 0.8391, p95 0.8600) | **0.8553** | no |
| TPS (typical particle size)\* | median 44.4 (p95 51.1) | 48.07 | within normal |

\* TPS is published as µm, but values of 39–58 are implausible for ambient
aerosol — almost certainly a unit or scaling error in the platform's channel
mapping. Used here only as a relative signal, and it did not move either.

PM2.5/PM10 spans 0.96–1.00 across 1,080 hours. PN0.5/PN10 spans ±1.2%. These
are not measurements, they are constants.

**Why:** low-cost optical sensors — Sensirion SEN5x, Plantower PMS5003,
Seeed HM-3301 alike — size particles poorly and derive the coarse fractions
from an assumed distribution. An independent
[2024 evaluation of Plantower particle-number output](https://pubs.rsc.org/en/content/articlelanding/2024/ea/d3ea00181d)
found agreement with reference instruments spanning more than an order of
magnitude, and recommended restricting use to PM mass in the smaller bins.
Our data agrees, in the strongest way: during a real fourfold-plus excursion, the ratios
did not move.

**Consequence: there is no composition gate available at this price point.**
Magnitude and dynamics are all we have from particles. Chemistry has to come
from a different sensor.

### Resolution matters more than expected

At the steepest hour the event rose **+18.1 µg/m³/h**. A "rise > +20/h" rule
evaluated on hourly rollups would have **missed it**. On 15-minute data the
same event rises +10.8 in a single step and is unmistakable.

**Archive at native resolution. Hourly averaging destroys the signal you are
trying to detect.**

### Candidate rules, measured

Evaluated on 4,306 15-minute points, consecutive fires collapsed into
distinct events with a 3-hour debounce:

| Rule | Alert events / 44 d | Events / day | Catches 25 Jul? |
|---|---|---|---|
| z > 3 MAD | 29 | 0.64 | yes |
| z > 4 MAD | 24 | 0.53 | yes |
| **z > 5 MAD** | **16** | **0.36** | **yes** |
| z > 6 MAD | 15 | 0.33 | yes |
| rise > +5 / 15 min | 48 | 1.07 | yes |
| rise > +8 / 15 min | 23 | 0.51 | yes |
| rise > +10 / 15 min | 17 | 0.38 | yes |
| rise > +15 / 15 min | 10 | 0.22 | **no** |
| rise > +20 / 60 min | 14 | 0.31 | yes |
| rise > +25 / 60 min | 13 | 0.29 | yes |
| z>4 AND rise > +10/60 min | 21 | 0.47 | yes |
| **z>4 AND rise > +15/60 min** | **16** | **0.36** | **yes** |

Everything except the +15/15 min rule catches the event, so with n = 1 this
cannot rank the survivors. What it *does* establish:

- The workable operating region is **0.3–0.5 alert events per day per node** —
  roughly one every two to three days. That is a rate humans will actually
  respond to.
- A single-sample rise threshold set too tight (+15 in 15 min) misses a real
  fourfold event. Prefer the 60-minute window, or a lower 15-minute threshold.
- **Starting point: `z > 4 MAD AND rise > +15 µg/m³ / 60 min`** — 0.36
  events/day, catches the known event, and requires both magnitude and
  dynamics so a slow regional haze build-up does not trip it.

Of the ~16 alerts this produces per 44 days, exactly one has a matching
report. The rest are unexplained — some are certainly real unreported
burning, some are not, and **we currently have no way to tell them apart.**
That is what Tier 1 in section 4 is for.

---

## 3. What the hardware already measures — and we throw away

This is the finding that changes the shopping list.

**AirGradient (12 public nodes in the Bali bbox, keyless API).** Each returns,
every few minutes:

```
pm01  pm02  pm10  pm003Count  atmp  rhum  rco2  tvoc  tvocIndex  noxIndex
```

Live example from **Kuwum, Bali — the node 50 m from our most-reported site**:

```
pm01 8.5 · pm02 20.8 · pm10 22.0 · pm003Count 729
atmp 29.9 · rhum 52 · rco2 404 · tvoc 37.5 · tvocIndex 36 · noxIndex 1
```

Our pipeline kept `pm25`, `pm10`, temperature and humidity. **`rco2`,
`tvocIndex`, `noxIndex`, `pm01` and `pm003Count` were discarded on every
single poll** — the CO2 channel needed for combustion
efficiency, and the VOC/NOx indices that respond to plastic and to
nitrogen-rich waste respectively.

**Smart Citizen kits (ours).** SEN5X exposes PM1 / PM2.5 / PM4 / PM10,
particle-number bins PN0.5 / PN1 / PN2.5 / PN4 / PN10, and TPS. All but two
discarded. (Per section 2 the size channels turn out to be inert — but that is
a conclusion we could only reach by looking, and we could not look, because
nothing was stored.)

**Kit 19651, "Bali DIY Node — Office"**, carries a Plantower PMS5003 *and* a
Seeed HM-3301 *and* a BME680 side by side — a direct head-to-head for the
DIY node BOM decision. It has been offline since 15 June. Getting it back
outdoors settles the PMS5003-vs-HM3301 question with our own data instead of
datasheets.

**What nothing in the network measures: CO.** Not one node, of any type.

---

## 4. What to add, in order

### Tier 0 — free, do first

Store everything already arriving, at native resolution. Implemented today
(section 6). Zero cost, and it is the precondition for every other decision
here.

### Tier 1 — the one channel worth buying: CO

CO is the strongest cheap discriminator for open waste burning, for two
reasons. Dust makes none of it, so it separates combustion from every
mechanical PM source absolutely. And smouldering makes enormous amounts of
it: the [ACP 2023 characterisation of open household-waste burning](https://acp.copernicus.org/articles/23/8921/2023/)
measured CO emission factors **4–9× higher for smouldering than flaming**, and
found vegetation at 50% moisture produced **20–30× the PM** and 3× the CO of
dry or naturally-moist material — which makes rainy-season yard-waste burning
the worst case, not the mild one. The same study puts plastic bags at
MCE > 0.94 (flaming) and plastic bottles at MCE ≈ 0.6 (smouldering only), with
0.9 as the flaming/smouldering divide.

| Option | Approx. cost | Notes |
|---|---|---|
| Winsen ZE07 / ZE12-CO | $20–30 | adequate for multi-ppm plume enhancements; not sub-ppm |
| **SPEC DGS-CO 968-034** | **$60–90** | 0–1000 ppm, 0.1 ppm resolution, T90 < 30 s, 12 mW continuous, digital output, 5–10 yr life |
| Alphasense CO-B4 + ISB | $120–180 | reference-class; needs an analogue front end; not worth it here |

**Tropical caveat, and it is not the one people expect.** The
[AMT 2023 year-long field evaluation](https://amt.copernicus.org/articles/16/3313/2023/)
found the Alphasense CO-B4 held R² = 0.70 against reference at 10–20 °C but
collapsed to **0.05 above 30 °C**, and drifted 53% in a year. High humidity
was *fine* — R² 0.70 at RH > 75% versus 0.20 at RH < 30%. **Heat is the
killer, not damp.** Bali ambient at 24–32 °C sits on the edge; a dark
enclosure in sun passes 50 °C easily.

Non-negotiable if we deploy CO: white double-walled ventilated radiation
shield, never sun-exposed, annual replacement budgeted, and CO treated as a
*relative event indicator* rather than a calibrated concentration.

### Tier 2 — CO2, for MCE, only where a node is close to the source

Modified Combustion Efficiency, `MCE = ΔCO2 / (ΔCO2 + ΔCO)`, is the cleanest
single number available at this price point: above 0.9 is flaming, below is
smouldering. Traffic sits near 0.98; plastic bottles smouldering came in near
0.6 in the ACP work. A
[multi-sensor smouldering/flaming classifier](https://pmc.ncbi.nlm.nih.gov/articles/PMC5017393/)
reached 97.5% on the smouldering class using only smoke, CO2 and temperature.

The AirGradient nodes **already report `rco2`**. For the Kuwum hotspot we
need no new CO2 hardware at all — only CO, and the archive we just started.
Where we do add it: SCD41 (~$20, −10 to +60 °C) over SenseAir S8 (~$20,
0–50 °C), on temperature range alone. Absolute accuracy of ±40 ppm is
irrelevant because MCE uses a difference over a short window and the offset
cancels.

Hard limit: at 200 m the CO2 enhancement drops below the noise. **MCE is a
near-node diagnostic.** Two or three nodes at known chronic sites — not a
fleet-wide feature.

### Tier 3 — wind, one or two units for the whole network

Direction converts "something burned somewhere" into a source sector, and two
nodes plus a time offset give crude triangulation. $40–150. Siting properly
in a kampung is close to impossible, so treat it as sector-indicative, never
quantitative.

### Tier 4 — what cannot be bought

Dioxins, furans, PAHs, HCl. These are what make waste burning categorically
worse than biomass, and they are lab-only, roughly $500–1500 per sample with
a sampling train. Do not chase them with sensors.

The right use of the network here is inverted: it tells a university lab
exactly which three sites and which three hours to sample. That makes an
expensive campaign an order of magnitude more efficient, and it is a far
stronger basis for a research partnership than a funding request.

### The budget tension, named

The "under $50 open-source node" and CO do not fit in one box — the DGS-CO
alone breaks the budget. Split the tiers rather than compromise:

- **Density node**, target < $50: PM + T/RH + VOC. Coverage.
- **Diagnostic node**, ~$120–150: adds CO (+ CO2 where not already present).
  Three of these at chronic sites.

Density where it is cheap, chemistry where it matters. That is also a better
story than one node doing everything badly.

---

## 5. Alert design

### Principles the data forces

1. **Event detector, not threshold detector.** Absolute WHO thresholds fire
   4.55×/day at a *clean* site.
2. **Baseline per node, per hour of day**, rolling 14–28 days, median + MAD.
3. **Require magnitude and dynamics together.** Slow regional haze must not
   trip a local-burning alert.
4. **Persistence**, so a passing truck or a mosquito coil beside the node does
   not count.
5. **No composition gate.** It does not exist on this hardware. Do not write
   one and assume it works — we did, and it does not.
6. **Same anti-pinpointing discipline as the map.** "Burning detected 80 m NE
   of node 12 at 19:42" is a pointing finger. Alerts go out at desa or banjar
   level with a time window. Never a bearing, never a distance.

### Proposed tiers

| Tier | Trigger | Action |
|---|---|---|
| **0 — log** | any anomaly failing the combined rule | database only; nobody is told |
| **1 — verify** | `z > 4 MAD AND rise > +15 µg/m³ / 60 min`, sustained ≥ 30 min, one node | bot asks opted-in residents within ~1 km: "unusual smoke near [desa] — can you see or smell burning?" |
| **2 — advise** | two nodes within ~2 km inside 20 min, **or** one node + one human report within 30 min | area-level advisory: elevated smoke, [desa], [time window] |
| **3 — health** | rolling 1 h PM2.5 > 150 µg/m³ sustained | mask / close windows advisory regardless of source — at that level cause is irrelevant to the person breathing it |

**Tier 1 is the important one and it is not primarily an alert.** It is the
mechanism that converts sensor uncertainty into community verification, and
it is the only way to build the labelled dataset that would let us state a
detection rate instead of describing one event. Every yes/no answer is a
label. With ~16 Tier-1 candidates per node per 44 days, a handful of nodes
generates a usable training set in one season.

On the 25 July event, a Tier 1 ping would have gone out at 08:30 — **47
minutes before the first person reported it.**

### What we cannot yet claim

- No detection rate. One confirmed co-located event.
- No false-positive rate. ~15 of 16 alerts per 44 days are unexplained.
- No burning-time-of-day distribution. Most reports timestamp the
  submission, not the incident.
- Nothing about Kerobokan's baseline. The backtest site is Ungasan and it is
  much cleaner.

Every one of these is answerable with the archive that started today plus one
season of Tier-1 verification. None is answerable by buying sensors.

---

## 6. Changes made on 20 August 2026

**`generate_loop.sh` had been wedged for 20 days 16 hours.** A `git push`
blocked on a socket with no timeout, and the loop had no way back — every
downstream step behind it silently stopped. Fixed: each cycle now runs under
`timeout` (600 s default), and git gets `http.lowSpeedLimit 1000` /
`http.lowSpeedTime 60` so a stalled transfer aborts instead of hanging.

**`MSB_HTTP_TIMEOUT` defaulted to 20 s; `api.smartcitizen.me` now answers in
21–32 s from the NAS.** Every Smart Citizen call was timing out, so our own
kits vanished from `sensors.json` and `history.json` went empty — presenting
as dead hardware when the kits were online the whole time. Raised to 60 s.

**Added `archive.py`** — append-only NDJSON, one file per day, 5-minute
cadence, deduplicated on `(source, id, timestamp)`, gzipped after 3 days.
Captures every channel both networks expose, including the ones the site does
not render. Roughly 1 MB/day. It runs as a separate detached loop so a slow
archive cycle cannot hold up site generation, or vice versa.

Why 5 minutes and not 15: AirGradient publishes every 2–5 minutes and a
burning plume is a 10–30 minute event. The site cadence is too coarse to
catch one.

---

## 7. What to do next, in order

1. **Let the archive run for four weeks.** Then re-run this backtest against
   Kuwum, which is the nearest node for 29 of 35 events — including ten at
   one coordinate 54 m away. That is the study this document is a placeholder for.
2. **Fix the burning classifier**, or derive the flag from description text.
   19% false negatives currently propagate into `areas.json` and any
   category-keyed alert.
3. **Reject incident times later than submission**; add a "this happens
   regularly at…" field for what people appear to be trying to say.
4. **Get kit 19651 back outdoors** and settle PMS5003 vs HM-3301 with our own
   side-by-side data.
5. **Then, and only then, buy CO** — three DGS-CO in proper radiation
   shields, at Kuwum and two other chronic sites.
6. Baseline Kerobokan separately. Do not carry Ungasan's numbers across.

The sensors are not the constraint. Coverage, storage and labels are.

---

## Sources

- [Characterization of gas and particle emissions from open burning of household solid waste from South Africa — ACP 23, 8921 (2023)](https://acp.copernicus.org/articles/23/8921/2023/)
- [Chemically speciated air pollutant emissions from open burning of household solid waste — ACP 23, 15375 (2023)](https://acp.copernicus.org/articles/23/15375/2023/)
- [Field evaluation of low-cost electrochemical air quality gas sensors under extreme temperature and relative humidity conditions — AMT 16, 3313 (2023)](https://amt.copernicus.org/articles/16/3313/2023/)
- [Real-time identification of smouldering and flaming combustion phases using a wireless multi-sensor network and ANN](https://pmc.ncbi.nlm.nih.gov/articles/PMC5017393/)
- [Evaluation of low-cost electrochemical sensors for O3, NO2 and CO](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6541011/)
- [Evaluation of Plantower particle-number output — Environmental Science: Atmospheres (2024)](https://pubs.rsc.org/en/content/articlelanding/2024/ea/d3ea00181d)
- [DGS-CO 968-034 datasheet specifications](https://www.isweek.com/product/digital-carbon-monoxide-co-gas-sensor-module-dgs-co-968-034_2390.html)
- [Low-cost CO2 sensors compared: photo-acoustic vs NDIR — AirGradient](https://www.airgradient.com/blog/co2-sensors-photo-acoustic-vs-ndir-updated/)
- [AirGradient public API reference](https://api.airgradient.com/public/docs/api/v1/)

*Data: Making Sense Bali. Analysis scripts live on the NAS at
`/volume1/docker/aq-reporter/` (`archive.py`) and were run against the live
report store and the Smart Citizen public API.*
