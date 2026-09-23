# Outdoor AQ-sensor enclosure design — research brief (2026-06)

Deep survey of 22 real enclosure designs + the underlying engineering, to ground
a *function-first* enclosure for the Making Sense Bali DIY node (Seeed XIAO ESP32
+ Bosch BME680 + Cubic HM3301, wall-mounted under eaves, PETG, Prusa CORE One).
Every claim is cited to a primary source. This is the evidence base; the
methodology distilled from it lives in the `enclosure-design` skill.

---

## The four problems every outdoor AQ enclosure must solve

1. **Sensor airflow** — get true ambient air to the sensors without a wind tunnel.
2. **Self-heat / radiation** — keep electronics heat *and* sunlight off the T/RH sensor.
3. **Water + humidity** — exclude liquid rain, but *don't* seal (sealed = condensation trap in the tropics).
4. **Particulate path** — give the fan-driven PM sensor its own clean, separated airflow.

The single most important finding: **#2 is the one hobby builds get wrong, and it dominates accuracy.** Buried T/RH sensors read **+2.7 to +5.3 °C hot, RMSE 2.8 °C**, which throws RH **−9.7 to −24.3 %** ([PurpleAir T/RH evaluation, *Atmosphere* 2024](https://www.mdpi.com/2073-4433/15/4/415)). AirGradient's own correction proves it's an enclosure artifact, not the sensor: their outdoor unit needs `T×1.181−5.113` / `RH×1.259+7.34`, their indoor unit needs *none* "because it has a different ventilation design" ([AirGradient calibration algorithms](https://www.airgradient.com/documentation/calibration-algorithms/)).

---

## Survey A — DIY / open-source (6)

