# v6 — shared-platform enclosure (Basic + Plus)

One parametric generator (`tools/enclosure_v6.py`) builds both variants of the
Making Sense Bali DIY node. Research-grounded (`../DESIGN_RESEARCH.md`), built to
the `outdoor-sensor-enclosure` skill. Function-first; no styling.

**Shared platform.** Both variants share the brain mount, the BME680 radiation-
shield bay, the hood + drip-lip, the venting strategy and the bottom bayonet cap.
**Plus is the Core grown deeper** — a front bay for the vertical HM3301 with its
own down-duct — *not* a module stacked below (stacking the 80 mm carrier under the
102 mm Core would exceed the 140 mm height limit). Putting the HM3301 in a front
bay keeps Plus in the same height class and physically separates the particulate
air path from the temp/RH path.

| | Basic | Plus |
|---|---|---|
| Holds | XIAO ESP32-S3 + BME680 (40×60 perfboard) | + Grove HM3301 |
| Body | 56 × 45 × 102 mm | 56 × 55 × 112 mm |
| Body print | 50.8 g / 2h17m | 65.3 g / 2h48m |
| Cap print | 5.9 g / 17m | 6.9 g / 18m |
| Supports | 0 | 0 |
| Watertight / interference | yes / 0.000 cm³ | yes / 0.000 cm³ |

## Four fundamentals → how, and the rule it implements

- **Self-heat / radiation.** BME680 sits LOW in a **down-louvered, foil-lined bay**
  (front on Basic, a side bay on Plus so it's clear of the HM3301), with the XIAO
  HIGH so the chimney carries MCU heat up and away; plan a firmware T-offset.
  Implements DESIGN_RESEARCH rules 3–6 (buried sensors read +2.7…+5.3 °C; shield +
  isolate + reflective liner, since filament is IR-transparent).
- **Airflow.** Passive chimney: cool ambient in the low louvers past the BME680,
  warm air out the high side louvers under the hood eave (rule 1, 7).
- **Water.** No opening faces up; down-facing louvers; hood with a **13–19 mm
  drip-lip curl**; **2.5 mm weep** at the low point; **ePTFE membrane boss** on the
  leeward wall; the body is **not sealed airtight** (rules 9–14).
- **Particulate (Plus).** HM3301 on a **dedicated down-facing duct**, intake at the
  front-bottom wall, can grille on the front, kept separate from the BME680 bay and
  the MCU; correct PM against the shielded ambient RH in the dashboard (rules 7–8).

Validated internals reused verbatim: perfboard back-wall standoffs, keyholes
behind the board, HM3301 front C-rails + 2 registration pegs, bottom bayonet cap
centred on the cavity.

## Honest status — first pass

- **Fits are all `COUPON_TBD_*`.** Print the calibration coupons (`../coupons/`),
  measure, fill ICD §5.1, then lock fits. Nothing fit-critical prints before that.
- **The BME680 "shield" is a louvered, foil-lined bay + vertical isolation** —
  workshop-grade. The research-grade upgrade is a full **stacked-disc shield pod**
  (5–7 discs) or **micro-aspiration** (25–80 mA); add if a co-location shows the
  T/RH bias is too high.
- **Unproven in plastic:** louver water-shedding, the bayonet fit, the PM-duct
  separation. Section-print the BME680 louver band + the bayonet + (Plus) the PM
  duct; then a hose test on a printed body before trusting the water path.
- **User-added:** reflective foil tape in the BME680 bay; a removable stainless
  mesh cartridge (0.4–0.6 mm) over the louvers/duct; the ePTFE vent; conformal
  coat on the PCB.

## Next
1. Print coupons → measure → fill ICD §5.1 → lock fits.
2. Section-print: BME680 louver band, bayonet ring, PM duct (Plus).
3. Print one Basic + one Plus; hang; **hose test**; rehearse board loading + service.
4. Co-locate against an SCK; if T/RH bias is too high, fit the stacked-disc shield pod.
