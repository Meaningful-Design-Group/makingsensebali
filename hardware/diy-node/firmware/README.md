# Bayu firmware

**Flash [`diy_node_v5/`](diy_node_v5/) once it has passed a bench check (below); until
then, [`diy_node_v4/`](diy_node_v4/).** One image serves the whole fleet — no
secrets in the source, WiFi and the Smart Citizen token entered through a captive
portal on a phone, and a status page on the local network so a node can be checked
without a laptop. v4 added one choice: where the node publishes. Left alone it goes to
Smart Citizen exactly as v3 did; pointed at a [PLANETAI node](https://planetai.fab.city)
on the same network it publishes there first, and the node passes the readings on.
v5 adds the other half of "one image": it works out which sensors are plugged in.
Since 24 Oct 2026 it also knows the Bayu sensors (Plantower PMS5003 and PMS5003T,
SHT4x, SCD4x), tries the PLANETAI node before Smart Citizen, and updates itself
from the published build, so a node flashed once by cable keeps up from then on.

| Sketch | What it's for |
|---|---|
| [`diy_node_v6/`](diy_node_v6/) | **On the bench, not yet flashed by CI.** v5 plus automatic detection of the Seeed Expansion Base for XIAO: on that board it adds the screen with the Fab City logo, readings and ISPU alarms, the buzzer, the button, a CSV log on the microSD and the clock. On a Grove Shield it behaves as v5. Status LED on the XIAO ESP32-S3. Compiled for both chips; has not run on a board. |
| [`diy_node_v5/`](diy_node_v5/) | **The production candidate.** v4 plus sensor auto-detect: HM3301, Sensirion SEN5x, BME680, SHT4x, SCD4x and a Plantower PMS5003 or PMS5003T, in any combination. PLANETAI node first, Smart Citizen as fallback, daily self-update. Compiled for XIAO ESP32-S3 and ESP32-C3 on core 3.3.12; the self-update and the three new sensors have not run on a board yet. |
| [`diy_node_v4/`](diy_node_v4/) | HM3301 + BME680 only. Publishes to Smart Citizen, or to a PLANETAI node on the LAN. |
| [`diy_node_v3/`](diy_node_v3/) | The previous production sketch: Smart Citizen only. Kept until every fleet node is on v4 or later. |
| [`diy_node_test/`](diy_node_test/) | Verification only. Scans I²C, probes both sensors, prints to Serial every 5 s. No WiFi, no MQTT, no Smart Citizen account. What a participant flashes straight after soldering. |
| [`diy_node_display/`](diy_node_display/) | The variant driving the XIAO Expansion Base OLED. |
| [`previous/`](previous/) | Retired. Kept for history, not for flashing. |

## Sensors (v5)

Plug in any of these and flash the same image. There are no build flags.

| Sensor | Address | Published on Smart Citizen IDs |
|---|---|---|
| Seeed Grove HM3301 | 0x40 | 233 PM1 · 234 PM2.5 · 235 PM10 |
| Sensirion SEN50 / SEN54 / SEN55 (e.g. Seeed *Grove – All in one Environmental Sensor SEN5X*) | 0x69 | 193 PM1 · 194 PM2.5 · 195 PM4 · 196 PM10 · 203 RH · 204 T · 205 VOC index · 206 NOx index |
| Bosch BME680 | 0x76 / 0x77 | 237 T · 238 RH · 239 pressure · 240 gas · 241 IAQ (approximation) |
| Sensirion SHT40 / SHT41 / SHT45 | 0x44 | 79 T · 80 RH (see below) |
| Sensirion SCD40 / SCD41 | 0x62 | 258 CO2 · 259 T · 260 RH |
| Plantower PMS5003 | UART, XIAO D7 | 89 PM1 · 87 PM2.5 · 88 PM10 |
| Plantower PMS5003T | UART, XIAO D7 | 89 PM1 · 87 PM2.5 · 88 PM10 · 118 T · 119 RH |

The SEN5x IDs are the ones the Smart Citizen Kit 2.3 publishes the same part on
(`fablabbcn/smartcitizen-kit-2x`, `lib/Sensors/Sensors.h`), so a DIY node with a
SEN5x is directly comparable with the kits. The model is read from the sensor, and
channels a model doesn't have (SEN50: no T/RH/VOC; SEN54: no NOx) are simply not
published.

The PMS5003 and SCD4x IDs are the ones the kits use too: 87/88/89 are the SCK's
Plantower PM board, 118/119 its "Particle Matter Sensor Temperature/Humidity", and
258–260 its SCD4x. Smart Citizen has no SHT4x entry, so the SHT4x goes on 79/80,
the "External Sensirion SHT31" channels the kits use for their own external T/RH
probe. It is the same family one generation older, and the two IDs are constants at
the top of the sketch if the platform adds an SHT4x.

**The Plantower is only listened to.** Its TX goes to XIAO D7 (GPIO44 on the S3,
GPIO20 on the C3, which is also RX on the C3 SuperMini); the node opens that pin as
UART receive and attaches nothing to its own TX, so a board with something else on
D6 or D7 is never driven. The sensor streams a frame every second from power-up,
and the node counts it as fitted when a frame with a good checksum arrives. Its
SET pin can stay unconnected: the PMS5003 pulls it up and runs. Nothing from it is
published for its first 30 seconds, the time Plantower gives the fan to settle.

**PMS5003 or PMS5003T is read from the frames.** Both send the same frame; the T
puts its temperature and humidity where the plain one has its 5 µm and 10 µm
counts. Those counts are cumulative, so on a PMS5003 they can only fall as the size
grows, and a frame where they rise must come from a T. Until the node has seen one
it publishes PM only, so a T is never mistaken the other way round.

**The SCD4x calibrates itself** against the lowest CO2 it sees each week, assuming
that is outdoor air near 400 ppm. That is the factory setting and it stays on. In a
room that never airs out, the reading will drift.

**A sensor that isn't plugged in is "not fitted", not an error.** It gets one line in
the boot inventory (`[sensors] fitted: HM3301 (0x40), BME680 · not fitted: SEN5x`) and
a grey row on the status page, and that's all. Every 5 minutes the node quietly looks
for a sensor that wasn't there and brings it up if it now answers. The one state
that *is* reported as a fault is a sensor that was online and then fails three reads
in a row: that is a loose cable or a dead fan, and it is logged once and shown in red.

**HM3301 and SEN5x together is supported and worth doing.** They publish on
different IDs, so a node carrying both is a co-location in one box: the shared
HM3301 correction curve can be checked against a SEN5x on every such node, not only
at the two co-location sites.

**Power.** The SEN5x runs a laser and a fan and needs 5 V (Sensirion: 4.5–5.5 V,
about 70 mA while measuring); its I²C lines are fine at 3.3 V. If it doesn't appear
in the boot inventory, check the Grove port's supply before suspecting the firmware.

Nothing about how the HM3301 or BME680 are read changed from v2 to v5 — same
oversampling, filter, heater profile, frame bytes and IDs — so a calibration fitted
on older nodes still applies.

### Bench check before promoting v5

One node, one serial monitor, four boots: HM3301 + BME680 only (must publish exactly
what v4 published), SEN5x only, all three, and none. Then pull the SEN5x cable on a
running node and confirm one "stopped answering" line after three minutes, and that
it comes back within five minutes of reconnecting. Check the device page on
smartcitizen.me shows the SEN5x channels.

For the 24 Oct additions, on an S3 and a C3:

1. A Bayu board with PMS5003T, SHT40 and SCD40: all three in the boot inventory,
   `the Plantower is a PMS5003T` within a minute, nothing from it in the first 30 s.
2. A plain PMS5003 alone on D7: fitted, PM published, no 118/119 ever.
3. An existing fleet node with nothing on D7: the same inventory as before, plus
   three "not fitted" entries.
4. With a PLANETAI node set: stop its broker, see the switch to Smart Citizen after
   three misses, start it again, see the node take over within ten minutes. Repeat
   with the fallback box off: no Smart Citizen connection at all.
5. Self-update: flash a CI build by cable, publish a second one, watch the node
   update and confirm itself. Then publish a build that never joins WiFi and watch
   it roll back after 30 minutes and stay back.

## Which board

Both the **Seeed XIAO ESP32-S3** and the **MakerGO ESP32-C3 SuperMini** run the same
sketch — the I²C pins are probed at boot rather than hard-coded, so nothing in the
file is chip-specific.

Set **Tools → USB CDC On Boot: Enabled** on either board, or `Serial` goes to the
UART pins and the monitor stays silent.

**ESP32-C3: set Tools → Partition Scheme → Minimal SPIFFS (1.9MB APP with OTA).** On
arduino-esp32 core 3.3.x, v3 and v4 are 1.34–1.36 MB and v5 is 1.50 MB, which no
longer fits the C3's default 1.25 MB app partition. Minimal SPIFFS also has the two
app slots the self-update needs. The XIAO ESP32-S3 default (3.3 MB) is fine.

If the upload fails with `No serial data received`, check which port you are
actually targeting before anything else. A board that enumerates as a USB
composite device can put a second `usbmodem` port on the list, and so can anything
else plugged into the same hub — the ESP32-S3 is the one that appears as
Espressif's *USB JTAG/serial debug unit* (VID `0x303A`).

## Setting up a node

The portal asks for WiFi, the Smart Citizen device token, where to publish, and a
name, site, mounting height and an indoors checkbox for the node. **Only the token
reaches Smart Citizen** — it is the node's entire publishing identity. The name and
site are local: they give the node an mDNS hostname and label its status page. A
device's display name and location on smartcitizen.me are set there, on the device
page; no MQTT topic carries them.

**Where it publishes.** The PLANETAI node first, then Smart Citizen. The four
broker fields describe the node: run `planetai broker` on that machine and type
what it prints, the machine's `.local` name or LAN address, port 1883, the broker
user and password. The node then hears every reading first, with this device's own
timestamp, and keeps it through an internet outage. If the node misses three
connections in a row, the sensor publishes to `mqtt.smartcitizen.me:8883` directly,
on the same topic with the same bytes, and tries the node again every ten minutes.
A box in the portal turns that off, for a sensor whose readings should only ever
reach the node. Leave the host blank and the sensor publishes to Smart Citizen only,
byte for byte what v3 sent. On the node,
`SC_FORWARD=<token>` passes the device's messages on to Smart Citizen unchanged, so
its page there and the campaign dashboard keep working; leave it blank and nothing
leaves the house. A device that will only ever talk to a PLANETAI node needs no
Smart Citizen account: any six characters make a token.

When the broker is a PLANETAI node, the node also publishes a retained
`device/sck/<token>/meta` message on every connection: name, site, height, indoors,
hardware variant and firmware version (v5 adds a `sensors` list of what is fitted, now including `pms5003`, `pms5003t`, `sht4x` and `scd4x`,
and two new `hardware` values, `msb-diy-node-sen5x` and `msb-diy-node-hm3301-sen5x`;
the v4 values are unchanged). The indoors checkbox is the one that matters:
a PLANETAI node never lets an indoor sensor into an outdoor average. None of this is
sent to Smart Citizen.

**For a workshop, set the token at kit prep and label the enclosure.** Pasting a
six-character token from a logged-in Smart Citizen device page, on a phone that is
currently joined to a captive portal, is the step that goes wrong. Do it once at the
bench and a participant only ever picks their WiFi and types its password.

**Or skip the typing with the setup page.** [makingsense.fablabbali.com/setup.html](https://makingsense.fablabbali.com/setup.html)
signs in to Smart Citizen, creates the device with a fresh token, and shows that
token as a QR code for `http://192.168.4.1/t?token=…`. Join the node's `MSB-Node-…`
network on a phone, scan the code: the node saves the token and opens the WiFi
picker with the token already filled in. The page then waits for the first reading
and links to the device page. The page has no server of its own; the browser talks
to `api.smartcitizen.me` directly. Source: [`setup.html`](../../../setup.html).
The `/t` route is in v5 and v3; v4 does not have it, so on v4 type the token.

On v5 the same QR can carry the PLANETAI node as well:
`http://192.168.4.1/t?token=…&host=…&port=1883&user=planetai&pass=…` saves all five
in one scan. Only `token` and `host` are needed; port defaults to 1883. Nothing
generates that QR yet, `planetai broker` could print one.

## Updates

A v5 node built by CI checks
[`flash/firmware/diy-node/manifest.json`](../../../flash/firmware/diy-node/manifest.json)
(v6 and later check [`flash/firmware/bayu/manifest.json`](../../../flash/firmware/bayu/manifest.json),
the channel the flasher serves) five minutes after it starts and then once a day, over HTTPS against the CA bundle
in the core. When the manifest names a build other than the one it runs, it
downloads that build's `app.bin` for its chip into the spare app slot and reboots.
Bootloader and partition table are never touched, and the saved settings stay.

**A new build is on probation until it reads the manifest again.** That one fetch
proves WiFi, DNS, TLS and the update path still work, which is what keeps the fleet
reachable for the next fix. If the new build crashes, or has not managed it after
30 minutes, the bootloader goes back to the old one on the next reboot, and the old
one remembers not to try that build again.

**Merging a change to `diy_node_v5/` into `main` updates the fleet.** The `firmware-build` workflow stamps each
build with its tag and refuses to publish an image that does not carry it, because
a node that cannot recognise its own build would reinstall it every day. A build
from the IDE carries no tag and never updates itself. The portal has a box to turn
updates off.

Nodes on a v5 build from before 24 Oct 2026 have no self-update. They need one
reflash by cable to get it.

## Retired sketches

Both are in [`previous/`](previous/), with a table of what each one asked for at
setup and how you reopened its portal.

- **[`previous/diy_node_v1.1/`](previous/diy_node_v1.1/)** — WiFi through the portal,
  token hardcoded in the source. One build per node.
- **[`previous/diy_node_v2/`](previous/diy_node_v2/)** — token moved into the portal.
  One image for the fleet. Lived only on a laptop as `bayu_sensor_wifimanager.ino`
  until now; v3 is built from it.

A v2 node reflashed with v3 keeps its WiFi and token — same NVS namespace, same key —
and comes up with the name fields empty. A v3 node reflashed with v4 or v5 keeps
everything and comes up publishing to Smart Citizen, as before, until somebody opens
its portal.

Two things v3, v4 and v5 carry forward unchanged, and they are limitations rather than
features: temperature and humidity are published **raw** (channels 237/238 are
labelled heat-compensated in the Smart Citizen catalogue, but nothing here
compensates — expect 1–3 °C high in an enclosure; the SEN5x's own T/RH on 203/204 is
published with its temperature offset at 0 and will read warm in an enclosure too),
and TLS runs with `setInsecure()`, which is fine for a workshop kit and not fine for
a sensor cited in policy work.
