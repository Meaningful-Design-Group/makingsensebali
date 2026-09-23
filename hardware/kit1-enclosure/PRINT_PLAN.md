# KIT 1 enclosure — Print Plan (v1, 2026-07-23)

Machine: Prusa CORE One, HF0.4, PETG. Profiles used for every gate slice:
printer "Prusa CORE One HF0.4 nozzle" · print "0.15mm SPEED @COREONE HF0.4" ·
filament "Generic PETG @COREONE HF0.4". Gcode sliced ASCII (`binary_gcode=0`)
so the support gate is verifiable by grep.

## Gate evidence (final run, all five parts)

| Part | Orientation on bed | `;TYPE:Support` | control (`External perim`) | Filament | Time |
|---|---|---|---|---|---|
| kit1_lower | base facet down (as deployed) | **0** | 1959 | 107.7 g | 3h48 |
| kit1_upper | rim down, spire up (as deployed) | **0** | 1599 | 102.4 g | 3h29 |
| kit1_tray | deck flat on bed | **0** | 1203 | 62.0 g | 2h17 |
| kit1_grommet | flange down | **0** | 120 | 0.7 g | 9m |
| kit1_meshring | flat | **0** | 12 | 0.4 g | 2m |

All STLs watertight, 0 open edges (trimesh, merged). Interference checks all
0.00 mm³ (upper↔lower closed, tray↔lower seated, HM/shield envelopes vs both).

Per unit: ~273 g, ~9h50, 3 plates (lower / upper / tray+smalls).
Six units: ~1.64 kg, ~59 h machine time — one printer, ~6 days at one plate
per evening, or 3 days running two plates/day.

## Overhang audit (geometric, independent of slicer)

Rule: no downward face steeper than 45° from horizontal, else a named fix.
Residuals, all declared:

- DB-1 (upper): Ø9.8 flat internal ceiling at the spire tip inner cap
  (z=107.5). Designed bridge, internal, cosmetic-irrelevant. Verified by the
  spire-tip coupon (below) before batch.
- Lower: 51 mm² of ≤3 mm² tessellation slivers exactly at 45.0°, at the
  corbel-to-wall junction ring. Prints as bridged micro-steps; invisible
  (internal).
- Tray: 11 mm² of sub-3 mm² nubbins at clip/ledge corners. Cosmetic.

Everything else ≥45°: shell facets 55–59° from horizontal, corbel underside
50°, bayonet teardrop lugs/grooves 50° roofs, kite grid holes (50° roofs, cut
on horizontal axes), exhaust gill channels 50°, USB and keyhole teardropped
50°+, tray gable roofs 46.8°, corridor corbel 63°, snorkel gable 45.9°,
mast base shaved by the tunnel-cavity plane (46.8°).

Designed bridges (all ≤4 mm, standard FDM practice, no support wanted):
upper web ring annuli (2.5 / 3.7 mm), bayonet groove roofs (1.3 mm radial),
boss-slot none (open-top pins). Slicer bridges these; do not enable supports.

## Print settings notes

- Supports OFF (they are off in the profiles; leave them off — the design is
  the support).
- Seam: rear / nearest-to-az0 (wall side). On the lower this parks the seam on
  the keyhole facet, which faces the wall in service.
- Elephant-foot compensation on (profile default 0.2). No brims needed:
  lower lands on the Ø88 base decagon, upper on its Ø145 rim annulus + ring
  walls, tray on the full deck.
- White PETG body. Accent: reprint the mesh retainer ring (and optionally the
  grommet) in the FC accent hue — the triangular intake mouth is the accent
  moment. Fuzzy skin optional on shells (body panels only).

## Coupons before committing the batch (one evening, <2 h total)

1. **Bayonet ring section** (~40 min): slice a 12 mm-tall horizontal section of
   lower+upper at z −5..+12 (crop in slicer). Verify: quarter-turn engages,
   ramp clamps, detent clicks, halves release. Governs COUPON_TBD_BAYONET
   (0.45 radial). If it binds: +0.1 via `SLOT_CLEAR`; if sloppy: −0.1.
2. **Spire tip** (~20 min): crop upper z >90. Verifies DB-1 bridge + loop.
3. **Grommet + bore test** (~10 min): grommet + a 20×20 wall coupon with the
   teardrop bore. Cable Ø4.5 grip governs COUPON_TBD_GROMMET (grip Ø4.3).
4. **Tray bay section** (~30 min): crop tray x±? around the HM bay, slide the
   real HM3301 in: rails 0.30, corbel clearances, corridor window. Confirms
   TBC-01 (slot-face side) by eye — if the slot faces +Y instead of −Y, flip
   the board 180° (bay is symmetric in X; plenum feeds either end).

## Assembly (no tools)

1. Boards onto tray on the bench: HM3301 slides into the bay on rails from the
   +X end to the stop; Grove shield drops between flanks onto ledges; BME680
   drops into the edge clip on the arm; whip antenna into the mast cup
   (C-slot sideways), U.FL pigtail routed under the bay roof to the shield.
2. Grove cables: HM3301 cable exits the bay through the gabled notch; BME
   cable over the bay roof through the hooks. USB-C in through the grommet
   facet (az36), drip loop outside, plug into XIAO.
3. Tray drops into the bowl over the three gabled pins (one orientation).
4. Mesh scrap into the intake rebate, retainer ring presses in.
5. Dome on: align the four entry slots over the tongue lugs, press, twist
   ~20° until the detent. The whip disappears up the spire as you lower it.
6. Hang by the loop, or wall-mount: one screw, keyhole facet (az0), head
   Ø<9 mm, stand-off ~6 mm; USB cable acts as the soft anti-rotation. Or sit
   it on the base facet on a desk.

## Deployment notes (Boston, semi-sheltered)

- Line the BME680 facet's inner pocket with adhesive foil tape + keep the
  2–3 mm air gap to the board: FDM PETG is IR-transparent; the foil blocks
  radiant gain so T/RH reads true. One 40×40 scrap per unit.
- Orient the BME/grid facets away from afternoon sun if hanging free (node is
  rotationally free on the loop; the grids sit at az144/216 relative to the
  keyhole facet).
- The seam labyrinth is deliberately NOT airtight: it is the enclosure's
  distributed vent + pressure equalizer. Do not tape it.
- Weep hole is in the base center; active when hung/wall-mounted. A node
  sitting on a table in rain is not a supported case.
- PM intake (accent triangle, az252) and exhaust gills (az324/342) both face
  down-out under the ball's own belly — no hoods needed, the form is the hood.
- Firmware note: apply an RH correction to HM3301 PM readings (fan-driven
  optical sensors over-read in fog/high RH), and a small T offset for the
  BME680 if the node hangs in full sun despite the foil.

## Parameters that matter later (kit1_model.py `P` dict)

`WALL` 2.5 · `RINGS` (the whole silhouette) · `TONGUE_*`/`CH_*`/`SLOT_CLEAR`
(bayonet) · `GRID_*` (perforation) · `TRI_INSET_*` (intake) · `LOUVRE_*`
(exhaust gills) · `BOSSES` (tray registration) · `SHIELD_L` 39.5 (set 58.0 for
the unbroken Grove shield — relayout needed, see code comment) · `STACK_H` 25
(headroom over the shield). KIT 1+ screen facet: use az288 equator facet
(currently blank) — cut with `facet_frame(288, -11)` + a window; KIT 2: swap
the bay contents, shell untouched.
