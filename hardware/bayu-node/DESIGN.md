# Bayu node — modular air quality sensor for the Bali campaign

Proposal · 2026-10-24 · draft for discussion, nothing built yet. Corrected the same day
after the circuit drawings in [`circuits/`](circuits/) were checked against the Seeed
schematic and the Meshtastic source; what changed is listed in
[Corrections from the circuit drawings](#corrections-from-the-circuit-drawings).

Bayu is the campaign's node. The one deployed today is Bayu v3: XIAO ESP32-S3, BME680 and
HM3301 on a Grove Shield or Fab Lab Bali's PCB, firmware v5, enclosure node-v3.2, documented
in [`../diy-node/`](../diy-node/). This design keeps that node as it is and adds four
variants around it, with the same MCU and new sensors: Sensirion SEN54 and Plantower
PMS5003 / PMS5003T. One carrier board, several sensor roles, WiFi uplink on every unit and
LoRa mesh where WiFi is missing. Hard constraint: a complete kit under USD 100.

Bayu v3 already fits the pin budget below unchanged: its BME680 and HM3301 sit on the same
I2C bus the new variants use, so it runs on the Bayu Core board, on the Grove Shield, and on
the proposed [Grove Shield Mini](grove-shield-mini/).

On the name: `bayu-vN` was retired as an *enclosure* numbering scheme (see
[`../diy-node/enclosure/README.md`](../diy-node/enclosure/README.md)). Bayu names the node,
enclosures keep Fab Lab Bali's node-vN numbering.

## Decisions taken in this draft

These are my calls so the proposal is complete. Each one is cheap to reverse now and
expensive after the first PCB order.

1. **Mesh = Meshtastic on the Seeed Wio-SX1262 for XIAO, from day one** (Tomas's call,
   2026-10-24). The radio stacks on the XIAO through the board-to-board connector,
   Meshtastic ships a build for that exact pair, and kit1-hex already reserves the stack
   height and the SMA boss. Every Bayu node runs Meshtastic, WiFi-only ones included; the
   Smart Citizen firmware v5 stays on the DIY node and is not carried forward. ESP-NOW
   was rejected: 2.4 GHz, 100 to 300 m line of sight, useless between banjar compounds.
2. **USD 100 covers the whole kit on wall power:** MCU, sensors, carrier board, connectors,
   USB supply, printed enclosure, coating and fixings. Solar is a separate power module,
   priced apart, because most campaign sites have a socket.
3. **One carrier board for every role.** Roles differ only in what is plugged in.
   Meshtastic already works this way: its telemetry modules scan I2C at boot and bring up
   whatever they find.
4. **SEN54 and PMS5003 may live on the same node.** They use different buses (I2C and
   UART), and Meshtastic's air quality module polls every PM sensor it finds. This is what makes the anchor role
   a calibration tool and not just a nicer sensor.
5. **Phase 0 uses the Grove Shield for XIAO and pigtails, no PCB.** The carrier PCB is
   phase 1, once five nodes have run a month.

## Why these sensors, and what each one is for

| Sensor | Bus, power | Price range | Role in Bayu |
|---|---|---|---|
| **Sensirion SEN54** | I2C 0x69, 5 V (4.5 to 5.5), JST GH 1.25 mm 6-pin | USD 27 (DigiKey) to 35 (SparkFun); not stocked in Indonesia | Anchor tier. Laser PM1/2.5/4/10, VOC index, T/RH with Sensirion's compensation, fan auto-clean, 10-year spec. Quiet and stable enough to be the local reference the cheap tier is corrected against. |
| **Plantower PMS5003** | UART 9600 8N1, 5 V fan, 3.3 V logic, Molex PicoBlade 1.25 mm 8-pin | USD 13 to 16 direct from China, 25 at EU/US retail | Density tier. The most studied low-cost PM sensor there is (PurpleAir, Sensor.Community, AQ-SPEC). Correction curves exist, including the EPA's humidity term. |
| **Plantower PMS5003T** | as PMS5003 | USD 18 to 25 | Density tier, one part fewer. Same PM mass channels; the two largest particle-count bins are replaced by a T/RH reading. That T/RH sits in the fan's airflow inside the sensor housing: treat it as indicative, publish it flagged, never as ambient truth. |

What the Sensirion part does not buy: a SEN54 to PMS5003 head-to-head in the field does not
exist in the literature. The closest proxy is the SEN55 (same platform plus NOx), which
tracked an SPS30 within 6 to 10 % and gravimetric reference within about 15 % in a 2026
Ethiopian study, and which clips at high concentrations during biomass burning. For Bali's
July to October rice-stubble season that clipping matters: the PMS5003 next to it on the
anchor node reads the peaks the SEN54 flattens.

### Extra sensors: keep, option, skip

| Sensor | Price | Verdict |
|---|---|---|
| **SHT40 / SHT41** T/RH breakout | USD 2 to 6 | **Keep, on every outdoor node.** On a 10 cm Grove tail, mounted in the radiation-shield bay outside the electronics volume. This is the fix for the Node V2 failure (radio heating the BME680) and the ambient truth the PMS5003T and SEN54 internal readings are compared against. |
| **SCD40** CO2 | USD 17 bare, 20 to 25 as breakout | **Option, indoor role.** Ventilation in schools and kos rooms is a dengue, heat and health story the campaign has not told yet. SCD41 costs twice as much for range the sites never reach. |
| **SGP41** VOC/NOx index | USD 8 to 12 | Option only on PMS-based nodes that want a smoke signature. Redundant next to a SEN54. |
| **INMP441** I2S microphone | USD 2 to 4 | Option. Noise is a live complaint in Canggu; the XIAO S3 has I2S. Firmware work, not hardware cost. Publish a dBA-ish level, never audio. |
| **BH1750** light | USD 1 to 2 | Option as a diagnostic: tells you when a node sits in sun and its temperature reads high. |
| **BME280** pressure | USD 3 | Skip. Pressure adds nothing the campaign uses; the BME680 stays supported by v5 for existing nodes. |
| **MiCS-4514** CO/NO2 | USD 12 to 15 | Skip for now. Needs heater burn-in and per-unit calibration we cannot do yet. |
| Electrochemical NO2/O3 (Alphasense class) | USD 80 and up per gas | Out. Blows the budget on its own. |
| **GPS** (ATGM336H / NEO-6M class) | USD 4 to 6 | Only for a mobile role, see below. |

## Pin budget on the XIAO ESP32-S3

This is the fact the whole board design rests on. The Wio-SX1262 uses GPIO 38 to 42 for
NSS, reset, DIO1, busy and the RF switch, and SPI on GPIO 7/8/9. All of it reaches the radio
through the board-to-board connector. GPIO 38 to 42 are not castellated XIAO pins, but GPIO
7/8/9 are the same nets as D8 to D10, so with the LoRa board stacked those three are taken
and every other D pin is free.

The Wio rides on top of the XIAO, and its edge pads sit right over D0 to D4 carrying radio
lines. Header pins go into the XIAO only, with the stubs trimmed flush, never through both
boards.

| XIAO pin | GPIO | Bayu use |
|---|---|---|
| D4 / D5 | 5 / 6 | I2C: SEN54, SHT40, SCD40, Grove sockets |
| D6 / D7 | 43 / 44 | UART: PMS5003 or PMS5003T (one Plantower per node) |
| D0 | 1 | user button (config portal, LoRa pairing) |
| D1 | 2 | status LED (WS2812) |
| D2 | 3 | PMS5003 SET pin: fan sleep between readings. GPIO3 is a strapping pin (JTAG select); harmless here, the PMS only has a weak pull-up on SET |
| D3 | 4 | battery voltage sense (divider) when the Power module is fitted |
| D8 to D10 | 7 / 8 / 9 | SPI, taken by the Wio-SX1262 when fitted; keep them free on every Core so any node can take the radio later |

One UART means one Plantower per node. That is fine: a second PM sensor on a node is the
SEN54 on I2C.

## The board set

### 1. Bayu Core (the only mandatory board)

A 60 × 40 mm two-layer carrier, the same envelope as the 4 × 6 cm perfboard the node-v3.2
enclosure already takes, so no enclosure rework for phase 1. Kit1-hex rails are cut for the
25 × 58 mm Grove Shield and need a rail change or a printed adapter.

What is on it:

- female headers for the XIAO (socketed, as the DIY node already recommends), with 25 mm
  of clear height above for the Wio-SX1262 stack and a route for its U.FL pigtail;
- 1 × JST GH 1.25 mm 6-pin for the SEN54 (Sensirion's own connector, SEL tied to GND for I2C);
- 1 × Molex PicoBlade 1.25 mm 8-pin for the PMS5003 / PMS5003T, with SET wired to D2 and
  RESET left open (the sensor pulls SET and RESET up inside);
- 2 × Grove I2C sockets (SHT40, SCD40, anything else on the bus);
- 1 × Grove socket on D0/D1 jumpered as GPIO, for the button and LED breakout or a spare;
- 4.7 kΩ I2C pull-ups behind a solder jumper (Grove modules bring their own, bare SEN54 does
  not);
- 5 V rail from the XIAO's VBUS through a 1 A resettable fuse, with a 2-pin JST PH input so
  the Power module can feed 5 V instead;
- 3 M2.5 holes on the perfboard pattern, test pads on every bus, silkscreen with the role
  names so a workshop can read the board.

Cost: USD 2 to 3 per bare board at ten pieces from JLCPCB plus about USD 20 shipping to Bali
per order, so USD 4 to 5 per board landed. Connectors and headers add about USD 3. Fab Lab
Bali's PCB mill can cut a single-sided version for the first two, which saves the shipping
wait but not the connector order.

I2C addresses never collide: SEN54 0x69, SHT40 0x44, SCD40 0x62, SGP41 0x59, BH1750 0x23,
HM3301 0x40, BME680 0x76/0x77.

### 2. Bayu Power (optional, off-grid sites only)

40 × 30 mm. 6 V solar input on JST PH, CN3791 MPPT charger or a TP4056 if MPPT is not
stocked, single 18650 holder or LiPo on JST PH, 5 V boost (TPS61023 or MT3608 class, 2 A)
with its enable pin on a header so the firmware kills the fan rail during sleep, battery
divider to D3. The XIAO's own charger is bypassed. Parts about USD 6, panel USD 6 to 8,
cell USD 4. Fan sensors are the whole power story: a PMS5003 draws about 100 mA awake and
0.2 mA asleep, so a 30 s read every 3 minutes is what makes a 3 W panel enough.

### 3. Bayu Climate (optional, tiny)

An SHT40 on a 20 × 20 mm board with a Grove tail, meant to be clipped into the enclosure's
radiation-shield bay, 60 mm or more from the stack. Off the shelf Grove or Adafruit SHT40
breakouts do the same job for USD 3 to 6; this board only exists if the printed clip wants a
specific outline. Skip it in phase 0.

### No mesh board

The Wio-SX1262 for XIAO is the mesh board. Buy it as the Seeed kit with the XIAO, USD 9.90.
Seeed sells the board-to-board version of the radio only in that kit, a plain XIAO ESP32-S3
may come without the B2B connector fitted, and the "Wio-SX1262 for XIAO" sold on its own is
likely the header version for the nRF52840 with a different pinout. The Core only has to
leave 25 mm of room above the socket and a pigtail path to the SMA bulkhead.

## Roles

| Role | Fitted | What it answers | Where, how many |
|---|---|---|---|
| **Bayu Anchor** | SEN54 + PMS5003 + SHT40, LoRa stack | The reference the cheap tier is corrected against, and the burning-season peak reader. Every PMS5003 in a cluster gets its correction from the nearest anchor. | One per cluster: a banjar, a school, the Fab Lab. Co-located for its first week against an SCK. |
| **Bayu Dense** | PMS5003T only, WiFi, LoRa optional | PM2.5 and PM10 at spatial density. Indicative T/RH. | Many: kos rooms, warungs, compounds. Deployed by participants after a workshop. |
| **Bayu Indoor** | PMS5003 + SCD40 + SHT40, WiFi | Ventilation and indoor combustion: classrooms, kos, kitchens with mosquito coils. | Schools and kos, in the dozens. No enclosure venting problem, a simple printed shell. |
| **Bayu Relay** | XIAO + Wio-SX1262 + SHT40, WiFi, MQTT uplink on | Carries a cluster's LoRa traffic to the broker. The SHT40 makes it a climate point rather than a dead box. | One per cluster where the anchor has no WiFi. Any Anchor or Dense with WiFi does the same job, so most clusters need none. |
| **Bayu Mobile** (later) | PMS5003 + SHT40 + GPS, battery | Traffic-corridor transects on a motorbike, Gojek partnerships. | A handful. Not in this round; GPS and battery both bring their own problems. |

One Meshtastic image runs every role. Roles differ in what is plugged in and in two
settings: device role (`SENSOR` for Anchor, Dense and Indoor, `CLIENT` for a Relay, since
`ROUTER_CLIENT` is deprecated and the `ROUTER` roles force power saving, which sleeps WiFi)
and whether MQTT uplink is on (yes on any node with WiFi).

## Cost per kit

USD, single-unit prices, October 2026, direct sourcing (Seeed or China for Plantower and
XIAO, DigiKey or RS for Sensirion). Indonesian retail is in the next table.

| Item | Dense | Anchor | Indoor | Relay |
|---|---|---|---|---|
| XIAO ESP32-S3 | 7.5 | 7.5 | 7.5 | 7.5 |
| Wio-SX1262 | — | 6 | — | 6 |
| SEN54 + cable | — | 32 | — | — |
| PMS5003 / PMS5003T | 22 | 15 | 15 | — |
| SHT40 breakout | — | 4 | 4 | 4 |
| SCD40 breakout | — | — | 22 | — |
| Core PCB landed + connectors | 8 | 8 | 8 | 8 |
| 5 V / 2 A USB supply + cable | 5 | 5 | 5 | 5 |
| Enclosure print (PETG/ASA, 150 to 250 g) | 7 | 8 | 5 | 5 |
| Coating, mesh, ties, SMA bulkhead where LoRa | 3 | 5 | 3 | 4 |
| **Total** | **52** | **91** | **70** | **40** |

- Dense with LoRa: about 58. Anchor without LoRa: about 85.
- The LoRa columns price the XIAO and the Wio apart, USD 13.50. As the Seeed kit they cost
  USD 9.90, so an Anchor or a Relay built from the kit comes out about USD 3.50 cheaper.
  The variant pages quote the higher figure.
- The Power module with panel and cell adds 18 to 22 on top of the supply it replaces, so an
  off-grid Anchor lands at 105 to 110. That is the one configuration over budget; fix it by
  dropping the PMS5003 from an off-grid anchor (back to about 92) or accepting it for the
  two or three sites that need it.
- Phase 0 (Grove Shield at USD 5 plus pigtails instead of the Core) costs the same within
  a dollar.

## Availability by region

| Part | Indonesia (Tokopedia, Shopee, Halo Robotics) | China direct (Seeed, AliExpress, LCSC) | Singapore / Malaysia (RS, element14) | EU (Mouser, DigiKey, RS, Berrybase, Sensor.Community shops) | US (Adafruit, SparkFun, DigiKey) |
|---|---|---|---|---|---|
| XIAO ESP32-S3 | Yes. Rp 279k and up, the Sense variant Rp 410 to 740k | USD 7.49 Seeed, in stock | Yes | Yes, ~EUR 8 to 10 | Yes, ~USD 8 |
| Wio-SX1262 for XIAO | Only as the kit with XIAO, Rp 399 to 500k, thin stock | USD 5 to 6 alone, 9.90 as kit | Patchy | Yes, GBP 4.80 at The Pi Hut | Yes, USD 12 to 13 as kit |
| SEN54 | **No local stock found.** Import only | Seeed Grove SEN54 (price not verified this round, page returned 404); Sensirion via LCSC | RS Malaysia / Hong Kong carry trays; single units patchy | DigiKey USD 26.85, RS UK GBP 20, both in stock | SparkFun USD 34.95, DigiKey |
| PMS5003 | Yes, generic sellers; expect Rp 250 to 400k (not verified this round) | USD 13 to 16, with pigtail, weeks of lead time | Yes | USD 20 to 25 retail | Adafruit USD 39.95 |
| PMS5003T | Rare locally | USD 18 to 25 on AliExpress and eBay, often a variant of the same listing | Rare | Rare | Rare |
| SHT40 / SHT41 breakout | Yes, clones, Rp 40 to 90k | USD 1.5 to 3 | Yes | Adafruit and Sensirion dev boards, EUR 5 to 8 | Adafruit USD 5.95 |
| SCD40 breakout | Some, Rp 300 to 450k | USD 17 to 22 | RS: bare SCD40 ~EUR 17 | Pimoroni / Adafruit, EUR 25 to 45 | Adafruit USD 44.95 |
| Grove Shield for XIAO | Yes via Halo Robotics, markup | USD 4 to 5 | Yes | GBP 3.80 to 4.50 | Yes |
| JST GH / PicoBlade connectors, 18650 holders, boost modules | Yes, Tokopedia generic | LCSC, cents | Yes | Yes | Yes |
| 6 V solar panel, CN3791 | Yes, Rp 60 to 120k | USD 5 to 8 | Yes | Yes | Yes |

Import rules into Indonesia as of this draft: de minimis is USD 3, above that 7.5 % flat
duty plus 11 % VAT plus income tax withholding on the declared value, and courier handling
fees on top. A single SEN54 ordered to Denpasar lands near USD 40. Three ways around it:

1. **One consolidated Seeed order to Fab Lab Bali** for XIAO, Wio-SX1262, Grove Shields
   and Grove SEN54, as the DIY node already does for the HM3301. Budget three weeks.
2. **Carry Sensirion parts in from Barcelona or Singapore.** DigiKey and RS stock the SEN54
   in both places, and it is small and light. One trip covers a year of anchors.
3. **Plantower from Tokopedia** for the dense tier. The sellers' stock is real, the lead
   time is days, and the price difference against China direct is smaller than the duty.

What this table does not settle: a current Tokopedia price for the PMS5003 and PMS5003T,
and whether Halo Robotics will list the Grove SEN54. Both are a ten-minute check in a
browser, not a search engine.

## Mesh: Meshtastic on every node

### What upstream already does

Checked against `meshtastic/firmware` master on 2026-10-24. More is there than the
documentation says:

| Bayu part | Upstream driver | Fields it fills |
|---|---|---|
| SEN54 | `Sensor/SEN5XSensor.h` + `SENXXSensor.cpp`, in `AirQualityTelemetry` | PM1/2.5/4/10, particle counts, `pm_temperature`, `pm_humidity`, `pm_voc_idx`, `pm_nox_idx`, `pm_status_flags`; handles warm-up and fan cleaning |
| SHT40 | `Sensor/SHT4XSensor.h`, in `EnvironmentTelemetry` | `temperature`, `relative_humidity` |
| SCD40 | `Sensor/SCD4XSensor.h`, in `AirQualityTelemetry` | `co2`, `co2_temperature`, `co2_humidity` |
| BH1750, VEML7700 | in `EnvironmentTelemetry` | `lux` |
| HM3301 (existing DIY Plus nodes) | `Sensor/HM330XSensor.h` | PM fields |
| Plantower over I2C (PMSA003I) | `Sensor/PMSA003ISensor.cpp` | all PM and particle fields, with sleep/wake through `PMSA003I_ENABLE_PIN` |
| **PMS5003 / PMS5003T over UART** | **missing** | — |

The `AirQualityMetrics` protobuf already has every field Bayu needs, including
`pm_temperature` and `pm_humidity` for the PMS5003T's internal reading. No protobuf
change, so the stock Android and iOS apps and anything that decodes Meshtastic's MQTT
protobufs understand Bayu packets unchanged.

### The fork, scoped

One new sensor class, one small module change and one build variant. All three are
candidates to send upstream.

1. **`Sensor/PMS5003Sensor.{h,cpp}`**, UART transport. The PMSA003I class already parses
   the 32-byte 0x42 0x4D frame and already implements sleep, wake-up, warm-up (30 s) and
   the readiness wait; the UART class reuses that parsing and swaps `Wire` for `Serial1`
   at 9600 8N1. It is registered without an I2C scan (`DeviceType::NONE`, the way
   `T1000xSensor` is) behind a build flag `HAS_PMS5003_UART`. The SET pin goes on
   `PMS5003_ENABLE_PIN` (D2, GPIO3) and follows the same duty cycle as the I2C class.
   For the T variant, bytes 24 to 27 go to `pm_temperature` and `pm_humidity` and the two
   missing count bins are left unset.
2. **One packet per PM sensor.** `AirQualityTelemetry` currently loops over its sensors
   and lets each one write into the same `AirQualityMetrics` message, so on an Anchor the
   last sensor read would overwrite the other's PM fields. The fork sends one packet per
   sensor instead, alternating. No new field is needed to tell them apart: a SEN54 packet
   carries `pm_voc_idx` and `particles_tps`, a Plantower packet carries `particles_03um`,
   and the bridge keys on that. This is the one change that touches a module rather than
   adding a sensor, and the one most worth discussing upstream before writing it.
3. **Variant `variants/esp32s3/seeed_xiao_s3_bayu/`**, copied from `seeed_xiao_s3`, which
   is the Wio-SX1262 kit build. Changes: `PIN_SERIAL1_RX/TX` on GPIO 44/43 (D7/D6) belong
   to the PMS instead of the L76K GPS, `HAS_GPS 0`, `HAS_PMS5003_UART 1`,
   `PMS5003_ENABLE_PIN 3`, button on GPIO1 (D0), WS2812 on GPIO2 (D1), battery ADC on
   GPIO4 (D3). Everything LoRa-side is inherited untouched (GPIO 38 to 42, SPI 7/8/9).
4. **Build flags** trimmed to what Bayu uses, so the image fits the XIAO's 8 MB flash with
   OTA partitions. The stock XIAO build already does.
5. **Nothing else.** No protobuf edits, no app changes.

Done looks like: a Bayu Anchor appears in the stock Meshtastic app with PM2.5 from both
the SEN54 and the PMS5003 in its telemetry log, and the same packet arrives on the
broker. Rough size: about 200 lines of C++ and a 60-line variant header. Upstream the
PMS5003 UART class first; the variant can live in our fork until there is a Bayu product
to name it after.

### Region and channel

- Band: 920 to 923 MHz class licence in Indonesia. Meshtastic has no `ID` region yet;
  firmware issue #9782 (ID_923) has been open since March 2026. Until it lands, the
  Indonesian community runs `MY_919` (919 to 924 MHz). Bayu does the same and pins
  `lora.override_frequency` to a slot inside 920 to 923 MHz so no node ever transmits on
  the band edges. Verify the legal text (PM Kominfo 1/2019 or Permenkomdigi 2/2025) once
  before the first deployment; both are cited by the community, neither was read for
  this draft.
- Channel plan: a private `bayu` channel with its own PSK and MQTT uplink enabled, as the
  primary. The default public `LongFast` channel as a secondary only on Relays, so the
  campaign nodes also carry community traffic without exposing campaign telemetry to the
  public MQTT broker.
- Modem preset: `MEDIUM_FAST` for a dense cluster within a village, `LONG_FAST` where a
  Relay has to reach across rice fields. Air-time budget: one `AirQualityMetrics` packet
  is under 80 bytes, so at a 15-minute `air_quality_interval` a cluster of 20 Dense nodes
  stays well under the channel-utilisation cap on either preset. Meshtastic scales the
  interval up by itself as the node count grows.

### Data path to Smart Citizen

```
Bayu node (SENSOR role) --LoRa--> any WiFi node in the cluster --MQTT uplink--> broker
broker (msh/ID/2/e/bayu/#) --> bayu-bridge --> Smart Citizen MQTT (per-device token)
```

- Broker: our own Mosquitto in Docker on the NAS, next to the AQ bot. Not the public
  `mqtt.meshtastic.org`: it rate-limits, it is public, and we lose nothing by owning it.
  MQTT JSON output was removed in firmware 2.8.0, so nodes publish protobuf only, with
  `mqtt.encryption_enabled false` so the packet inside arrives decoded.
- `bayu-bridge`: a small Python service that subscribes to the protobuf topic, decodes the
  `ServiceEnvelope` with the `meshtastic` Python package, maps Meshtastic
  node id to Smart Citizen device token and sensor ids, applies the field mapping
  (`pm25_environmental` to PM2.5, `pm_temperature` to "PM internal temperature", and so
  on), and republishes with the token. One YAML file holds the node table. This replaces
  the per-node credentials that v5 kept in `secrets.h`: tokens never leave the NAS.
- Dashboard markers stay as today: Dense nodes are DIY tier, Anchors are their own tier.

### What Meshtastic costs us

- No captive portal for WiFi credentials. On an ESP32, Meshtastic runs Bluetooth only while
  WiFi is off, so provisioning goes over Bluetooth until WiFi is set, and over USB with the
  Meshtastic CLI or over the node's IP after. Do it once per node, in the workshop, WiFi
  last.
- Telemetry interval floor: Meshtastic will not broadcast sensor telemetry faster than a
  few minutes and scales back on busy meshes. For PM, 5 to 15 minutes is the right
  cadence anyway.
- A firmware fork to maintain against a fast-moving upstream, until the PMS5003 UART class
  is merged. Rebase cost is small while the fork is one class and one variant.

## Firmware plan

Smart Citizen firmware v5 stays with the DIY node and is not ported. Bayu work splits in
three pieces, in this order:

1. **Fork and variant** (section above): flash a stock `seeed_xiao_s3` image on the kit,
   confirm SEN54, SHT40 and SCD40 show up in the app with no code at all. Then add the
   PMS5003 UART class and the Bayu variant.
2. **Broker and bridge** on the NAS: Mosquitto container, `bayu-bridge` container, node
   table. Done when a Dense node's PM2.5 appears on smartcitizen.me through the mesh.
3. **Correction, server side.** PMS5003 raw values are published as read. The EPA
   PurpleAir-style humidity correction and the per-cluster anchor coefficients run on the
   server, where they can be revised; nodes never carry calibration state. The humidity
   term uses ambient RH from a shielded SHT40: the node's own on Anchor and Indoor, the
   nearest Anchor or Relay for a Dense node. A PMS5003T's internal RH reads low because its
   air is warm, and would under-correct.

Fan sleep for the Plantower is Meshtastic's existing sleep/wake cycle driven by the SET
pin: 30 s warm-up before each read, idle between reads. This roughly triples fan life
against always-on and is the difference between a 1-year and a 3-year node in Bali's
humidity. The SEN54 manages its own fan and periodic cleaning.

## Data honesty, unchanged

Dense nodes report as DIY tier with their own dashboard marker. Every new node co-locates
against an Anchor or an SCK for its first week. Anchors co-locate against an SCK or the
nearest official reference station when they are first installed. A PMS5003T's temperature is never
shown as ambient.

## What I would do first

Flash one XIAO + Wio-SX1262 kit with stock Meshtastic and plug a SEN54 and an SHT40 into
it: that is a working Anchor radio in an afternoon, before any fork. Then build five on
Grove Shields, no PCB: two Anchors (one at the Fab Lab next to the SCK, one at a school),
three Dense with PMS5003T on the forked image. Run them a month. The co-location week tells you
whether the SEN54 is worth USD 30 against a corrected PMS5003 in this climate; nobody has
published that for the tropics. Order the Core PCB only after that answer, with whatever
the month changed on the connector list.

## Open decisions

1. Does the USD 100 need to include solar for most sites, or is wall power the norm?
2. Roles to start with: Anchor + Dense as above, or Indoor first because the school
   partners are ready?
3. PCB in phase 0 after all, if the mill at Fab Lab Bali is free and the connector order
   can go out this week?

Settled 2026-10-24: Meshtastic from day one, fork limited to the PMS5003 UART sensor class,
one packet per PM sensor, and a Bayu board variant. My calls inside that: own Mosquitto broker on the NAS rather
than the public Meshtastic broker, and `MY_919` with a pinned frequency inside 920 to 923
MHz until Meshtastic ships an Indonesia region.

## Corrections from the circuit drawings

The four variant sessions checked the drawings against the Seeed schematic, the sensor
datasheets and the Meshtastic source on 2026-10-24. What they found, now fixed above:

1. D8 to D10 are the radio's SPI bus, so the LoRa board does take three D pins.
2. The Wio's edge pads over D0 to D4 carry radio lines: header into the XIAO only.
3. Buy the XIAO and Wio as Seeed's kit; the board sold alone is likely a different radio.
4. PMS5003 RESET needs no pull-up on the Core, the sensor has one inside.
5. A Relay uses the `CLIENT` role, not `ROUTER_CLIENT`.
6. Meshtastic 2.8.0 dropped MQTT JSON, so the bridge decodes protobuf.
7. Bluetooth stops once WiFi is on, which changes the provisioning order.

Open from the same checks: the WS2812 is specified from 3.5 V and is run on 3V3 here, the
SCD40's accuracy is specified only up to 2000 ppm, and a diode is needed on the Core's 5 V
input if the Power board and USB can both be live.

## Sources checked for this draft

- DigiKey SEN54-SDN-T listing USD 26.85; SparkFun SEN-19325 USD 34.95; RS UK GBP 20.16.
- Seeed XIAO ESP32-S3 product page, USD 7.49 in stock; Tokopedia search pages, Rp 279k.
- The Pi Hut, Wio-SX1262 for XIAO GBP 4.80; XIAO + Wio-SX1262 kit GBP 9.60 to 10.50;
  Seeed launch price USD 9.90; Tokopedia kit listings Rp 399 to 500k.
- Meshtastic firmware `variants/esp32s3/seeed_xiao_s3/variant.h` for the LoRa GPIO map;
  `src/modules/Telemetry/AirQualityTelemetry.cpp`, `Sensor/SEN5XSensor.h`,
  `Sensor/PMSA003ISensor.cpp`, `EnvironmentTelemetry.cpp` for the driver inventory;
  `meshtastic/protobufs` `telemetry.proto` and `config.proto` (`override_frequency`,
  `MY_919`, `SG_923`); firmware issue #9782 (Indonesia region, open).
- Meshtastic region-by-country page (Indonesia → SG_923); MeshNode Indonesia and
  mesh.nusatec.id on the 920 to 923 MHz class licence and the MY_919 community practice.
- Barkjohn, Gantt, Clements 2021, AMT 14:4617, the US-wide PurpleAir correction.
- EGUsphere 2026-2537 preprint, SEN55 vs SPS30 vs gravimetric in Arba Minch.
- Plantower PMS5003 manual v2.3: 100 mA active, 200 µA standby, MTTF 3 years.
- Zonos and forwarder guides on Indonesian de minimis (USD 3), 7.5 % duty, 11 % VAT.
