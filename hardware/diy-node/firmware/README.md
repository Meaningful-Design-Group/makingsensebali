# Firmware

**Flash [`diy_node_v5/`](diy_node_v5/) once it has passed a bench check (below); until
then, [`diy_node_v4/`](diy_node_v4/).** One image serves the whole fleet — no
secrets in the source, WiFi and the Smart Citizen token entered through a captive
portal on a phone, and a status page on the local network so a node can be checked
without a laptop. v4 added one choice: where the node publishes. Left alone it goes to
Smart Citizen exactly as v3 did; pointed at a [PLANETAI node](https://planetai.fab.city)
on the same network it publishes there first, and the node passes the readings on.
v5 adds the other half of "one image": it works out which sensors are plugged in.

| Sketch | What it's for |
|---|---|
| [`diy_node_v5/`](diy_node_v5/) | **The production candidate.** v4 plus sensor auto-detect: HM3301, Sensirion SEN5x and BME680, in any combination. Compiled for XIAO ESP32-S3 and ESP32-C3 on core 3.3.12; not yet run on a board. |
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

The SEN5x IDs are the ones the Smart Citizen Kit 2.3 publishes the same part on
(`fablabbcn/smartcitizen-kit-2x`, `lib/Sensors/Sensors.h`), so a DIY node with a
SEN5x is directly comparable with the kits. The model is read from the sensor, and
channels a model doesn't have (SEN50: no T/RH/VOC; SEN54: no NOx) are simply not
published.

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

## Which board

Both the **Seeed XIAO ESP32-S3** and the **MakerGO ESP32-C3 SuperMini** run the same
sketch — the I²C pins are probed at boot rather than hard-coded, so nothing in the
file is chip-specific.

Set **Tools → USB CDC On Boot: Enabled** on either board, or `Serial` goes to the
UART pins and the monitor stays silent.

**ESP32-C3: set Tools → Partition Scheme → Minimal SPIFFS (1.9MB APP with OTA).** On
arduino-esp32 core 3.3.x, v3, v4 and v5 are all 1.34–1.36 MB, which no longer fits
the C3's default 1.25 MB app partition. The XIAO ESP32-S3 default (3.3 MB) is fine.

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

**Where it publishes.** Four fields: broker host, port, user, password. Blank or
`mqtt.smartcitizen.me:8883` is the Smart Citizen path, byte for byte what v3 sent.
To publish to a PLANETAI node instead, run `planetai broker` on that machine and
type what it prints: the machine's `.local` name or LAN address, port 1883, the
broker user and password. The node then hears every reading first, with this
device's own timestamp, and keeps it through an internet outage. On the node,
`SC_FORWARD=<token>` passes the device's messages on to Smart Citizen unchanged, so
its page there and the campaign dashboard keep working; leave it blank and nothing
leaves the house. A device that will only ever talk to a PLANETAI node needs no
Smart Citizen account: any six characters make a token.

When the broker is a PLANETAI node, the node also publishes a retained
`device/sck/<token>/meta` message on every connection: name, site, height, indoors,
hardware variant and firmware version (v5 adds a `sensors` list of what is fitted,
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
