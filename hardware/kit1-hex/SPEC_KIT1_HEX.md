# SPEC — Making Sense Bali · KIT 1 HEX ("basalt hood")
Version: K1H-1.0-DRAFT · 2026-07-24 · sibling of kit1-enclosure (planet/Boston),
NOT a v4 of it. Same electronics, different mission: outdoor Bali master,
wall/pole-mountable, external SMA whip. Toolchain + verified component data
inherited from kit1 SPEC + diy-node ICD. No geometry inherited.

## 1. Mission
Outdoor-capable (Bali monsoon) two-part enclosure: shallow mounting BASE +
deep faceted HOOD. Plan geometry lives on the Fab City hex grid (all wall
directions ∈ {0°,60°,120°}), poly-faceted everywhere, no mirror symmetry,
no soft surfaces (chamfers, not fillets). Zero-hardware closure. One SMA
bulkhead (bought, declared) + insect mesh scrap (bought, declared).

## 2. Components (verified 2026-06-11 Eagle parse + 2026-07-23 physical)
| Part | Envelope | Mount |
|---|---|---|
| Grove Shield for XIAO | 25×58×1.6 | floor rails 25.0+0.30/side + end stops + top clips |
| XIAO ESP32S3 + Wio-SX1262 stack | 21×17.8 fp; 25 headroom reserved over shield | socketed |
| HM3301 | board 80×40×1.6; can 40×38×15, X−25.39..+14.61, Y−18.79..+19.21 (board-ctr); J2 Grove exits −X; NO mount holes | rails + edge capture, tool-free |
| HM3301 air ports | intake = 40×15 slot, can SIDE Y-face (which side = TBC-01 → mirror-capable plenum); exhaust = fan grille, can TOP. Physically confirmed | — |
| Grove BME680 | 20×40×1.6, Grove conn one short end | corner rails, ≥25 from stack |
| Grove cables ×2 (~20 cm) | plug ~10×8×5 | printed open hooks |
| LoRa: U.FL→SMA pigtail + whip 13×195 | SMA bulkhead Ø6.35 barrel + nut | reinforced boss in hood high facet |
| USB-C + power switch (shield/XIAO end) | service only | oval port in base wall, printed press-in bung |

## 3. Form (the numbers)
- Footprint: irregular hex-grid heptagon, ~148×102 external, drawn on a=8 hex
  lattice; no edge pair parallel-equal → no mirror axis. Walls plumb (draft 1°).
- BASE: floor 2.5 + wall h34, t2.5. Countersunk ×4 M4 (Ø4.5/Ø9.5×90°) wall/pole
  mount bosses on hex nodes, asymmetric; 2 weep Ø2.5 at true low corners;
  elephant-foot chamfer 0.4×45° all bed edges.
- HOOD: skirt overlaps base wall outside, drop to z24 (10 overlap), drip edge =
  sharp lip + 1.5 groove. Roof = asymmetric faceted peak, apex ~z92 offset over
  the stack/SMA corner; every roof facet 45–62° from horizontal (self-supporting
  rim-down AND monsoon-shedding); no flat top anywhere.
- Seam: labyrinth — tongue on base rim 1.6, +0.25/side, engage 4; groove opens
  DOWN on hood. Z-seams → designated arris gutters, off weather faces.
- All ports in BASE wall, under the 10 mm skirt shadow, louvres face down ≤45°.

## 4. Zones (never share air)
- **PM**: HM3301 flat on floor rails, can toward wall az~240 zone. Intake:
  full-face plenum docks the 40×15 slot face → mesh rebate + retainer →
  down-louvred base port (mirror-capable for TBC-01). Exhaust: printed hood
  over can-top grille → adjacent-face gill slots, ≥40 exterior path + one arris
  between in/out. Plenums sealed from electronics zone, slope ≥3° out, weep each.
- **Climate**: BME680 in the far corner bay (≥60 from stack), behind two
  down-louvred facets on adjacent walls (cross-vent), 6 air gap, foil liner +
  2–3 gap note (IR). Not downstream of PM exhaust (opposite wall group).
- **Electronics**: shield rails under the peak; USB oval + switch reach through
  base wall az~30, bung'd. SMA boss in hood facet above, wall 4.0 local, bore
  Ø6.35+0.3 teardrop, flat for nut, pigtail hook path to stack. Passive stack
  vent: high gill pair under peak eave (down-facing) for LoRa TX heat.
- Desiccant: printed clip pocket 30×20×12 on base floor, electronics side.

## 5. Closure (zero hardware)
3× cantilever hooks at HOOD rim (print in XY at bed, rim-down): L 12, t 1.2,
taper 0.5×, root fillet 0.6, lead-in 25°/return 40°, engage base wall windows
w 6; release = press-slots hidden under skirt. Clearance 0.45 =
COUPON_TBD_SNAP. Asymmetric spacing (one per non-adjacent wall) = keying:
hood only seats one way.

## 6. Print (fail-closed gate)
Prusa CORE One HF0.4, PETG, "0.15mm SPEED @COREONE HF0.4". BASE prints open-up
(floor on bed); HOOD prints rim-down. Both ≤ bed 256². Per part: orientation
declared; overhang map ≥45°-from-vertical rule everywhere or named designed
fix; bridges ≤5 until coupon; no islands; `;TYPE:Support` grep -ac == 0.
Fits carried from diy-node §5.1: rails 0.30 · slide 0.25/side · free 0.40 ·
vert hole +0.2Ø · horiz hole +0.3Ø teardrop. Est. mass: base ~85 g, hood ~120 g.

## 7. CMF
Matte white PETG body (T/RH truth in sun) + ONE accent facet = PM intake scoop
(FC hue). Fuzzy skin body option, smooth mating faces. No text.

## 8. Open
- TBC-01 which can Y-face carries intake slot (carried from kit1; mirror-capable).
- COUPON_TBD_SNAP 0.45 · grommet/bung fit · rail 0.30 re-verify on new printer roll.
- OPEN: exact stack height over shield (25 reserved, kit1 carry).
