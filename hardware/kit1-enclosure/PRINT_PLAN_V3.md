# KIT 1 v3 "PLANETAI light" — Print Plan (2026-07-23)

Ø110 poly-faceted sphere, N=8, wall 1.6 mm, THREE parts, no internal tray:
boards mount directly on the shell's inner facets. Rhino source
`kit1_v3_planetai.3dm` (v3_* objects; note: the saved band predates two
mesh-level fixes — the STLs are the shipping truth; the 3dm one-number fixes
are recorded below).

## Gate (final STLs, CORE One HF0.4, PETG, 0.15 SPEED, ASCII gcode)

| Part | Orientation | Support | control | Watertight | Filament | Time |
|---|---|---|---|---|---|---|
| v3_bowl | base facet down | **0** | 1987 | yes, 0 open | 32.7 g | 1h28 |
| v3_band | rim down | **0** | 906 | yes, 0 open | 45.1 g | 1h47 |
| v3_crown | flat down | **0** | 193 | 20 cosmetic edges (slicer-healed; own coupon) | 9.9 g | 26m |

**Per unit: ~88 g, ~3h41.** Six units ≈ 0.53 kg, ~22 h — one weekend.
(v2 was 249 g / 10h25; v1 273 g / 9h50 + tray.)

## Architecture

Same three-piece planet as v2, shrunk and gutted: bowl + band (equator
teardrop-lug bayonet, 18° twist) + crown (twist-lock polar cap, cord through
the pole, knot in a cone-roofed pocket). Hang by cord / keyhole az112.5 /
flat base Ø64.

**Direct-to-shell mounts (tool-free, dome off = everything in reach):**
- HM3301 lies across the sphere's waist (board z −10, can crossing the seam
  into the band's interior — the interior is continuous). Ends drop into two
  C-channels on the az135/315 facets (shelf + gabled end-lips, ±1 mm play).
- Grove shield stands vertically against the az67.5 facet: two bottom ledges,
  two top snap-hooks. XIAO/USB end faces az22.5; the USB-C teardrop bore is
  cut at 40° so the plug lines up with the port — power and flashing without
  removing anything but the band.
- BME680 slides between two flank rails on the az180 facet, behind its kite
  grid, standoff ~5 mm (foil + air-gap note still applies).

**Airflow model changed honestly at this size:** no ducts. The sphere is a
vented sampling chamber (AirGradient-style): accent intake triangle az225
(mesh rebate) feeds the lower bowl next to the HM slot side; the fan exhausts
into the interior; air leaves via gill slots (az292.5+337.5), the BME grid,
and the seam labyrinth. Some recirculation smoothing of PM peaks vs the v1/v2
ducted design — acceptable at DIY grade; note it in the data docs.

## Declared residuals

- Bowl 82 mm²: flat undersides of the small C-channel shelves and intake
  rebate ledge (internal, ≤7.5 mm deep; print with slight droop — v3.1 adds
  50° wedges under them).
- Band 318 mm²: crown-post nub undersides + throat-bore rim ring (~0.5 mm
  bridge) + groove roofs (1.3 mm bridges). All bridges.
- Crown 246 mm²: three Ø8 groove pocket roofs (DB, crown = its own coupon).
- Envelope overlaps ≤41 mm³ = clip retention engagement + conservative
  box-corner artifacts. Verify at first fit with real boards.

## Recorded 3dm deltas (the saved band predates these)

1. BAND_VOID last ring z 42.0 → 45.8 (opens the throat; STL fixed via bore).
2. Corner tabs: 8 @ az22.5+45k → 4 @ az0/90/180/270, r44.5..53.0 (the
   originals pierced the thin mid-facet wall — the corner/mid swap between
   twisted rings, both directions of the v2 lesson).

## Coupons (one evening)

1. Bayonet section (bowl+band z −8..+10 crop): twist, ramp, detent, release.
2. Crown (26 min, complete part = coupon): twist-lock + cord knot pocket.
3. Board fit: real HM3301 into the C-channels, shield into its clips, BME
   into rails. This also settles TBC-01 (slot side) — flip the board if needed.
4. Grommet + bore coupon carries over from v1 (cable Ø4.5).

Antenna: stick the kit's FPC antenna to the band's interior (adhesive), or
clip the whip diagonally — interior diagonal ~95 mm fits it. Mesh retainer
ring: regenerate for the v3 intake triangle (2-min print, TODO).
