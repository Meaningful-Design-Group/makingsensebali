# v12 — DIY-node MODULAR STACKING SYSTEM (BUILD)

> 🟡 **STAGING — print ONLY the rim fit sections.** ICD §5.1 is **INFERRED** (1.12-DRAFT,
> Tomas waived coupon measurement, ±0.1 confidence): the press-fit rim **section print is
> the de-facto coupon** and gates all full modules. Generator: `tools/enclosure_v12.py` +
> `tools/fit_section_v12.py`. Built 2026-06-11, HM geometry rev same day.

## The idea (Tomas, 2026-06-11)

A **tower of interchangeable tier-modules** on one standard interface. The stack grows with
the number of sensors and the deployment (indoor vs outdoor); the stacking *is* the meru.

- Modules are clean **gyroid-window boxes**; only the **crown** carries the meru eaves/finial.
- Standard **press-fit keyed rim**: each stacking module has a bottom **spigot** that press-fits
  into the open-cavity **socket** of the module below (`COUPON_TBD_STACK` = 0.15, INFERRED).
  The cavity is open top-to-bottom, so air rises and the I²C + power cable runs up the centre.
  The rectangular section + flat back key the orientation.
- Flat back + keyholes on every module → the stack lies flush on a wall at any height.

## Parts (common footprint 46 × 26 mm)

| Part | Role | Size (mm) |
|---|---|---|
| **Basic** | XIAO + BME680 (BME low / XIAO high), base intake grille at the bottom. Indoor core. | 46 × 26 × 58 |
| **Plus** | HM3301 module (Eagle-resolved geometry) + **sideways** PM apertures at the can vent zone. Stacks on Basic. | 46 × 26 × 103 (96 + spigot; **no more ±22 bump**) |
| **HM bar** | Skewer bar through the Plus side-wall mortises — retains the HM board's top strip. | 45 × 3 × 8 |
| **Crown** | Faceted 3-tier meru, generous eaves (overhang to 66 × 50), bottom spigot. Outdoor top. | 66 × 50 × 47 |
| **Cap** | Low gyroid-vented top (gyroid INTEGRATED — one part, 48% open), bottom spigot. Indoor top. | 46 × 26 × 29 |
| **Fit sections** | `v12_fit_section_socket` (top 14 of a tube) + `v12_fit_section_spigot` (6 of tube + spigot). **THE §5.1 COUPON.** | 46 × 26 × 14 / 13 |

All: **single watertight solids, component interference 0.000 cm³** (incl. bar vs body/board).

## Plus module — HM3301 reality (ICD 1.12, from Seeed Eagle .brd + datasheet V2.1)

- Board exactly **80×40**; can (40×38×15) occupies board-z **14.6..54.6, Grove end DOWN**
  (the 4P cable drops through the centre floor gap to the Basic below).
- Both air ports on the can's one **40×15 narrow face → they face SIDEWAYS.** PM apertures
  are side-wall slots at the can vent zone (low + high pair per side), **mirror-symmetric**
  because the datasheet doesn't label in vs out — confirm direction by feel at power-up.
  A plenum baffle between the pairs blocks short-circuiting. Side apertures sit in the
  crown's rain-shadow — verify on the assembled outdoor stack.
- **NO mounting holes exist on the board** (the old "pegs into Ø3.2" was wrong): retention =
  **bottom pocket (tilt-in) + back ribs + top skewer bar** through side-wall mortises.
  Optional hard-mount: 2× M2.5 through the board's Ø2.4 pass-throughs into the can bottom.
- Plus grew 92→96 tall: the board top used to poke into the crown-spigot zone.
- The chimney air from the Basic rises in the slot **behind** the board (board = the baffle,
  F-04). Plus has no gyroid windows; the crown/cap exhausts the column.
- Assembly: tilt board bottom into the pocket → swing top back against the ribs → slide the
  HM bar through the side mortises in front of the board's clear top strip → done. Grove
  cable exits down through the floor gap.

## Variants (verified stacks)

| Variant | Stack | Height |
|---|---|---|
| **Indoor Basic** | Basic + cap | ~80 mm (compact) |
| **Outdoor Basic** | Basic + crown | ~100 mm |
| **Indoor Plus** | Basic + Plus + cap | ~115 mm |
| **Outdoor Plus** | Basic + Plus + crown | ~201 mm (slender meru tower) |

Renders: `review/v12_plus_preview.png`, `review/v12_fit_*_preview.png`, stack previews.

## FIRST PRINT — the rim fit sections (sliced, ready)

| File | Time | PETG | Note |
|---|---|---|---|
| `v12_fit_section_socket.bgcode` | ~17 min | 5.1 g | print as-is |
| `v12_fit_section_spigot_FLIPPED.bgcode` | ~15 min | 4.3 g | already rotated 180° (spigot up); 0 support material |

Sliced 0.15mm SPEED @COREONE HF0.4, Generic PETG. **Test: press the spigot into the socket.**
Firm hand press, no rattle, survives 10 join/separate cycles → STACK=0.15 confirmed, full
modules unlock. Binds → +0.05; rattles → −0.05; regenerate both scripts.

## Airflow

Base intake (Basic bottom grille) → rises up the open central cavity (behind the Plus board)
→ exhausts under the crown eaves (outdoor) or the cap vents (indoor). The Plus PM bay is its
own fan-driven system: side intake low, side exhaust high (or the reverse — symmetric),
isolated from the climate column by the board + bottom pocket.

## Open items / next

1. **Print + verify the fit sections** — gates everything.
2. **Gyroid into Basic side/front windows** (cap technique proven; Plus no longer has windows).
3. **Inter-module cabling** — Grove connector clearance through the spigot pass-through;
   strain relief at each interface.
4. **Stack security** — press-fit chosen; if outdoor handling loosens it, add a quarter-turn
   detent to the keyed rim (validated on a section print).
5. **Hardware BOM + footprint guides** (ICD OPEN-12/13) — wall screws, mesh/membrane seats,
   debossed board outlines.
6. **Proportion** — outdoor Plus now ~201 mm. Tune tier/module heights if it reads too slender.
7. **Insect mesh seats on the Plus side apertures** (aperture ≤1.2mm rule, F-0x) — pair with
   the mesh hardware workstream.
