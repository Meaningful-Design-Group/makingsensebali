# SPEC — Making Sense Bali · KIT 1 enclosure ("faceted lantern")
Version: K1-1.0-DRAFT · 2026-07-23 · fresh start, no geometry inherited from diy-node.
Toolchain inherited: MDG/.cad-venv (build123d 0.10.0), tools/run_model.py, PrusaSlicer 2.9.6 CLI.

## 1. Mission
Hangable / wall-mountable / tabletop poly-faceted sphere ~Ø150 for KIT 1
(Wio-SX1262+XIAO ESP32S3 + Grove Shield + HM3301 + Grove BME680).
First deploy: Boston, semi-sheltered (balcony/eaves/canopy), warm summer.
6+ units → print time is a design driver. Shell parametric so KIT 1+ (screen
facet) and KIT 2 (other boards) reuse it.

## 2. Components (verified)
| Part | Envelope | Source | Mount |
|---|---|---|---|
| Grove Shield for XIAO (103020312) | 25×58×1.6 (breakable 25×39.5) | Seeed wiki | edge rails, param length |
| XIAO ESP32S3 + Wio-SX1262 (B2B) | 21×17.8 fp; stack headroom 25 res. | Seeed wiki 102010611 | socketed on shield |
| USB-C on XIAO | cable jacket Ø4.5 (Tomas) | — | facet grommet, lower half |
| HM3301 module | board 80.0×40.0×1.6; can 40×38×15 at X−25.39..+14.61, Y−18.79..+19.21 (board ctr origin); Grove J2 exits −X short edge; NO mount holes; 2×Ø2.4 pass-throughs (−23.62,−17.02)/(+12.57,+17.14) | Eagle .brd parsed 2026-06-11 (diy-node ICD) | rails + edge capture |
| HM3301 air ports | intake = rect slot on can SIDE face (a 40×15 Y-face); exhaust = fan grille on can TOP. Perpendicular, ~90°. CONFIRMED PHYSICALLY by Tomas — supersedes ICD "both on one face". Which Y-side / slot XY = TBC-01 → plenums span full faces, mirror-capable | Tomas, physical part | — |
| Grove BME680 (101020513) | 20×40×1.6, Grove conn one short end | Seeed wiki | edge clip on cantilever arm |
| Grove cables ×2 | plug ~10×8×5, hand-pluggable | — | open hooks on tray |
| LoRa antenna | U.FL pigtail + whip/FPC; PETG RF-transparent 868/915 | kit contents | clip channel in spire |
| Insect mesh (bought) | aperture ≤1.2, user-cut scrap | — | rebate + snap retainer at intake |

## 3. Form & architecture (the numbers)
Revolve-profile polyhedron, N=10 gon, triangulated bands (alt rings offset 18°).
Vertex rings (r@z, sphere R75 belt):  base r40@−66 · r53@−53 · r71.7@−22 ·
**r75@0 = SPLIT** · r71.7@+22 · r53@+53 · r20@+90 · r6@+104 loop base.
- Bottom: flat base 10-gon Ø80, 3 feet pads h2; 45° chamfer skirt −66→−53. SIT ✓
- Top: faceted 45°-max spire = antenna radome + hang loop + rain hat. HANG ✓
  (Deviation from pure ball: a closed faceted dome apex cannot print support-free;
  poles become functional caps — flag at checkpoint.)
- Wall: 2 keyholes, lower-equatorial facets az 0°±36°. WALL ✓
- Wall thickness 2.5. No flat top anywhere. Z-seam → wall-side facet edge.

