# KIT 1 v2 "PLANETAI" — Print Plan (2026-07-23)

True poly-faceted sphere Ø150, N=8 (chunky low-res read), four printed parts.
Built live in Rhino (`kit1_v2_planetai.3dm`, objects named v2_*), gated with the
same fail-closed pipeline as v1. Machine: Prusa CORE One HF0.4, PETG, profiles
as v1, ASCII gcode, support grep verified against live control markers.

## Architecture (what changed vs v1 and why)

The v1 spire existed because a closed faceted dome cannot print support-free.
v2 keeps the SPHERE by paying the physics differently: the polar cap becomes a
separate faceted **crown** (8 facets + apex) that prints flat-face-down — zero
overhang by construction — and twist-locks onto the **band** (equator to 55°
latitude). The band's interior above ~14° latitude is a 37.5°-from-vertical
**corbel funnel**: it is simultaneously the printable ceiling, the crown's
seat, and the hang-load ring. The **bowl** is v1's lower half re-faceted at
N=8. Hang is a **cord** through the crown's pole (Ø5.8 teardrop hole, knot in
a cone-roofed pocket); crown lugs carry the load into the band; the equator
bayonet carries it into the bowl. Wall-mount keyhole az112.5; flat base
facet Ø88 to sit.

Zones as v1, remapped to the N=8 facet grid: PM intake = accent triangle
az225 (mesh rebate); PM exhaust = carved 50° gill slots az292.5+337.5 (flank
the bay tunnel mouth); BME kite-grid az135; convection grid az180; USB-C
teardrop az22.5 at z−10 (no boss — the bore runs through wall + corbel ring =
native grommet engagement); tray pins now at az10/60/100 (bay-free quadrant).
Grove shield sits on ledges beside the bay — as central as an 80 mm sensor
module allows on a Ø92 deck; the antenna mast holds the true center axis.

## Gate evidence (final)

| Part | Orientation | Support | control | Watertight | Filament | Time |
|---|---|---|---|---|---|---|
| v2_bowl | base facet down | **0** | 2208 | yes, 0 open | 101.6 g | 3h51 |
| v2_band | rim down (deployed) | **0** | 1478 | yes, 0 open | 104.8 g | 4h03 |
| v2_crown | flat underside down | **0** | 245 | 4 cosmetic open edges (slicer healed; part = own coupon) | 19.9 g | 47m |
| v2_tray | deck flat | **0** | 1081 | yes, 0 open | 57.0 g | 1h55 |

Interference (closed assembly, Rhino BREP intersections): all pairs 0.00 mm³.
crown↔band 0.22 mm³ = intentional detent preload at the untwisted rest
position. Board envelopes (HM 80×40×16.6, shield 39.5×25×26.6): 0.00 vs all.

Overhang audit residuals, all declared:
- DB-2: band web annular gaps (2.5 / 3.6 mm ring bridges at z8.5). Bridges.
- DB-3: crown groove pocket roofs (3× Ø8 internal). Bridges; crown coupon.
- Bowl: 18 mm² teardrop-tangent slivers. Cosmetic.
- Tray: 0 mm². Clean.

Per unit: ~283 g, ~10h40. Six units ≈ 1.7 kg, ~64 h.

## Knobs Tomas may want to turn (all in the 3dm / build script)

- Band mass (105 g): the corbel funnel at 37.5°-from-vertical is rule-clean
  45° after faceting. Your machine spec allows 50°: reverting the funnel to
  43° meridian saves ~50 g if you accept ~47° interior facets. Sector relief
  pockets could save another ~25 g. Both noted in the build script.
- Crown (20 g sliced): currently solid tent; relief pockets possible.
- Facet count: N=8 everywhere; N=6 goes chunkier still.

## Open / carried

- Mesh retainer ring must be regenerated for the v2 intake triangle (v1's
  fits v1's facet). Two-minute print once sized; grommet carries over as-is.
- TBC-01 (HM3301 slot side) still confirmed by the tray-bay coupon; plenums
  symmetric, board flips if needed.
- Coupons before batch: bayonet ring section, crown (own print), grommet
  bore, tray bay slide with the real HM3301. Cord: 3–4 mm paracord, figure-8
  knot in the crown pocket.
- Bali variant note: same shells; consider ePTFE-taped weep + finer mesh at
  the intake for monsoon deployment.
