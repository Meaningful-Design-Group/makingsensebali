# K1H2 "low boulder" — Print Plan (Phase 3, 2026-07-24)

Outdoor LoRa+WiFi air-quality node, Fab City hex facet system, Bali monsoon.
Two main prints + five accessories, zero hardware in the enclosure itself.
Source `tools/k1h2_model.py` (build123d) → `v2/` (STL + STEP per part, gcode,
6-view renders, X/Y sections). Spec + decision log: `SPEC_K1H2_PHASE0.md`.
Phases 0/1/2 signed by Tomas 2026-07-24 (D-1 economy-first clean sheet,
D-2 keyholes+zip-ties, D-3 USB recess, F2 46/65-upstream, parts 2+5,
exhaust-spill + zip-conduit declarations ratified).

## Gate table (CORE One HF0.4, PETG, 0.15 SPEED, ASCII gcode, support_material ON = hardest gate)

| Part | Orientation (bed face) | Watertight | ;TYPE:Support | g | Time |
|---|---|---|---|---|---|
| base | floor-down (as modeled) | yes | **0** | 56.0 | 2h25 |
| hood | rim-down (as modeled) | yes | **0** | 51.5 | 1h45 |
| baffle | flat | yes | **0** | 2.1 | 4m |
| bung | face-plate down | yes | **0** | 0.8 | 6m |
| ret_n (FC-hue accent) | flat | yes | **0** | 0.6 | 2m |
| ret_e | flat | yes | **0** | 0.5 | 2m |
| ret_w | flat | yes | **0** | 0.6 | 2m |

**Per unit ≈ 112 g, ≈ 4h26** (v0.8 was 132 g / 4h35 with no USB access, no sealed
intake, no keyholes). Assembled interference = 0.000 mm³ (hood∩base, baffle
seated, every board envelope, plug corridor, antenna landing, sachet).

## Per-part plans

### base — prints floor-down
- **Why support-free:** all walls plumb; every internal ceiling is 45°-gabled,
  45°-arched or a ≤2.2 mm short-direction bridge; hex cells are point-up
  (60° self-supporting tops); gill slots and louvre fins are 45° plates;
  alcove ceiling is a 45° single slope; keyhole slots carry printed gables.
- **Declared bridges (all ≤ 5 until coupons):** zip-conduit covers 2.0 (short
  direction) ×4 · plenum-wall board notches 1.2 ×2 · mesh-rebate roofs 1.4
  (short direction) ×3 · snap-pocket roofs 1.3 ×3.
- **Elephant foot:** 0.4 × 45° chamfer cut on bed edges + profile compensation ON.
- **Z-seam:** profile `seam_position = aligned`; place spool-side toward the e3
  (rear/wall) facet in the plater so the aligned seam lands on the mounting face.
- First layer: full hex floor, no brim needed (PETG on textured sheet).

### hood — prints rim-down (as modeled; apex up)
- **Why support-free:** roof facets 47° from horizontal (43° from vertical,
  inside the design-45 limit); skirt plumb; snap arms cut flat in XY at the
  rim; drip groove faces up in print; desiccant tray + WiFi-landing zone walls
  lean 43° standing on the inner roof plane; SMA pad's downhill overhang is
  filled by the printed 45° wedge; bore is teardropped, point up-slope.
- **Declared bridges:** groove ceiling ring 2.1 (tongue seats against it —
  v0.8-proven) · snap-arm top slots 1.5 ×3.
- **Z-seam:** aligned → rotate in plater so it rides the e3-side arris (gutter,
  off weather faces).

### baffle / bung / retainers — flat plates
- Full-contact first layers, no overhangs. ret_n is the ONE accent-colour part
  (FC hue) per CMF; everything else matte white.

## COUPON_TBD table (section prints gate the full build — one evening)

| Tag | Value in CAD | Coupon |
|---|---|---|
| COUPON_TBD_SNAP | 0.45 | snap-arm crop + pocket: engage/release by hand, no whitening |
| COUPON_TBD_BUNG | oval −0.2/side | bung into pocket crop: firm press, tool-free pull |
| COUPON_TBD_BAFFLE | channel 1.7 vs plate 1.2 | drop-in crop: slides, seats, no rattle |
| COUPON_TBD_RAIL (mesh) | rebate 1.3 / frame 1.2 | retainer press into grille crop |
| rails 0.30 / slide 0.25 / free 0.40 | §5.1 inferred | board-fit rehearsal (below) |
| SMA bore Ø6.65 | +0.3 horiz rule | boss crop: bulkhead through, nut torqued on 43° pad |
| tongue/groove +0.25/side | v0.8 recipe | seam crop + hose test |

Board-fit rehearsal (settles TBC-01/02/03): HM3301 onto rails can-face-north —
if the slot faces south, flip the board (ducting is mirror-capable); shield
under the nib fingers, plugs into both notched Grove ports; BME680 into the e5
slots, connector toward the stack; photo-check the shield is v1.2 (no holes);
measure the kit WiFi antenna against the 30×10 landing.

## Assembly order (tool-free)
1. Mount the base: keyholes on 2 wall screws you already have, or 2 zip-ties
   through the rear conduits around a pole. Weeps down. Mount BEFORE boards.
2. HM3301 onto rails (vent face toward the N grille), drop the front baffle
   into its channel. Shield stack onto rails until the E stop clicks under the
   nib. BME680 into the e5 slots, foil liner behind the louvre panel
   (≥15 mm from the WiFi landing — it is, by construction, across the box).
3. Grove cables: BME → W-route S of the corridor wall; HM J2 → around the wall's
   W end; both into the two notched N-row ports. Cables into the floor hooks.
4. Pigtail onto the Wio U.FL, up through the e2 hook, bulkhead out the roof
   boss, nut outside, whip on (43° up-out). WiFi antenna onto the XIAO U.FL,
   stick/clip to the landing on the inner S roof.
5. Desiccant sachet into the hood tray. Mesh scraps into the three rebates,
   snap the retainers (accent = intake).
6. Hood on: one orientation only (keyed snaps), press till 3 clicks. USB bung in.
   Service: bung out for USB/switch; hood off = 3 snaps for everything else.

## Declarations (ratified 2026-07-24)
- PM intake fully sealed (plenum + baffle + mesh); PM exhaust capture partial —
  residual can-top spill into the N cavity strip is declared; primary path is
  the 3-window transfer → sealed E chamber → e2 grille. Better contained than
  v0.8's open model. Correct PM for RH in the dashboard, not firmware.
- Zip-tie slots pass through e3 into the exhaust (outbound) chamber; ties fill
  the slots, pole shadows them.
- Corridor-wall W gap = J2 cable pass (soft zone boundary at the far-W, low).
- Skirt overlap 8 mm (gate minimum) — bought the USB mouth height.
- Plenum top closes against the hood inner roof at 0.5 mm (pressure-equalized
  by design; weeps at every zone floor). The box breathes; it never seals.
