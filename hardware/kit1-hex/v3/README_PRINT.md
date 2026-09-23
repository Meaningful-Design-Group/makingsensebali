# K1H3 "meru" v6 — Production print bundle (2026-07-25)

**Two parts. Nothing else.** Outdoor LoRa+WiFi air-quality node · Fab City hex system · Bali monsoon.

| File | Part | Print as | g | Time | Support |
|---|---|---|---|---|---|
| `k1h3_shell.stl` / `k1h3_shell_FINAL.gcode` | pyramid shell, matte WHITE | as-is, rim on bed | 38.1 | 1h49 | **0** |
| `k1h3_grille_print.stl` / `k1h3_grille_FINAL.gcode` | grille, FC-hue ACCENT | as-is, floor on bed | 13.5 | 0h59 | **0** |

**TOTAL 51.6 g · 2h48.** (v5 was 86 g/4h11 in 3 parts; K1H2 was 112 g/4h26 in 7.)
`k1h3_asm.step` = CAD assembly · `k1h3_asm_viz.stl` = assembly + sensor volumes (best for review).
Gcode: Prusa CORE One, HF0.4, PETG, "0.15mm SPEED @COREONE HF0.4", support generation ON in-profile.

## What changed in v6 (Tomas iter-5)
- **Height 110 → 64.7 mm.** The dome truncates the pyramid, so cutting it lower is the
  material lever — the facets keep their 47° (rain-shedding, support-free) and the object
  just gets shorter. Footprint unchanged (132.5 × 90.9).
- **Wall 2.5 → 1.6 mm** = 4 perimeters at 0.4 nozzle: the honest minimum for a
  weather-facing PETG wall (watertight recipe). 3 perimeters is not trustworthy in monsoon.
- **Vents are now rain-proof by geometry.** No opening anywhere near the top. The four
  vents sit LOW on the two lee facets and their passage runs **up-and-inward at 45°** —
  the outer mouth looks down-and-out, so a droplet would have to *climb* ~4 mm to get in,
  while warm air still leaves by buoyancy. Both passage walls are at 45°: self-supporting.
- **Two parts only.** The deck is deleted: the shield now zip-ties to the **top** of the
  grille (locating curbs on 3 sides, N curb notched for the two Grove plugs), the sensors
  hang **below** the same plate. One plate, both jobs.
- **RAIN GATE (new, automated):** ray-casting 8,000+ vertical columns over the HM3301,
  the shield/stack and the BME680 → **0 columns with no material above them.** No vertical
  path for rain reaches any hardware. The BME and HM were shifted 3 mm north because the
  test found a 1 mm uncovered fringe at the south edge — that is exactly why the test exists.

## Kept from the v5 design review
Fan relief Ø24 over the HM can-top fan + Ø29 mesh rebate · USB port square to the plug and
tilted 12° down-out with a mitred corner brow above · graduated vents · datum reveal groove
at the plinth · 2 wall keyholes + 2 zip-tie conduit pairs on the flat rear (e3) band · SMA
boss with 45° wedge and teardrop Ø6.65 bore · drip lip + groove · elephant-foot chamfers.

## Assembly (tool-free, zero hardware)
1. Zip-tie HM3301 **under** the grille: can-top fan under the Ø24 relief, intake facing
   the south standoff (flip the board if the slot is on the other face — TBC-01).
2. Zip-tie BME680 under the grille in the south strip, at the HM intake (reads inlet RH);
   foil card on the same ties, foil up.
3. Cables up through the stadium aperture (plugs pass **pre-connected**). Shield onto the
   grille top between the curbs, zip-tied; Grove plugs over the notched north curb.
4. Grille assembly up into the shell: floor edge cams past the two nibs, seats on the four
   support columns. USB/switch reachable through the tilted corner port.
5. SMA pigtail → e5 boss, nut outside, whip up-out. WiFi antenna on the grille tab.
6. Mount: 2 keyholes (M4 pan heads) or 2 zip-tie pairs on the flat rear band, drip lip down.

## Coupon night before the batch
Nib engagement · keyhole on a real M4 head · SMA nut torque · dome inner-crown bridge ·
vent mouth cleanliness at 45° · fan-mesh retainer · hose test from above and at 45°.
