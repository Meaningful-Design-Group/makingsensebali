# Reference — evidence base (22 designs surveyed, 2026-06)

Condensed catalogue behind the rules in SKILL.md. Refresh if the node differs.

## DIY / open-source
- **AirGradient Open Air** — T/RH read inside the PM module + firmware correction; dual PMS cross-mounted; 3 parts, ASA. [build](https://www.airgradient.com/documentation/diy-open-air-presoldered-v11)
- **AirGradient DIY Outdoor** — snap-on external temp probe; PM fan faces the edge. [doc](https://www.airgradient.com/documentation/diy-outdoor)
- **Smart Citizen SCK2.3** — white PETG, no supports, ≥3 perimeters; 2.0 mm seal; M4 brass inserts; pressure-relief membrane; tropical-tested. [SCK2.3](https://enclosures.smartcitizen.me/Air/SCK2.3/SCK2.3_SEN5X/3D_printed_outdoor_sen5x_only/), [Fighting Water II](https://forum.smartcitizen.me/t/fighting-against-water-part-ii-effective-waterproof-3d-printed-enclosures-that-do-the-job/2017/3)
- **Smart Citizen frog box + umbrella** — separate radiation-shield/rain-hat over a sealed box. [SC](https://enclosures.smartcitizen.me/Air/)
- **Sensor.Community airRohr** — two DN75 87° elbows, openings face down; mesh over tube ends. [airRohr](https://sensor.community/en/sensors/airrohr/)
- **Printables PMS5003 (rainb0w_wheez3)** — slanted roof + ridge; separate Stevenson screen for BME280; 19 mm filter mesh; support-free. [39560](https://www.printables.com/model/39560-outdoor-enclosure-for-pms5003-particulate-matter-s)

## Commercial
- **PurpleAir PA-II/Flex/Zen** — hat+recess+open bottom; one-screw captive sled; open bottom invites wasps. [AQ-SPEC](https://www.aqmd.gov/aq-spec/product/purpleair-pa-ii)
- **Clarity Node-S** — two zones: IP67 electronics + IPX3 sensing module. [Node-S](https://www.clarity.io/products/clarity-node-s)
- **Aeroqual AQS 1** — standoff double-skin solar shield; inlet heater dries the PM sample. [AQS1](https://www.aeroqual.com/products/aqs-air-quality-monitor)
- **QuantAQ MODULAIR** — bottom intake behind insect screen; T/RH "flow cell, not ambient"; wet I/O on bottom. [docs](https://docs.quant-aq.com/hardware/modulair/modulair)
- **TSI BlueSky** — ~0.3 LPM PM flow → small shieldable openings; IP67 supply. [spec](https://www.kenelec.com.au/wp-content/uploads/2023/05/TSI-8143-8145-Bluesky-Air-Quality-Monitor-SpecSheet-revF-2023.pdf)
- **Vaisala AQT530** — vertical cylinder + louvered PC radiation shield; sealed M12. [datasheet](https://usermanual.wiki/m/c223d58f46d0e17a055dd1cc2efa9fd4c67141c8ec64284c6941a6cff94de1ce)
- **Kunak AIR Pro** — self-identifying plug-in sensor cartridges. [Kunak](https://kunakair.com/air-quality-monitor/)
- **Atmotube Pro 2** — airflow vs full waterproofing are mutually exclusive in a small body. [Atmotube](https://atmotube.com/atmotube-pro)
- **Libelium Plug & Sense!** — all I/O via sealed external screw-in ports/probes. [Libelium](https://www.libelium.com/iot-products/plug-sense/)

## Radiation shields / T-RH housings
- **Stevenson screen** — double-louver walls + double roof w/ air gap. [wiki](https://en.wikipedia.org/wiki/Stevenson_screen)
- **R.M. Young 41003** — flared stacked discs; error 0.4/0.7/1.5 °C @ 3/2/1 m/s (passive fails low-wind). [datasheet](https://www.fondriest.com/pdf/rm_young_41003_spec.pdf)
- **Davis 7714** — 6 plates (3 open/3 closed), 13–25 mm gaps. [manual](https://www.manualslib.com/manual/460560/Davis-7714-Radiation-Shield.html)
- **R.M. Young 43502 aspirated** — triple-wall intake, <±0.2 °C. [Campbell](https://www.campbellsci.com/43502)
- **Apogee TS-100** — low-power aspiration 25–80 mA, within 0.03 °C. [spec](https://www.apogeeinstruments.com/content/TS-100-spec-sheet.pdf)
- **BARANI MeteoShield Pro** — helical double-louver vortex; ~zero error >1 m/s; 3D-printable form. [BARANI](https://www.baranidesign.com/meteoshield-professional)
- **DIY flower-pot shields** — 4–7 discs on rods; filament IR-transparent → foil liner; PLA dies 30–90 d UV. [Hackaday](https://hackaday.com/2022/02/04/3d-printed-radiation-shields-get-put-to-the-test/)

## Key quantified anchors
- Enclosure T/RH bias: +2.7…+5.3 °C, RH −9.7…−24.3 % ([Atmosphere 2024](https://www.mdpi.com/2073-4433/15/4/415)); AirGradient correction T×1.181−5.113, RH×1.259+7.34 ([AG](https://www.airgradient.com/documentation/calibration-algorithms/)).
- PM over-reads ~40 % in humid air; correct with RH term, over-shoots >65 % RH ([AMT 2021](https://amt.copernicus.org/articles/14/4617/2021/), [AMT 2024](https://amt.copernicus.org/articles/17/6735/2024/)).
- Louvers 35–45°, 45–55 % free area ([Greenheck](https://content.greenheck.com/public/DAMProd/Original/10016/LouverFundamentals_appguide_ARL.pdf)); drip lip 13–19 mm ([Construction Canada](https://www.constructioncanada.net/the-effectiveness-of-different-drip-edge-designs/)); ePTFE vent ([Gore](https://www.gore.com/resources/faq-gore-protective-vents)); mesh 0.4–0.6 mm ([Mesh Co](https://themeshcompany.com/shop/insect-mesh/stainless-insect-mesh/0-57mm-hole-stainless-steel-woven-insect-mosquito-netting-0-28mm-wire-30-lpi/)).
- Print: walls 2.5–3 mm/≥4 perimeters, watertight recipe, ≤45° overhangs ([Prusa](https://blog.prusa3d.com/watertight-3d-printing-part-2_53638/), [All3DP](https://all3dp.com/2/3d-printing-overhang-how-to-master-overhangs-exceeding-45/)); ASA>PETG>PLA outdoors ([JLC3DP](https://jlc3dp.com/blog/best-3d-printing-filament-outdoor-use)).
- Airflow-guiding geometry beats a plate stack: 0.12 vs 0.59 °C ([MDPI Atmosphere 2026](https://www.mdpi.com/2073-4433/17/3/272)).
