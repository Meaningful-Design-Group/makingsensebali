# v10 — DIY-node enclosure (BUILD): organic shell + base breathing

> 🟡 **STAGING — NOT FOR PRINT.** Architecture + layout resolved; fits are `COUPON_TBD_*`,
> ICD §5.1 still TBD. **The HM3301 envelope (40×40×16) is caliper-confirm** — measure a
> physical unit before committing. Organic form is a **first pass** to react to.
> Generators: `tools/enclosure_v10.py`, `tools/breathing_panel_v10.py`,
> `tools/dimension_render.py`. Built 2026-06-10.

## What changed from v9 (Tomas review, 2026-06-10)

1. **Breathing moved to the base.** The side slide-in window is gone. The whole bottom is
   a large drop-in **gyroid breathing panel** (`v10_{basic,plus}_panel.stl`): Basic vent
   ~35×25, Plus ~35×37 — much bigger than the old 30×30 side plate. Air enters low through
   the base, rises past the BME680 (low, fresh) and XIAO (high, sheds heat), exits the high
   exhaust louvers. One clean base→top chimney.
2. **HM3301 corrected to ~40×40×16.** v8/v9 reserved an **80×40** bay sourced only from the
   schematic (no mechanical drawing). The Grove HM3301 is a ~40×40 board. The Plus front bay
   is resized. ⚠️ **Confirm by caliper** (board L×W, can, hole spacing) before print.
3. **Organic shell over the kept chassis.** The body is a softly-lofted, front-leaning pod:
   flat back retained for wall-mount keyholes, soft corners, gentle low bulge, the front
   face leaning back toward the top. Width is held constant so the perfboard always fits —
   the organic read comes from the front lean + soft corners, not from pinching the guts.
   All validated internals carry over **verbatim**: perfboard standoffs, keyholes, HM
   rails/pegs, exhaust louvers, ePTFE boss, separate hood (2× M3), press-fit base.

Sensor set (your call): **current build** — XIAO ESP32-S3 + BME680 (+ HM3301 on Plus). No SEN54.

## Internal strategy (answering "are they on another board?")

One **perfboard (40×60)** carries XIAO + BME680 on female headers — the workshop's one-board
solder job, kept intact. The **HM3301 (Plus) is the only separate module**, standing vertically
in printed front rails with two registration pegs into its mounting holes. Everything hangs off
the flat back wall (standoffs + keyholes); the base and hood are separate parts. See the
dimensioned layout maps for exact positions and clearances.

## Build result (2026-06-10, staging)

Both variants: **single watertight solids, interference 0.000 cm³** (incl. seated base panel).

| Variant | body (mm) | hood (mm) | base (mm) | breathing vent | base panel |
|---|---|---|---|---|---|
| basic | 50 × 42 × 84 | 53 × 34 × 15 | 48 × 40 × 11 | ~35 × 25 | flange 41×31 |
| plus  | 50 × 54 × 94 | 53 × 45 × 15 | 48 × 52 × 11 | ~35 × 37 | flange 41×43 |

Renders: `review/v10_{basic,plus}_layout.png` (**dimensioned, to scale, mm** — read the fits
here), plus `review/v10_plus_{assembly,cutaway}_preview.png` (3D form).

## What the dimensioned map flags

- **Perfboard fit:** 40 mm board in a 43 mm cavity → ~1.5 mm each side. Fine.
- **HM3301 fit (Plus):** 40 mm board in the 43 mm cavity → also ~1.5 mm/side, and the rails
  share that margin — **tight**. If the caliper says the real HM3301 is wider than 40, the
  Plus body needs to widen. This is exactly why the envelope is caliper-confirm.
- **Front lean:** base depth (Basic 40 / Plus 52) tapers to a 43 mm top depth — the front
  leans back ~9 mm. Nothing internal sits in the leaned-back top volume.

## Open items / next

1. **Caliper the HM3301** → set the real envelope; rebuild if it's not ~40×40.
2. **Organic form is a first pass** — say where to push it (more taper? rounder? a defined
   front feature?) before it's frozen.
3. Fill **ICD §5.1** from the coupons → the press-fit (`COUPON_TBD_PRESSFIT`), base-panel seat
   (`COUPON_TBD_PANELSEAT`), HM rail (`COUPON_TBD_SLIDE`), pegs, standoffs all get real values.
4. Section-test order unchanged in spirit: press-fit ring → hood bosses → base-panel seat.
