# K1H3 "meru" — Print Plan (v4 FEATURED, 2026-07-25)

**v4 (iter-4, Tomas):** dome rebuilt TANGENT-CONTINUOUS (Hermite cap: joint slope
matches the facets, crown ends horizontal — no more "cap on a pyramid"; top z110).
Grille gains a **29×10 stadium cable aperture** (Grove + USB plugs pass pre-connected)
and a **4-slot shield tie field** (a 58×25 board can zip-tie to the grille too).
**Wall mount built on the straight e3 band:** 2 printed keyholes (Ø8.8 entry, 4.6
slot, hollow blister head cavity, gabled/teardropped for print) + 2 zip-tie conduit
pairs. Plus the Phase-2 set: apex gill fields e0+e2 (331 mm² ≥300, 45° down-out),
USB window square to the plug axis (gabled, drip fin roof above; bung P2b), SMA boss
on e5 mid-facet (Ø15 pad, 45° wedge, teardrop Ø6.65 bore, whip 40° up-out), 4 grille
support columns (facet-flush) + 2 retention nib wedges (COUPON), deck spigot keys.

| Part | Orientation | Watertight | ;TYPE:Support | g | Time |
|---|---|---|---|---|---|
| shell (featured) | rim-down | yes | **0** | 56.3 | 2h34 |
| grille | floor-down | yes | **0** | 21.2 | 1h19 |
| deck | plate-down | yes | **0** | 9.2 | 0h21 |

**Total ≈ 86.7 g / ≈ 4h15** (K1H2: 112 g/4h26). Interference all-pairs 0.000 (mesh
boolean, manifold); 12/12 component keep-outs 0.000. Coupon list: nib engagement,
keyhole slot on M4 head, SMA nut torque, dome inner-crown bridge, deck spigot fit.

---
# (v3 notes below)


Outdoor LoRa+WiFi air-quality node, Fab City hex facet system, Bali monsoon.
Irregular **hex pyramid with a rounded (domed) apex**, open bottom, three parts:
shell + **recessed perforated grille** (internal sensor mount) + deck (main board).
Zero hardware in the enclosure. Source `tools/k1h3_model.py` (build123d) → `v3/`.

**STATUS: revised massing — Tomas iter-3 changes in (rounded apex; grille recessed
≥ PM height, sensors hang below). All gates pass. Phase-2 features next.**

## Architecture (iter-3)
- **Shell** — irregular hex pyramid, apex offset E over the stack, **top domed/blunted
  at z115** (was a sharp z129 point); every facet ≥47°; open bottom; plumb rim band
  z0–20 = the protective **skirt**.
- **Grille** — perforated hex plate **recessed ~20 mm up inside** the pyramid (its
  underside at z20, ≥ the HM3301's ~18 mm height). The **sensors zip-tie to it and
  hang below into the skirt**: PM can-top (fan) against the grille → exhaust rises
  through the perforations into the chimney; PM/BME intakes face down into the
  skirt-shaded open bottom. Two short walls rise from the grille (z23→44) to carry
  the deck. This one part replaces the old tray-cradle **and** the separate base.
- **Deck** — flat plate high (z41–44) on the grille wall-tops; shield rails + 2 N-row
  plug notches + chimney vents + WiFi tab. Main board (shield+LoRa stack) on top.

## Gate table (CORE One HF0.4, PETG, 0.15 SPEED, support_material ON = hardest gate)

| Part | Orientation (bed face) | Watertight | ;TYPE:Support | g | Time |
|---|---|---|---|---|---|
| shell | rim-down (domed apex up) | yes | **0** | 54.5 | 2h16 |
| grille | floor-down (walls up) | yes | **0** | 22.9 | 1h23 |
| deck | plate-down (rails up) | yes | **0** | 9.2 | 0h21 |

**Total ≈ 86.6 g / ≈ 4h00** — now **below K1H2 (112 g)** and far below v0.8 (132 g).
The rounded/shorter apex (shell 76.5→54.5 g) and folding base+tray into one grille
did it. Assembled interference = 0.000 mm³ (all 3 part-pairs); 12/12 component
keep-outs = 0.000 (shield, stack 24 mm reserve, 2× N-plug corridor, USB, HM
board+can+intake, BME, foil, WiFi landing, stack headroom).

## Per-part print notes
- **shell** — support-free by form: facets ≥47°, plumb rim skirt, domed apex prints
  like a sphere-cap top (slicer 0 support; the small inner apex ring bridges — confirm
  on the coupon). Drip groove = 1 mm bridge. Elephant-foot 0.4×45° on the rim.
- **grille** — floor on the bed, hex holes point-up (60° self-supporting), walls + rim
  tabs vertical, zip-tie slots are through-holes. Support-free.
- **deck** — flat plate, everything stands up off it; plug openings are the rail
  notches. Zero bridges. (This split is why the electronics carrier prints clean.)

## Assembly (tool-free)
1. Zip-tie HM3301 under the grille (can-top to the grille underside, fan up through
   the perforations); zip-tie BME680 under the grille in the S strip at the HM intake
   (reads inlet RH). Both hang into the skirt.
2. Deck onto the grille wall-tops; shield stack onto the deck rails; 2 Grove plugs
   fly N over the N wall through the rail notches.
3. Grille+deck assembly drops UP into the shell; rim tabs snap at z~20 (P2 detail).
4. USB/switch via the e1 pocket; SMA whip out the e5 boss; WiFi antenna on the deck
   tab (all P2). Service: the whole electronics tree drops out the bottom on the grille.

## Declarations (iter-3)
- PM path: cavity/skirt-sampling (open bottom ≈ ambient); exhaust rises to the apex,
  decoupled from the down-facing intake. RH-correct PM in the dashboard.
- F2: BME hangs ~26 mm **below** the stack (heat rises away) + reflector + white body
  + firmware T-offset. Reads the PM inlet air (correct per the domain rule).
- Grille fixing (rim tabs → shell catch) and all snaps are Phase-2 + COUPON.
- Domed-apex inner ceiling: prints as a sphere-cap; slicer 0 support; coupon-verify.

## Phase-2 queue (next)
Apex gills (F1 exhaust ≥300 mm²), e1 USB pocket + bung (D-3), e5 SMA boss + teardrop
bore, grille↔shell + deck↔grille keyed snaps, drip-lip refinement, zip-tie boss
fillets, CMF (grille = the one FC-hue accent). Then the coupon/section-print night.

*Change log: K1H3-P1 v1 (tray+deck+base, sharp apex) → v3 2026-07-25 (rounded apex;
grille recessed, sensors hang; base+tray merged). All gates pass at each step.*
