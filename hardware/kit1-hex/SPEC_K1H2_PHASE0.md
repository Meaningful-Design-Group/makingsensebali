# PHASE 0 — Ground Truth + 4-Fundamental Spec
## Air Quality Node, Additive-Native Enclosure (Fab City Hex Facet System, Bali Outdoor)

Version: K1H2-P0-SIGNED · 2026-07-24 · status: **Phase 0 signed off (Tomas, same day) — Phase 1 authorized**

**Sign-off decisions (Tomas, 2026-07-24):**
- **D-1 Clean sheet.** Do NOT evolve v0.8. New design; hex rules stay as the guiding geometric principle. **"As simple as possible, and the shortest use of material and time to print"** — economy is now the top-ranked form driver (target: beat v0.8's 132 g / 4h35 clearly).
- **D-2 Mount = printed keyholes + zip-tie channels.** The 4× M4 countersunk bosses are deleted; no countersunk hardware mounts.
- **D-3 USB-C recess reinstated.** USB-C + power switch reachable without opening the enclosure, via a recessed down-and-out pocket with drip lip (a pocket needs no hex-legal square wall). If it provably breaks the 45° gate, return with evidence.
Relationship: candidate v2 baseline for `kit1-hex` ("basalt hood", K1H-1.0 / print-plan v0.8, gated 2026-07-24 AM).
Sources: Seeed wiki ×4 (fetched today) + `ref_seeed/` design files (KiCad PCB parsed, STEP measured, datasheet read) + diy-node ICD 1.12 (HM3301 Eagle parse + Tomas physical confirmations) + kit1/kit1-hex specs.

---

## 1. Ground truth — verified numbers (design files, not marketing pages)

### 1.1 Grove Shield for XIAO (SKU 103020312) — KiCad v1.2 PCB parsed (`ref_seeed/grove_shield_kicad/`)
Board coords: origin = board corner nearest Grove row start, X along 58 edge, Y along 25 edge.

| Item | Number |
|---|---|
| Outline | **58.000 × 25.000 × 1.6 mm** exactly (Edge.Cuts bbox) |
| Mounting holes | **NONE. Zero drilled mounting holes on the board** (83 drilled pads total = connectors/switch/TPs only, all ≤Ø1.0 plated) |
| XIAO socket (U1) | 2×7 female rows @2.54; pin field X 39.65–54.89, rows at Y 4.83 and 20.07; **XIAO sits at the right end, USB-C flush with the right 25 mm edge** |
| Power switch (SW1) | 9 × 3.5 × 3.5 slide, center 4.4 mm in from right edge, mid-height — **same right edge as USB-C** ✓ |
| Grove ports ×8 | two rows of 4 along both 58 mm edges, plug mouths facing out; X centers 6.2 / 14.2 / 24.0 / 32.0 |
| Battery | J9 2-pin solder pads near right-top corner (SMD, underside) |
| Pass-through headers | J10–J13, 2×7 @2.54 flanking the XIAO socket |

**→ Brief correction #1: "4× M2/M2.5 holes → printed posts" is impossible — the v1.2 board has no holes.**
Retention = perimeter **rails 25.0 + 0.30/side + end stops + top nib fingers** (kit1-proven, zero hardware, gate-compatible).
`TBC-02`: 30-second visual check of Tomas's physical shield (older revision could differ — v1.2 is current).

### 1.2 XIAO ESP32S3 + Wio-SX1262 stack — STEP measured (`ref_seeed/wio_sx1262_for_xiao.step`) + datasheet V1.1
| Item | Number |
|---|---|
| XIAO ESP32S3 | 21 × 17.8, USB-C on short edge (protrudes ~1.3), **WiFi/BLE antenna is EXTERNAL via U.FL "bottom left of the front (top) face" — there is NO onboard chip antenna** |
| Wio-SX1262 carrier | **17.78 × 21.44 × 1.6**; RF module + shield can **+2.95** over carrier top (can lid 10.1 × 11.3); B2B connector −3.4 under; stacks on TOP of the XIAO |
| LoRa U.FL (IPEX) | on carrier **top** face: Ø3.0 barrel, center **12.4 from board left edge (of 17.78), 2.0 in from short edge** — top corner of the stack |
| Stack height | measured reconstruction over shield top face: headers 8.5 + male base 2.5 + XIAO 1.2 + B2B 3.5 + carrier 1.6 + can 2.95 ≈ **19.5–20.0 mm**; USB-C axis ≈ 13.8 over shield top. **Keep the 25 mm reserve → CONFIRMED with ~5 mm margin (closes kit1/K1H OPEN item)** |
| LoRa RF/thermal | 22 dBm max @862–930 MHz; TX 125 mA @3.3 V ≈ **0.41 W bursts** (duty-cycled), RX 7.6 mA, sleep 1.62 µA; −40…+85 °C |

**→ Brief correction #2: the node carries a SECOND antenna inside the enclosure.** The kit's WiFi antenna
(rod/FPC, `TBC-03` exact type+dims from the box) needs a printed landing: flat facet zone ≥ 45 × 12,
**≥15 mm from any foil liner/conductive part**, not crossing the PM path, ≥20 mm from the SMA whip axis
(decouple the two radios). "Unfilled PETG near the antenna" applies to this landing zone, not to a chip antenna.

### 1.3 HM3301 PM2.5 — RESOLVED (Eagle parse 2026-06-11 + Tomas physical confirmation; wiki adds nothing)
| Item | Number |
|---|---|
| Board | 80.00 × 40.00 × 1.6, origin board-center |
| Metal can | 40 × 38 × 15 (18 total incl. board), footprint X −25.39…+14.61, Y −18.79…+19.21 → 14.6 clear board at Grove end / 25.4 at electronics end |
| Grove J2 | right-angle, exits the −X short edge |
| Mounting | **NO mounting holes** (only 2× Ø2.4 can-screw pass-throughs at (−23.62,−17.02) / (+12.57,+17.14)) → rails + edge capture |
| Air ports | **intake = 40 × 15 slot on one can SIDE Y-face; exhaust = fan grille on can TOP — perpendicular faces** (physically confirmed; supersedes the brief's "inlet and outlet on edges") |
| `TBC-01` | which Y-side carries the intake slot → ducting stays mirror-capable; board flips on rails either way |

### 1.4 Grove BME680 (101020513)
40 × 20 × 1.6 twin module, Grove connector at one short end, ≈7 mm max height incl. connector. Sensing element near the non-connector end → aim the louvred aperture at the full module face.

### 1.5 Antenna + honest bought parts
SMA whip **Ø13 × 195 mm**, 2 dBi, mounts OUTSIDE (Seeed's own case does the same); SMA-to-IPEX pigtail 10–15 cm; bulkhead barrel Ø6.35 + nut → **bore Ø6.65 teardropped** (Ø6.35 + 0.3 horizontal-hole rule), boss wall 4.0 local, flat for the nut, nut outside.
Bought, declared: SMA bulkhead pigtail · insect-mesh scrap (aperture ≤1.2) · desiccant sachet. Nothing else. USB power cable enters via the printed split grommet (kit1 part, re-used) only if mains-powered permanently; otherwise battery pads/JST inside.

### 1.6 Printer truth + fits (diy-node ICD §5.1, INFERRED ±0.1, Tomas-waived coupons — section prints gate)
Prusa CORE One HF0.4 · PETG · "0.15mm SPEED @COREONE HF0.4" · bed 250 × 220 · slicer 2.9.5/2.9.6 CLI, ASCII gcode, `;TYPE:Support` grep == **0** with `support_material ON` as the hardest gate.
Sliding 0.25/side · free 0.40/side · press 0.15/side · rails 0.30 · snap `COUPON_TBD_SNAP` 0.45 · vertical hole +0.2 Ø · horizontal hole +0.3 Ø + teardrop · design overhang limit 45° from horizontal · min self-supporting edge 0.8 · elephant-foot chamfer 0.4 × 45° all bed edges · walls 2.5 (4 perimeters water-facing) · gyroid infill 15–25 % where closed volume exists.

---

## 2. The four fundamentals (binding, with numbers)

### F1 — Sensor airflow
- Passive chimney in the climate zone: ambient in LOW past the BME680, out HIGH near the stack; **high exhaust open area ≥ low intake effective open area** (v11 lesson — never throttle the top).
- BME680 behind **downward louvres ≤45°, slot gaps ≥2 mm, total open ≥300 mm²**, cross-vented (apertures on two adjacent facets), **air gap 6 mm** panel-to-module.
- Stack vent: dedicated high gill pair (down-facing, ≥120 mm² total) above the XIAO/SX1262 for the 0.41 W TX bursts.
- Bali is low-wind: no sealed pockets anywhere air must move; every duct self-drains (slope ≥3° out).

### F2 — Self-heat / radiation
- BME680 **≥60 mm from the stack** (brief minimum is 10; we hold kit1-hex's 60 — passive error in still air demands it), never above it (heat rises), never downstream of PM exhaust.
- **Reflective foil liner + 2–3 mm air gap** behind the BME aperture (PETG is IR-transparent); foil **≥15 mm from the WiFi-antenna landing AND ≥15 mm from the LoRa U.FL/pigtail**.
- Matte **white** PETG body (T/RH truth in sun); firmware T-offset stays available as trim.

### F3 — Water + humidity (breathe, don't seal)
- Every downward-facing facet **≥45° from horizontal**; **no flat top anywhere**; apertures face down-and-out only, under ≥8–10 mm eave/skirt overlap.
- Drip break at the skirt: sharp bottom lip + **1.2–2 mm groove**. Labyrinth seam: tongue 1.6, +0.25/side, engagement 4, **groove opening DOWN**. Z-seams in designed arris gutters, off weather faces.
- **Weep Ø2.5 at every true low point** (each zone + each plenum). **Desiccant clip pocket 30 × 20 × 12** in the electronics zone. Insect mesh (≤1.2) in rebates with printed snap retainers — replaceable, no tools. Pressure-equalized: the box breathes by design, never airtight.

### F4 — Particulate path
- HM3301 owns a **dedicated, separated duct system**; PM air never mixes with climate-zone air (sealed plenum walls between zones).
- Intake plenum docks the full **40 × 15 slot face** with **≥5 mm standoff** off the can face (brief hard number; v0.8's 3.95 must grow), mirror-capable for `TBC-01`, → mesh rebate → down-louvred hex-cell grille, openings ≥2 mm.
- Exhaust: printed hood over the **can-top fan grille** → separate down-and-out grille; **≥40 mm exterior path + ≥1 facet arris between intake and exhaust mouths** (no recirculation), and the exhaust mouth sits on a wall group the BME680 apertures don't share.
- RH correction of PM happens in the dashboard, not firmware (standing rule).

---

## 3. Form + system rules carried into Phase 1
One irregular hex lattice generates everything: plan edges on {0°, 60°, 120°} axes, body facets, vent cells, closure lugs, mount features — consistent margins, **no mirror symmetry in any axis**. Chamfer system C0.5 functional / C1 standard / C2 corner (no radius system). Envelope ≤170 × 120 × 100 on a 220 × 220 bed; internal clear volume ≥ ~120 × 70 × 35. Closure: print-in-place (bayonet or 3–4-arc segmented snap; flex features FLAT in XY, L/h ≈ 10:1, tip 0.5×, root fillet ≥0.5× t). Mount: **printed keyhole slots + zip-tie channels on the rear facet** (per this brief — replaces v0.8's 4× M4 countersunk, see conflict C-1). Cables: 2× Grove 20 cm + pigtail in printed clips, never crossing PM air. CMF: matte white + one FC-hue accent part (PM intake retainer), fuzzy-skin body option, no text.

---

## 4. Brief ↔ reality ↔ v0.8 conflicts — DECIDE AT SIGN-OFF

| # | Conflict | Recommendation |
|---|---|---|
| C-1 | Brief mandates keyhole + zip-tie mount, bans countersunk bosses; **v0.8 built 4× M4 countersunk this morning** | Follow the brief: keyholes + zip-tie channels (zero-hardware-consistent). M4 deleted. |
| C-2 | Brief demands USB-C + switch reachable **without disassembly** via weather-protected recess; v0.8 dropped the wall port at checkpoint ("no hex-legal wall is square to the connector") | Phase-1 must solve it: a down-and-out service recess at the stack's right edge (USB axis ≈13.8 over shield top) with drip lip; hex-legality via a recessed pocket, not a through-wall square port. |
| C-3 | Brief says shield has 4 mount holes / SX1262 has chip antenna — **both false per design files** | Spec §1.1–1.2 corrections stand; rails + WiFi-antenna landing. |
| C-4 | Brief: PM apertures ≥5 mm off sensor faces; v0.8 intake gap 3.95 | Grow plenum standoff to 5.0. |
| C-5 | Brief allows ≤3 printed parts without asking; v0.8 = hood + base + 2 mesh retainers (+ reused grommet) | Ask: count retainers (0.4–0.9 g accents) as accessories → 2 main parts + accessories, or fold retainers into snapped mesh pockets. |
| C-6 | v0.8 SMA turret peaks at z≈102 vs envelope ≤100 tall | Trim turret 2 mm or accept 102 (envelope says ≤100; bed is not the constraint). Ask. |

## 5. Open / TBC table
| ID | Item | Blocking? |
|---|---|---|
| TBC-01 | Which can Y-face carries the HM3301 intake slot | No — mirror-capable ducting |
| TBC-02 | Photo-check Tomas's physical shield revision = v1.2 (no holes) | No — rails work regardless |
| TBC-03 | WiFi antenna in kit box: type + dims (rod vs FPC) | No — landing zone sized 45 × 12 generic |
| COUPON_TBD_SNAP 0.45 · rail 0.30 · grommet | Section prints before batch (kit1-hex coupon list stands) | Gates print, not CAD |

---

## 6. Phase 1 — base form "low boulder" (2026-07-24 PM, STOPPED at checkpoint)

Model `tools/k1h2_model.py` → `v2/` (STLs, STEP, 6-view renders, X+Y sections).

| Item | Number |
|---|---|
| Plan | irregular hexagon on {0,60,120} axes, edges **72 / 52 / 43 / 88 / 36 / 59** (all different → no mirror, no point symmetry); external 127.5 × 82.3 |
| Heights | base walls z0→30 + tongue →34 (tip-seats, v0.8 recipe); hood skirt z26→34 (**8 mm overlap**, ≥8 gate — buys the USB mouth); roof springs z34, **slope 47°** (43° from vertical, inside the design-45 limit both ways); apex z78 — **no turret** |
| SMA | boss on the SE (e1) roof facet, whip along the facet's outward normal = **43° above horizon**, teardrop bore Phase 2 |
| Zones | stack S-E (rests z5.5, USB axis z20.9 through e1 wall mouth, below skirt); HM3301 flat mid-N, can slot face 5.1 mm off the N grille wall (≥5 ✓); PM exhaust hood over can top → e2 facet; BME680 panel PARALLEL to facet e5, 6.0 mm air gap behind cross-vent louvres; WiFi landing on the N roof inner facet; desiccant clips to hood roof over the stack |
| Checks | both shells watertight; hood∩base = **0.000** (0.059 mm³ coincident seat-plane sliver shaved, guarded ≤0.5); all component envelopes vs shells = **0.000** |
| Print (massing, support_material ON) | base floor-down **43.9 g / 1h13, supports 0** · hood rim-down **44.5 g / 1h25, supports 0** → **88.3 g / 2h38 vs v0.8 132 g / 4h35 (−33 % g, −43 % t)**; Phase-2 features est. +10–15 g |

**⚠ F2 AMENDMENT NEEDED (Tomas to ratify):** the shrunken plan cannot hold BME680 ≥60 mm from the stack.
Built: BME module ≥46 mm from the XIAO socket, **sensing element ~65 mm** (rule: Grove connector toward the stack),
BME upstream at the low intake, foil + 6 mm gap, firmware T-offset trim. Restoring 60 costs ~+20 mm plan width ≈ +12 g / +20 min.

---

## 7. Phase 2 — features (2026-07-24 eve, STOPPED at checkpoint)

Phase-1 signed off same day (massing approved; **F2 amendment ratified: BME ≥46 module / ~65 sensing element, upstream + foil + T-offset**). Plan then stretched **+9 mm Y** (edges now **72/57/48/88/41/64**, ext 132.5 × 90.9, apex z82.8) — the packing fact that forced it: Grove plugs need a 13 mm insertion corridor at exactly the x-band the HM can occupies; no mirror/shift arrangement satisfied both at the old plan.

**Built (all in `tools/k1h2_model.py` → `v2/`):**
- **Closure:** 3 snap arms in the skirt (U-slot flexures print flat-in-XY at the rim, nib 1.2, keyed asymmetric on e0/e3/e5, CLR 0.45 `COUPON_TBD_SNAP`), labyrinth tongue 1.6 +0.25/side engage 4 groove-down, drip groove 1.2, elephant-foot chamfers.
- **PM intake (sealed):** plenum side walls rise to the hood inner roof (−0.5); board-edge notches (1.2 bridges); **drop-in front baffle** 39.6 × 32.4 × 1.2 in printed floor channels (can-face ↔ rib), v9-breathing-panel pattern — installs after the board, closes the dock; hex-cell grille (Ø5 cells, 1.7 webs, 20° down-skew) through e3; exterior mesh rebate + retainer; weep.
- **PM exhaust:** can-top plume → 3 gabled transfer windows in the chamber W wall (x75.6, fully E of the board) → sealed E-wedge chamber under a 45° shed → hex-cell grille through e2 + mesh rebate + weep. **Declared: capture above the can is partial (residual spill into the N cavity strip; fan momentum + chamber draw dominate) — same honesty class as v0.8's vented-chamber, better contained.**
- **Zone boundary:** corridor wall x1.5–e1 at y40 (clear of the board by 0.4); climate = S+W of it (BME cross-vent louvres e5 + e4 window + foil note, gills e1 high-E 45° down-out ×2); W gap = J2 cable pass (declared).
- **USB pocket (D-3):** alcove in e1 with 45° sloped ceiling, back face square to the plug, teardrop-gabled oval at z20.9 + press bung, switch finger slot z8.6, 45° drip fin above.
- **Mount (D-2):** 2 printed keyholes (gabled slots + head cbore + hollow-backed blisters, x4/x70) + 2 zip-tie conduit pairs through e3 into the chamber (tie fills slot; declared).
- **RF:** SMA boss on the e1 roof facet (Ø15 pad, 45° downhill wedge, inner pad to 4.0, teardrop Ø6.65 bore along the facet normal = whip at 43° up-out); pigtail hook on e2 skirt; **WiFi antenna landing 30 × 10 on the e0 inner roof directly over the XIAO's U.FL**; desiccant tray (34 × 22 fence) on the e0 inner roof, both printable at 43° lean, bands separated.
- **Cables:** 2 floor hooks; rail-lip notches at the two used Grove ports; J2 route W-around the corridor wall.

**Gates passed:** 7/7 parts watertight (trimesh, zero naked edges — two tessellation tangencies found and fixed at source) · hood∩base = 0.000 · seated baffle = 0.000 · every component envelope + plug corridor + antenna landing + sachet = **0.000** · `;TYPE:Support` = **0 on all 7 parts with support generation ON** · bridge audit: worst designed bridge 2.0 mm (conduit covers, short-direction), board notches 1.2, all ceilings gabled/45°.

**Print economy:** base 56.0 g / 2h25 · hood 51.5 g / 1h45 · baffle 2.1 g · bung 0.8 g · retainers 1.7 g → **112 g / ≈4h26 total vs v0.8 132 g / 4h35**, with USB access, sealed intake, keyhole+zip mounts, WiFi landing and desiccant that v0.8 lacked.

**Parts count:** 2 main + 5 accessories (baffle, bung, 3 mesh retainers) — brief says ask beyond 3 printed parts → **ASK AT CHECKPOINT.**

**Section-print / coupon list (gates the full print, one evening):**
1. Snap-arm crop (one arm + pocket) — engage/release, `COUPON_TBD_SNAP` 0.45.
2. Tongue/groove crop — seat + hose shed test.
3. USB pocket crop + bung — press fit `COUPON_TBD_BUNG`, plug insertion reach.
4. SMA boss crop — nut torque on the 43° pad, bore fit Ø6.65.
5. Baffle channel crop — drop-in friction `COUPON_TBD_BAFFLE` (1.7 channel vs 1.2 plate).
6. Grille + mesh + retainer crop (e3 field) — retainer press `COUPON_TBD_RAIL`, cell cleanliness at 20° skew.
7. Board-fit rehearsal: HM3301 on rails (settles TBC-01 mirror), shield under nibs, plugs at both ports, BME into slots.

*Change log: K1H2-P0-DRAFT 2026-07-24 — Phase-0 ground truth; SIGNED same day (D-1..D-3). Phase-1 massing gated + signed same day (F2 amended 46/65-upstream). Phase-2 features built + gated same evening; stopped at features checkpoint.*