| Design | Airflow / self-heat | Water | Print / parts | Source |
|---|---|---|---|---|
| **AirGradient Open Air** | T/RH read *inside* the PM module, openly "may deviate from ambient… require correction"; dual PMS cross-mounted so fans pull from opposite edges | downward designer-tuned vents, no separate hood; ASA | 3 parts (2 base + big top), 4× M1.8 Torx; STL/STEP free | [build](https://www.airgradient.com/documentation/diy-open-air-presoldered-v11), [outdoor](https://www.airgradient.com/outdoor/) |
| **AirGradient DIY Outdoor** | **snap-on external temp probe** to move T/RH out of the warm cavity; PM fan faces the enclosure edge | downward vents, sealed seams | 3 parts, 4× M1.7 | [DIY outdoor](https://www.airgradient.com/documentation/diy-outdoor) |
| **Smart Citizen SCK2.3** (closest analogue, tropical-tested) | white PETG "to avoid overheating"; PU foam between shells = insulation+seal | layered PETG shells, **2.0 mm seal** (2.5 didn't fit), commercial pressure-relief membrane | PETG **no supports, 0.2 mm, ≥3 perimeters**; ~7 parts; **M4 brass inserts** (printed threads strip) | [SCK2.3](https://enclosures.smartcitizen.me/Air/SCK2.3/SCK2.3_SEN5X/3D_printed_outdoor_sen5x_only/), [Fighting Water II](https://forum.smartcitizen.me/t/fighting-against-water-part-ii-effective-waterproof-3d-printed-enclosures-that-do-the-job/2017/3) |
| **Smart Citizen "frog box" + umbrella** | **separate umbrella radiation shield/rain-hat** over the sealed box — decouples thermal shield from electronics | umbrella sheds sun+rain; box sealed separately | core box + bolt-on shield (Dibond/HDPE) | [SC enclosures](https://enclosures.smartcitizen.me/Air/) |
| **Sensor.Community airRohr** | BME280 at the pipe mouth in the airstream; antenna pointed away — still runs warm/humid (the anti-pattern) | **two stacked DN75 87° elbows** — openings face down, the bend *is* the rain strategy | ~zero print (it's plumbing); mesh over tube ends for insects | [airRohr](https://sensor.community/en/sensors/airrohr/) |
| **Printables PMS5003 (rainb0w_wheez3)** | BME280 in a **separate Stevenson screen**; PM in the box | **slanted roof + ridge** sheds water; caulked cable hole; **19 mm tobacco-filter mesh** over inlets | 3 parts, support-free; self-tapping screw heated to thread | [Printables 39560](https://www.printables.com/model/39560-outdoor-enclosure-for-pms5003-particulate-matter-s) |

## Survey B — commercial (9)

| Design | Key transferable idea | Source |
|---|---|---|
| **PurpleAir PA-II/Flex/Zen** | "hat + recess + open bottom": hood overhang sheds rain, sensors recessed up inside, all openings face down; one-screw captive sled; **open bottom = wasp nests** (mesh!) | [AQ-SPEC](https://www.aqmd.gov/aq-spec/product/purpleair-pa-ii), [hack](https://seetheair.org/2021/01/18/purpleair-ii-pa-ii-hack/) |
| **Clarity Node-S** | **two-zone**: IP67 sealed electronics + IPX3 breathing sensor module — different IP targets, don't seal the whole box | [Node-S](https://www.clarity.io/products/clarity-node-s) |
| **Aeroqual AQS 1** | **standoff double-skin solar shield** over the cabinet (air gap); pumped sampling + **inlet heater dries the sample** to beat high RH | [AQS 1](https://www.aeroqual.com/products/aqs-air-quality-monitor) |
| **QuantAQ MODULAIR** | **bottom intake behind an insect screen**; T/RH "measured in the flow cell, *not* ambient" (honest labeling); all wet I/O on the bottom face | [docs](https://docs.quant-aq.com/hardware/modulair/modulair) |
| **TSI BlueSky** | low PM flow **~0.3 LPM** → small openings, easy to shield; firmware offset for self-heat; IP67 *supply* (wet join at the cable) | [spec](https://www.kenelec.com.au/wp-content/uploads/2023/05/TSI-8143-8145-Bluesky-Air-Quality-Monitor-SpecSheet-revF-2023.pdf) |
| **Vaisala AQT530** | **vertical cylinder topped by a louvered PC radiation shield** for T/RH; single sealed M12 connector; IP65 | [datasheet](https://usermanual.wiki/m/c223d58f46d0e17a055dd1cc2efa9fd4c67141c8ec64284c6941a6cff94de1ce) |
| **Kunak AIR Pro** | **self-identifying plug-in sensor cartridges** (field-swap, no recal); −40…+60 °C, 0–99 % RH | [Kunak](https://kunakair.com/air-quality-monitor/) |
| **Atmotube Pro 2** | states plainly: **airflow and full waterproofing are mutually exclusive** in a small body — under-eaves mounting reconciles them | [Atmotube](https://atmotube.com/atmotube-pro) |
| **Libelium Plug & Sense!** | every penetration is a sealed external screw-in port; sensing as external screw-in probes, not holes into the cavity | [Libelium](https://www.libelium.com/iot-products/plug-sense/) |

## Survey C — radiation shields / T-RH housings (7) — the part I was missing

| Design | Geometry / numbers | Source |
|---|---|---|
| **Stevenson screen** | double-louvered walls + **double roof with air gap**; louvers break every sky/ground sightline; white | [wiki](https://en.wikipedia.org/wiki/Stevenson_screen) |
| **R.M. Young 41003** | stacked **flared discs**, 12 cm Ø × 27 cm; error **0.4 °C @3 m/s, 0.7 @2, 1.5 @1 m/s** (passive fails in low wind) | [datasheet](https://www.fondriest.com/pdf/rm_young_41003_spec.pdf) |
| **Davis 7714** | **6 plates (3 open + 3 closed alternating)**, **13–25 mm gaps** — the only published exact stack geometry | [manual](https://www.manualslib.com/manual/460560/Davis-7714-Radiation-Shield.html) |
| **R.M. Young 43502 aspirated** | triple-wall intake (air turns, no radiative straight path); **<±0.2 °C** | [Campbell](https://www.campbellsci.com/43502) |
| **Apogee TS-100** | low-power aspiration: **80 mA full / 25 mA half @12 V**, Coandă/Venturi inlet, **within 0.03 °C** of reference; passive shields climb steeply <3 m/s | [spec](https://www.apogeeinstruments.com/content/TS-100-spec-sheet.pdf) |
| **BARANI MeteoShield Pro** | **helical double-louver** stack → self-cleaning vortex, ~zero error >1 m/s; flagged as a great **continuous-3D-print** candidate | [BARANI](https://www.baranidesign.com/meteoshield-professional) |
| **DIY flower-pot-saucer shields** | **4–7 middle discs** on M3/M4 rods, ~10–20 mm gaps; **filament is IR-transparent → needs reflective foil liner + air gap**; PLA dies in 30–90 days UV, ASA stable | [Hackaday test](https://hackaday.com/2022/02/04/3d-printed-radiation-shields-get-put-to-the-test/), [Thingiverse 4120452](https://www.thingiverse.com/thing:4120452) |

Modern benchmark: a CFD-optimized "bowl-cover" passive shield hit **0.12 °C mean error vs 0.59 °C for the R.M. Young 41003** — *airflow-guiding geometry beats a plain plate stack* ([MDPI Atmosphere 2026](https://www.mdpi.com/2073-4433/17/3/272)).

---

## The rulebook (prioritized, numeric, cited)

### Architecture
1. **Two zones, two IP targets.** Sealed electronics "brain" (conformal-coat the PCB) + a breathing "sensor" zone. Don't chase one high IP number on a box that must breathe ([Clarity Node-S IP67+IPX3](https://www.clarity.io/products/clarity-node-s); [IEC IP code](https://en.wikipedia.org/wiki/IP_code)). Target **IP54-by-geometry** for the breathing path + an **IP67 ePTFE membrane** on one equalization port.
2. **"Hat + recess."** A solid overhanging hood over recessed, downward-facing openings is the primary rain defense — gaskets are secondary ([PurpleAir](https://www.aqmd.gov/aq-spec/product/purpleair-pa-ii)).

### Temp/RH (the fix I missed)
3. **Give the BME680 its own louvered radiation-shield cavity, thermally isolated from the XIAO and HM3301.** Good shields take passive error from ~2 °C to **<0.5 °C** ([USFS](https://research.fs.usda.gov/treesearch/44116)).
4. **Stack geometry: 5–7 discs, ~12–18 mm gaps, alternating open/closed, flared/down-turned rims** (rain runs the outer skin, air enters shadowed gaps) ([Davis 7714](https://www.manualslib.com/manual/460560/Davis-7714-Radiation-Shield.html); [R.M. Young 41003](https://www.fondriest.com/pdf/rm_young_41003_spec.pdf)). Consider a **helical** stack for support-free printing + low-wind performance ([BARANI](https://www.baranidesign.com/meteoshield-professional)).
5. **Reflective inner liner + air gap — white plastic alone is not enough; filament is IR-transparent** ([Cave Pearl via Hackaday](https://hackaday.com/2022/02/04/3d-printed-radiation-shields-get-put-to-the-test/)).
6. **Bali is low-wind: passive shields show their *worst* error here (0.7–1.5 °C @ ≤2 m/s).** A micro-aspiration fan (**25–80 mA**, on its own ambient intake, not the PM bay) is the high-accuracy option ([Apogee TS-100](https://www.apogeeinstruments.com/content/TS-100-spec-sheet.pdf)). At minimum, plan a firmware T offset.

### Particulate path
7. **HM3301 gets a dedicated, straight-through, low-restriction air path**, intake at the shell wall facing **down**, separated from the T/RH cavity and from MCU heat; no recirculation loop or dead pocket (condensation kills the optics) ([AirGradient goals](https://www.airgradient.com/documentation/calibration-algorithms/)).
8. **Sense RH right at the PM inlet** — raw PM over-reads **~40 %** in humid air and physical corrections over-shoot above ~65 % RH (most of Bali's year), so RH-aware correction is mandatory ([AMT 2021](https://amt.copernicus.org/articles/14/4617/2021/), [AMT 2024](https://amt.copernicus.org/articles/17/6735/2024/)).

### Water + venting
9. **No opening faces up — ever.** Vents, mesh, weep holes all face down/down-out.
10. **Louver blades 35–45° down-and-out, ~45–55 % free area; recover airflow with area, not a straighter path** ([Greenheck Louver Fundamentals](https://content.greenheck.com/public/DAMProd/Original/10016/LouverFundamentals_appguide_ARL.pdf)).
11. **Labyrinth / Z-path** between outside and the chamber so droplets impact and drop out; drain the baffle floor outward ([US Patent 8,684,803](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8684803)).
12. **Drip lip 13–19 mm overhang ending in a downward curl/hem** (not a flat cut); zero straight sightline into any opening ([Construction Canada](https://www.constructioncanada.net/the-effectiveness-of-different-drip-edge-designs/)).
13. **Do NOT seal airtight.** A sealed box draws vapor in on every thermal cycle and traps it as liquid; use a **Gore-style ePTFE screw-in vent** (breathes both ways, no cracking pressure, IP67) on the leeward vertical face ([Gore FAQ](https://www.gore.com/resources/faq-gore-protective-vents), [Laird case](https://www.gore.com/resources/gore-protective-vents-reduce-condensation-sealed-enclosures)).
14. **Weep hole 2–3 mm at the single lowest interior point, angled down-out**; behind mesh/baffle so it's not an insect door ([Schneider NEMA 3R](https://www.se.com/us/en/faqs/FA240312/)).
15. **Stainless 304/316 insect mesh, 0.4–0.6 mm aperture, removable/cleanable cartridge** (0.42–0.57 mm stops mosquitoes; finer + baffle for ants; never nylon) ([The Mesh Company](https://themeshcompany.com/shop/insect-mesh/stainless-insect-mesh/0-57mm-hole-stainless-steel-woven-insect-mosquito-netting-0-28mm-wire-30-lpi/)).

### Material + print (Prusa CORE One)
16. **ASA for the sun-facing hood; UV-stabilized dark PETG (or PETG + UV clearcoat) for the body.** Bare/unstabilized PETG embrittles in **1–2 yr** equatorial sun; ASA lasts years; PLA dies in 30–90 days ([Hackaday/HardwareX](https://hackaday.com/2022/02/04/3d-printed-radiation-shields-get-put-to-the-test/), [JLC3DP](https://jlc3dp.com/blog/best-3d-printing-filament-outdoor-use)). Respect PETG Tg ~80–85 °C.
17. **Walls 2.5–3 mm, ≥4 perimeters; watertight recipe: nozzle +5–10 °C, flow +5–10 %, Linear Advance OFF, staggered inner seams ON** ([Prusa watertight](https://blog.prusa3d.com/watertight-3d-printing-part-2_53638/)).
18. **Support-free: ≤45° overhangs, 45° chamfers not 90° steps, bridges ≤5 mm, teardrop horizontal holes, elongated slots not round holes <4 mm** ([All3DP](https://all3dp.com/2/3d-printing-overhang-how-to-master-overhangs-exceeding-45/)).
19. **Brass heat-set inserts (M3/M4) at every serviced seam — never screw into printed PETG** (repeated open/close strips threads, deforms the shell, fails the seal) ([Smart Citizen](https://forum.smartcitizen.me/t/fighting-against-water-part-ii-effective-waterproof-3d-printed-enclosures-that-do-the-job/2017/3)).
20. **Never print the gasket.** Use an O-ring or **EPDM foam tube (Shore A15) in a ~3 mm groove + 1 mm compression nub** ([Prusa](https://blog.prusa3d.com/watertight-3d-printing-part-2_53638/)).

### Service + mount
21. **Single captive screw, sled drops out; external reset/USB poke-hole so you never open it to re-flash; wet I/O through one bottom gland with a drip loop** ([AirGradient](https://www.airgradient.com/documentation/diy-open-air-presoldered-v11), [PurpleAir](https://seetheair.org/2021/01/18/purpleair-ii-pa-ii-hack/)).
22. **Wall + pole mount (keyhole + zip-tie slots); standoff foot so a flush surface never blocks the bottom intake** ([PurpleAir Zen](https://www2.purpleair.com/products/purpleair-zen)).

---

## What this means for the Making Sense Bali node

The designs converge on an architecture the previous boxes ignored:

- **A vented sun-hood** (ASA, big overhang, drip-lip curl) over everything — takes the UV + rain + solar load.
- **A breathing sensor zone, not a sealed box** — IP54-by-geometry + one ePTFE membrane port; weep hole at the bottom.
- **The BME680 in its own louvered/helical radiation-shield stack** (5–7 discs, ~15 mm gaps, reflective-lined, air-gapped), thermally broken from the XIAO and HM3301, on its own bottom intake — *optionally micro-aspirated* given Bali's low wind.
- **The HM3301 on a dedicated down-facing straight-through duct**, intake at the wall, separated, with RH sensed at its inlet.
- **The XIAO/regulator conformal-coated in the sealed brain zone**, heat rising away from the BME680 stack.
- **Stainless mesh cartridges, brass inserts, elastomer gasket, captive-screw service, keyhole+pole mount.**

This is no longer "a box with holes." It's a shield + a duct + a sealed brain, packaged. That's tomorrow's build.

---

## Sources
All inline above. Strongest anchors: [AirGradient calibration algorithms](https://www.airgradient.com/documentation/calibration-algorithms/) · [PurpleAir T/RH evaluation (Atmosphere 2024)](https://www.mdpi.com/2073-4433/15/4/415) · [Apogee TS-100](https://www.apogeeinstruments.com/content/TS-100-spec-sheet.pdf) · [Davis 7714 geometry](https://www.manualslib.com/manual/460560/Davis-7714-Radiation-Shield.html) · [Gore Protective Vents FAQ](https://www.gore.com/resources/faq-gore-protective-vents) · [Greenheck Louver Fundamentals](https://content.greenheck.com/public/DAMProd/Original/10016/LouverFundamentals_appguide_ARL.pdf) · [Prusa watertight printing](https://blog.prusa3d.com/watertight-3d-printing-part-2_53638/) · [Smart Citizen SCK2.3](https://enclosures.smartcitizen.me/Air/SCK2.3/SCK2.3_SEN5X/3D_printed_outdoor_sen5x_only/) · [MDPI Atmosphere 2026](https://www.mdpi.com/2073-4433/17/3/272).
