# Firmware

**Flash [`diy_node_v3/`](diy_node_v3/).** One image serves the whole fleet — no
secrets in the source, WiFi and the Smart Citizen token entered through a captive
portal on a phone, and a status page on the local network so a node can be checked
without a laptop.

| Sketch | What it's for |
|---|---|
| [`diy_node_v3/`](diy_node_v3/) | **The production sketch.** Flash this. |
| [`diy_node_test/`](diy_node_test/) | Verification only. Scans I²C, probes both sensors, prints to Serial every 5 s. No WiFi, no MQTT, no Smart Citizen account. What a participant flashes straight after soldering. |
| [`diy_node_display/`](diy_node_display/) | The variant driving the XIAO Expansion Base OLED. |
| [`previous/`](previous/) | Retired. Kept for history, not for flashing. |

## Which board

Both the **Seeed XIAO ESP32-S3** and the **MakerGO ESP32-C3 SuperMini** run the same
sketch — the I²C pins are probed at boot rather than hard-coded, so nothing in the
file is chip-specific.

Set **Tools → USB CDC On Boot: Enabled** on either board, or `Serial` goes to the
UART pins and the monitor stays silent.

If the upload fails with `No serial data received`, check which port you are
actually targeting before anything else. A board that enumerates as a USB
composite device can put a second `usbmodem` port on the list, and so can anything
else plugged into the same hub — the ESP32-S3 is the one that appears as
Espressif's *USB JTAG/serial debug unit* (VID `0x303A`).

## Setting up a node

The portal asks for WiFi, the Smart Citizen device token, and a name, site and
mounting height for the node. **Only the token reaches Smart Citizen** — it is the
node's entire publishing identity. The name and site are local: they give the node
an mDNS hostname and label its status page. A device's display name and location on
smartcitizen.me are set there, on the device page; no MQTT topic carries them.

**For a workshop, set the token at kit prep and label the enclosure.** Pasting a
six-character token from a logged-in Smart Citizen device page, on a phone that is
currently joined to a captive portal, is the step that goes wrong. Do it once at the
bench and a participant only ever picks their WiFi and types its password.

## Retired sketches

Both are in [`previous/`](previous/), with a table of what each one asked for at
setup and how you reopened its portal.

- **[`previous/diy_node_v1.1/`](previous/diy_node_v1.1/)** — WiFi through the portal,
  token hardcoded in the source. One build per node.
- **[`previous/diy_node_v2/`](previous/diy_node_v2/)** — token moved into the portal.
  One image for the fleet. Lived only on a laptop as `bayu_sensor_wifimanager.ino`
  until now; v3 is built from it.

A v2 node reflashed with v3 keeps its WiFi and token — same NVS namespace, same key —
and comes up with the name fields empty.

Two things v3 carries forward unchanged, and they are limitations rather than
features: temperature and humidity are published **raw** (channels 237/238 are
labelled heat-compensated in the Smart Citizen catalogue, but nothing here
compensates — expect 1–3 °C high in an enclosure), and TLS runs with
`setInsecure()`, which is fine for a workshop kit and not fine for a sensor cited
in policy work.
