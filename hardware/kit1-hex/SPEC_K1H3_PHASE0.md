# PHASE 0 — K1H3 "meru" — Ground Truth + 4-Fundamental Spec
## Air Quality Node, Open-Bottom Irregular Hex Pyramid (Fab City Hex Facet System, Bali Outdoor)

Version: K1H3-P0-DRAFT · 2026-07-24 · status: **Phase 1 massing built + gated same session — amendments A-1..A-7 await ratification at the massing checkpoint**

**Sign-off decisions (Tomas, 2026-07-24, this session):**
- **D-4 Pyramid rebuild.** Clean-sheet K1H3; shape = irregular pyramid, sides need NOT be equal. **Irregular hex pyramid** chosen (6 triangular facets on the {0,60,120} axes, apex offset, no symmetry) — stays inside the FC hex system per D-1.
- **D-5 Drop-in carrier.** Boards live on one printed chassis that clicks up into the shell: **main board (shield+stack) on the carrier's top deck, sensors (HM3301, BME680) in the lower part.** Whole electronics tree drops out in one hand.
- **D-6 Open bottom; base removable AND optional.** The pyramid protects everything from above; a perforated base plate (hex-cell grille + insect mesh) closes the underside when wanted.
- **D-7 Height: form decides** (old z≤100 envelope note waived; flag the number at checkpoint).

Relationship: successor candidate to K1H2 "low boulder" (SPEC_K1H2_PHASE0.md, signed 2026-07-24). All K1H2 §1 ground truth (Grove Shield v1.2 no-holes, XIAO+SX1262 stack 19.5–20 + 25 reserve, HM3301 slot/fan geometry, BME680, SMA whip, printer truth §1.6 fits) **carries unchanged by reference.** TBC-01/02/03 carry open.

---

## 1. Architecture — what the pyramid changes

One monocoque shell, open at the bottom. The shelter works like a Stevenson screen with a chimney: ambient air enters the open underside, the HM3301's fan and the stack's heat drive it up the narrowing volume, out apex gills. Rain never sees an upward-facing aperture because there are none — every surface is a ≥47° facet or a downward mouth in its rain shadow.

| Part | Role | Attach |
|---|---|---|
| **shell** | irregular hex pyramid, plumb rim band z0–10, facets →apex; SMA boss (e5), apex gills (e0+e2), USB pocket (e1), keyholes+zips (e3) | mounts to wall/pole |
| **carrier** | ring + flared basket + top deck: shield rails on deck, stack rising under apex; HM3301 rails at ring level; BME680 cradle low-W; foil shade card; WiFi landing | ring seats in rim, keyed snaps (P2) |
| **base** (OPTIONAL) | perforated plate: hex cells Ø5/1.7 webs + mesh rebate + retainers; recessed 5 up into the rim's rain shadow | 3 keyed snap arms into rim pockets |

Service story: bung out = USB/switch (D-3, via e1 pocket). Base off = 3 snaps. Carrier out = boards on the bench, nothing unscrewed. Zero hardware throughout.

## 2. The four fundamentals — how they map + AMENDMENTS TO RATIFY

**F1 airflow — A-1:** the chimney is now the whole shelter. Intake = open bottom (unthrottleable); exhaust = apex gill pairs on e0+e2, 45° down-out, **total ≥300 mm²** (sized to the HM fan, not to the old intake ratio — the ratio rule is unsatisfiable and unnecessary with an open floor). The PM fan actively drives the stack's chimney. *Amends the intake/exhaust ratio wording.*

**F2 self-heat — A-2:** the pyramid IS the radiation shield. Louvre panels deleted; BME680 sits low, outboard W, in near-free shaded air, **below the stack for the first time — heat rises away from it** (strictly better than any K1H2 layout). Kept: **foil shade card + 2–3 mm gap** above the BME (PETG is IR-transparent), matte white body, firmware T-offset trim, ratified 46/65 rule (**built: module 51 mm from socket keep-out, sensing element ~70**), foil ≥15 from WiFi landing (built: >55).

**F3 water — A-3:** there is **no weather seam anywhere** — the only openings are the open bottom (in total rain shadow), down-out gills, and the e1 USB pocket (45° ceiling + drip fin, K1H2 recipe). Therefore: labyrinth tongue/groove **deleted**; weeps **deleted** (no floors to pool); desiccant **deleted** (no closed zone — the box is all breathing). Kept: rim drip lip + 1.0×1.2 groove, 0.4×45° bed chamfers, all facets ≥47°, no flat top (apex is a point), Z-seam in the e3 arris.

