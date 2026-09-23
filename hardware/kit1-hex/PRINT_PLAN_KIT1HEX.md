# KIT 1 HEX v0.8 "basalt hood" — Print Plan (2026-07-24)

Two-part outdoor master (Bali monsoon): BASE tub + HOOD with 52° skeleton
roof + SMA turret. Irregular hexagon 137×87, all walls on hex axes
{0/60/120°}, all six edges different (74/70/30/100/44/56) — no mirror, no
point symmetry. Source `tools/kit1hex_model.py` (build123d), config
`tools/coreone_petg_015speed.ini` (extracted from kit1 shipping gcode).

## Gate (CORE One HF0.4, PETG, 0.15 SPEED, ASCII gcode, support_material ON = hardest gate)

| Part | Orientation | ;TYPE:Support | control ;TYPE: | Watertight | g | Time |
|---|---|---|---|---|---|---|
| hood | rim-down (as modeled) | **0** | 4516 | yes | 73.7 | 2h26 |
| base | floor-down (as modeled) | **0** | 3179 | yes | 56.8 | 2h03 |
| retainer_n | flat | **0** | 42 | yes | 0.9 | 3m |
| retainer_w | flat | **0** | 42 | yes | 0.4 | 2m |
| grommet | flat (reuse kit1 part+gcode) | 0 (kit1 gate) | — | — | ~1 | 5m |

**Per unit ≈ 132 g, ≈ 4h35.** Interference (assembled) = 0.000 mm³.
Overhang audit: every down-face ≥45°-from-vertical except the DECLARED
bridges below. Elephant-foot: rim/base chamfer partial (OCC declined some
edges) → keep profile's elephant-foot compensation ON.

## Declared designed bridges (all ≤5 mm, print as bridges)
- hood z25.2: drip-groove roof ring, 1.0 mm span.
- hood z31.5: snap-arm top-slot roofs ×3, 1.5 mm.
- hood z38.0: seam groove roof ring, 2.1 mm (tongue seats against it).
- base z5.5: desiccant-fence air-notch roofs ×4, 5.0 mm.
- base z27.5: mesh-rebate roof (N +W), 1.3 mm.

## Architecture (as built)
- Seam z34, labyrinth: base tongue 1.6 (3.4..5.0 inset, z34..38) into
  hood groove (0.25/side), tongue tip = positive seat. Hood skirt overlaps
  base 10 mm, sharp drip lip + 1.2 groove at z24.
- Closure: 3 snap arms cut into the skirt (U-slot flexures, arm 14×6,
  print flat at bed), nib 1.2 into gabled wall pockets. Asymmetric spacing
  (S/N/W walls) = keying. CLR 0.45 = COUPON_TBD_SNAP.
- SMA turret: irregular hex column (13/8/7/14/7/8), z~43→102, own 52°
  mini-roof; teardrop Ø6.65 bore z72 through south face; internal pad →
  4.0 wall at bore; pigtail up the shaft, nut outside. Whip TBC-02 (elbow?).
- PM intake: 3 gabled windows 12×10(+6) N wall, direct-coupled to HM3301
  can face (3.95 mm gap), 2×45° louvre fins, mesh rebate + retainer_n
  (FC-hue accent part). TBC-01 mirror: flip board on rails if slot faces S.
- PM exhaust: can-top grille → cavity → 2 gill slots (12×2.2 @45°) NE hood
  wall + seam leakage. Vented-chamber model, declared in data docs.
- BME680: vertical panel x=-6 (posts + slots), behind 2 gabled W windows
  + fins + retainer_w; hood W gills ×2 above. Foil liner + 2-3 mm air gap
  on the panel = assembly note (IR). ≥60 mm from stack.
- Boards: zero screws — rails + end stops + 45/45 nib fingers (HM east,
  stack east). Grove Shield y9..34, XIAO/USB end north… USB service =
  hood off; permanent power = Ø4.5 cable via kit1 split grommet, W wall
  teardrop Ø6.7 @ z12, drip loop outside.
- Mounts: 4× M4 countersunk through floor (7,11)/(52,21)/(84,70)/(-14,52)
  — mount base BEFORE dropping boards in. Weeps Ø2.5 ×3.
- Desiccant fence 12×18 east, notched for airflow.

## Coupons before batch (one evening)
1. Snap-arm section (one hook + pocket crop): engage/release force, 0.45.
2. Tongue/groove crop: seat + shed test (hose).
3. Board fit: HM3301 on rails (settles TBC-01), shield under fingers,
   BME in slots. 4. SMA torque on a turret crop; grommet carry-over.

## Known deviations from SPEC (agreed at checkpoints)
- Service notch dropped (reflex edges break the 52° envelope) → asymmetry
  via unequal edges + turret. USB wall port dropped (no hex-legal wall is
  square to the connector) → hood-off service + grommet power.
- SMA dormer → turret (dormer cbore breached the roof).
- BME wall standoff 16 mm (not 6) — cross-vented chamber, honest note.