## 4. Zones (never share air)
- **PM**: HM3301 flat on tray, board ctr ~(0,−14,−44), can slot face → −Y.
  Intake: sealed plenum on tray, full 40×15 slot face → mouth docks over collar
  at lower-belt facet az 252° (faces down-out ~31° = under-eave). Mesh rebate +
  printed retainer at mouth. Exhaust: tray hood over full can top → adjacent
  facet az 288°, hooded, down-facing. Divider = sealed separate plenums inside;
  ≥40 mm + facet arris between ports outside. Weep Ø2.5 at each plenum low pt;
  ducts slope out ≥3° (self-draining). Optional 3mm foam strip note (not req'd).
- **Climate**: BME680 on 40 mm cantilever arm from tray, behind perforated facet
  az 144° lower-belt, 6 mm air gap, foil liner + 2–3 mm gap note (IR). Thermally
  away from XIAO (arm length + below electronics deck).
- **Electronics**: shield on rails z−36, XIAO USB-C → az 72°. Grommet: split-ring
  PETG plug, grips Ø4.3 (COUPON_TBD_GROMMET), teardrop facet bore Ø6.7, drip
  loop outside, entry z≈−10 (lower half → dome twists off with cable connected).
- **Convection**: perforated facets = diamond holes 4.5, web 2 (self-supporting
  any orientation). Low grids az144 (BME) + az216; exhaust = gill slots under
  spire-base eave ring (down-facing, rain-shadowed). Not airtight by design.

## 5. Split & closure (zero hardware)
Plane z=0. Lower: upstand tongue ring r66, h6, t1.6 + 4 radial-out lugs.
Upper: skirt overlaps outside (shingle), groove opens DOWN, land at z0;
internal ring wall with 4 L-slots + end detent bump. Quarter-turn ≈ 20°.
Radial clearance 0.45 = COUPON_TBD_BAYONET. Seal behind lip = labyrinth
(tongue 1.6, 0.25/side, engage 4) — sheds, doesn't seal airtight.

## 6. Tray (prints flat)
Ø~100 deck plate, 3 asym radial keys → bowl floor sockets (one orientation,
lift-out). Carries: HM bay rails+edge capture+both plenums; shield rails
(25.0+0.3×2, length stop 58/39.5 param); BME arm + edge clip; Grove cable
hooks; antenna pigtail route; finger lift tabs. Clearance to shell ≥1.5.

## 7. Print constraints (fail-closed gate)
Prusa CORE One, HF0.4, PETG. Profiles: printer "Prusa CORE One HF0.4 nozzle",
print "0.15mm SPEED @COREONE HF0.4", filament "Generic PETG @COREONE HF0.4".
Per part: orientation declared; overhang map ≥45° from vertical everywhere or
named designed fix; bridges ≤5 until coupon; no islands; slicer
`;TYPE:Support` grep -ac == 0 (binary gcode, use grep -a). No plan, no print.
Orientations: lower = base-down · upper = rim-down (spire up) · tray = flat ·
grommet+retainer = flat. All ≤ bed 256².
Fits carried (inferred ±0.1, diy-node §5.1): slide 0.25/side · free 0.40 ·
rails 0.30 · vert hole +0.2Ø · horiz hole +0.3Ø teardrop · elephant-foot
0.4×45° chamfer all bed edges · max design overhang 45° from vertical.

## 8. CMF
Matte white PETG body (reflects sun, helps T/RH truth) + ONE accent facet
(FC hue) = the PM intake scoop facet. Fuzzy-skin option body-only. No text.

## 9. Open
- TBC-01 which Y-face of the can carries the intake slot + slot XY (Tomas,
  physical part) — plenums designed full-face + mirrorable, so non-blocking.
- COUPON_TBD_BAYONET / _GROMMET / rail fits → coupon prints before batch.
- OPEN: exact Wio-SX1262 stack height over shield (25 reserved).

| K1-1.0 | 2026-07-23 | v1 BUILT+GATED: 5 parts watertight, interference 0, shipping slice ;TYPE:Support=0 (ASCII-verified w/ controls), overhang audit clean except DB-1 (spire-tip 9.8mm internal designed bridge, coupon). Form: ball->faceted teardrop (print physics: poles become functional caps). Exhaust gills az342 x2 (az324 facet too narrow low). Feet dropped (flat base + weep). BOSS pins (30/85/130). USB boss pad deleted (corbel = native boss). |