**F4 particulates — A-4:** plenum, drop-in baffle, transfer windows, sealed E-chamber — **all deleted.** The HM3301 samples the shelter cavity, which ≈ ambient because the floor is open; its exhaust plume rises with the chimney and leaves at the apex, ≥80 mm above and geometrically decoupled from the intake — no recirculation loop exists. Declared honestly: (a) cavity-sampling, not a docked duct; (b) the deck overhangs part of the can top with a 6.4 mm gap — plume exits via ≥500 mm² side gaps (≫ fan area); (c) with the base OFF, the HM intake is insect-exposed → **base-on is the deployed configuration; base-off is supervised/bench mode.** RH-correct PM in the dashboard (standing rule).

**D-3 USB — A-5 (a win):** K1H2 never had a hex-legal wall square to the plug. The pyramid does: facet e1 stands at **84.9°** — a recessed pocket there is nearly a vertical-wall port. Pocket + press bung carry over (P2); axis z59.4, keep-out gated at 0.000 in massing.

**D-2 mount — A-6:** keyholes ×2 on e3 (68.6° — node tips 21° into the wall, keyholes load correctly) + zip conduit pairs through the plumb rim band. Unchanged in spirit.

**Mesh — A-7:** one mesh field in the base grille replaces K1H2's three. Retainer count → checkpoint.

## 3. Geometry (built, Phase 1)

Plan = K1H2's proven packing hex: edges **72/57/48/88/41/64**, ext 132.5 × 90.9. **Apex (84, 45)** — directly over the stack, so headroom peaks exactly where the 25 mm reserve needs it and the form leans E: function authoring form. Apex z = spring 10 + tan 47° · d(apex→e5 edge line) ⇒ **z ≈ 122**. Facet slopes: e5 **47.0°** (governs), e4 ~49°, e0 ~68°, e3 ~69°, e1 ~85°, e2 ~83° — all ≥47, all ≤45° from vertical, shell prints rim-down support-free by construction.

Placements (carrier coords = shell coords): shield 58×25 @ x34–92, y32–57, board z44–45.6; stack keep-out x69–93, y34–56, z→70.6 (25 reserve ✓); Grove plugs both N-row, corridor y57–70 × z43–53 (13 mm insertion ✓); USB axis (92, 44.5, 59.4) → e1 pocket; HM3301 board x2–82, y28–68, z18–19.6, can top z34.6, intake standoff keep-outs BOTH Y-sides ≥10 (TBC-01 mirror-capable, beats the ≥5 rule); BME680 x−8–32, y6–26, z10–17, connector E; foil card z~30 above it; WiFi landing 30×10 on carrier E wall inner face; SMA boss on e5 at z~70, whip ~40–43° up-out, pigtail run <100 mm.

## 4. Deletions ledger (economy, D-1)

Gone vs K1H2: tongue/groove seam · 3 skirt snap arms→(carrier ring + base arms instead) · plenum walls · baffle · transfer windows · E exhaust chamber · exhaust grille+mesh+retainer · intake facet grille+mesh+retainer (mesh consolidates to base) · louvre panel field · desiccant tray+sachet · weeps · cable grommet (USB cable drip-loops out the open bottom if mains-powered). Parts: **7 → 3 main + bung + retainers.**

## 5. Open / TBC
| ID | Item | Blocking? |
|---|---|---|
| TBC-01/02/03 | carried from K1H2 (HM slot side / shield rev photo / WiFi antenna dims) | No |
| TBC-04 | carrier ring snap arm count + COUPON (reuse COUPON_TBD_SNAP 0.45?) | Gates print, not CAD |
| TBC-05 | gill field final area vs HM fan (measure fan free-air draw at coupon night) | No |
| A-1..A-7 | amendments above | **Ratify at checkpoint** |

## 7. Iter-3 amendments (Tomas, 2026-07-25) — IN, gates pass
- **D-8 Rounded apex.** Sharp z129 point → cosine dome, blunted, top at **z115** (shorter OK per Tomas). Prints rim-down like a sphere-cap; slicer 0 support.
- **D-9 Grille = recessed internal sensor mount.** The perforated base moves UP inside the pyramid by **≥ the PM-sensor height (~18 mm; grille underside z20)**. Sensors **zip-tie to the grille and hang below into the skirt** (PM can-top→fan up through the perforations; intakes face down into the shaded open bottom). This **folds the old tray-cradle AND the separate base into one grille part** — the complexity cut Tomas asked for. Shield stays high on the deck.
- **Economy result:** shell 54.5 g + grille 22.9 g + deck 9.2 g = **86.6 g / ~4h00 — beats K1H2's 112 g** (D-1 satisfied).
- **F2 update:** BME hangs ~26 mm below the stack (vertical separation; heat rises away) and reads the PM inlet air (domain-correct). A-2 stands, horizontal-gap rule retired in favour of vertical separation.

*Change log: K1H3-P0-DRAFT 2026-07-24 — pyramid clean sheet per Tomas (D-4..D-7); Phase-1 massing same session. Iter-3 2026-07-25 (D-8 rounded apex, D-9 recessed grille/hanging sensors); base+tray merged; all gates pass.*
