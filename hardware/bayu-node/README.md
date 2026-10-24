# Bayu node

Bayu is the next air quality node for Making Sense Bali, after the DIY node. It runs on the
same Seeed XIAO ESP32-S3. The sensors change: a Sensirion SEN54 and Plantower PMS5003 or
PMS5003T for particulate matter, an SHT40 for temperature and humidity, and an SCD40 for CO₂
indoors. Every node has WiFi. Where WiFi doesn't reach, nodes talk to each other over LoRa
with Meshtastic, through the Wio-SX1262 board that clips on top of the XIAO.

It is one board, fitted four different ways depending on what you want to measure and
where. Every kit stays under USD 100.

Why the design is the way it is, the costs, where to buy parts in Indonesia and elsewhere,
and the firmware plan are in [DESIGN.md](DESIGN.md). This page is the map of the drawings.

> Nothing here has been built yet. Every drawing was checked against the datasheets, the
> Seeed schematic and the firmware source, but none against a stack on the bench. If you
> build one, tell us what is wrong.

## The four variants

| | Sensors | Where it goes | Kit, USD | Firmware |
|---|---|---|---|---|
| [**Anchor**](circuits/anchor/) | SEN54, PMS5003, SHT40, LoRa | One per cluster, outdoors. The local reference the cheap nodes are corrected against. | about 91 | Meshtastic, Bayu image |
| [**Dense**](circuits/dense/) | PMS5003T, LoRa optional | Many, on kos rooms, warungs and family compounds, put up by workshop participants. | about 52, 58 with LoRa | Meshtastic `_t` image, or Smart Citizen v5 |
| [**Indoor**](circuits/indoor/) | PMS5003, SCD40, SHT40 | Classrooms, kos rooms, kitchens with a mosquito coil going. | about 70 | Smart Citizen v5 or Meshtastic |
| [**Relay**](circuits/relay/) | SHT40, LoRa | Only where a cluster has no node with WiFi. Carries the mesh to the internet. | about 36 to 40 | Meshtastic, Bayu image |

A fifth variant, Mobile, with GPS and a battery for transects on a motorbike, is in the
design and comes later.

### Anchor

SEN54 and PMS5003 side by side, breathing the same air, so every PMS5003 in the cluster
can be corrected against it. Its first week is next to a Smart Citizen Kit.

<table>
<tr>
<td width="50%"><a href="circuits/anchor/wiring-breadboard.svg"><img src="circuits/anchor/wiring-breadboard.svg" alt="Anchor breadboard wiring"></a></td>
<td width="50%"><a href="circuits/anchor/placement.svg"><img src="circuits/anchor/placement.svg" alt="Anchor placement"></a></td>
</tr>
<tr><td>Breadboard wiring</td><td>Placement</td></tr>
</table>

[Schematic](circuits/anchor/schematic.svg) · [Core connector map](circuits/anchor/wiring-core.svg) · [Pins, parts and placement rules](circuits/anchor/)

### Dense

The cheap one, with five wires between the PMS5003T and the XIAO. The placement sheet
uses pictograms so a resident can follow it without reading English.

<table>
<tr>
<td width="50%"><a href="circuits/dense/wiring-breadboard.svg"><img src="circuits/dense/wiring-breadboard.svg" alt="Dense breadboard wiring"></a></td>
<td width="50%"><a href="circuits/dense/placement.svg"><img src="circuits/dense/placement.svg" alt="Dense placement"></a></td>
</tr>
<tr><td>Breadboard wiring</td><td>Placement</td></tr>
</table>

[Schematic](circuits/dense/schematic.svg) · [Core connector map](circuits/dense/wiring-core.svg) · [Pins, parts and placement rules](circuits/dense/)

### Indoor

PM, CO₂ and climate for a room. Placement matters as much as wiring here: breathing
height, a metre from people, away from the AC and the stove, and fresh air once a week so
the SCD40 can calibrate itself.

<table>
<tr>
<td width="50%"><a href="circuits/indoor/wiring-breadboard.svg"><img src="circuits/indoor/wiring-breadboard.svg" alt="Indoor breadboard wiring"></a></td>
<td width="50%"><a href="circuits/indoor/placement.svg"><img src="circuits/indoor/placement.svg" alt="Indoor placement"></a></td>
</tr>
<tr><td>Breadboard wiring</td><td>Placement</td></tr>
</table>

[Schematic](circuits/indoor/schematic.svg) · [Core connector map](circuits/indoor/wiring-core.svg) · [Pins, parts and placement rules](circuits/indoor/)

### Relay

The Relay has no PM sensor. The whip goes above the roof ridge and the SHT40 goes low in
the shade. Its README also has the Meshtastic settings every node in a cluster needs.

<table>
<tr>
<td width="50%"><a href="circuits/relay/wiring-breadboard.svg"><img src="circuits/relay/wiring-breadboard.svg" alt="Relay breadboard wiring"></a></td>
<td width="50%"><a href="circuits/relay/placement.svg"><img src="circuits/relay/placement.svg" alt="Relay placement"></a></td>
</tr>
<tr><td>Breadboard wiring</td><td>Placement</td></tr>
</table>

[Schematic](circuits/relay/schematic.svg) · [Core connector map](circuits/relay/wiring-core.svg) · [Pins and Meshtastic settings](circuits/relay/)

## Pins, the same on every variant

A variant only leaves pins empty. No pin changes job between variants, so one Core board
and one firmware image serve all four.

| XIAO | GPIO | Job | Anchor | Dense | Indoor | Relay |
|---|---|---|---|---|---|---|
| 5V | VBUS | 5 V for the PM sensors' fans | ● | ● | ● | |
| 3V3 | | 3.3 V for the I²C sensors and the LED | ● | ● | ● | ● |
| D4 | 5 | I²C SDA | ● | | ● | ● |
| D5 | 6 | I²C SCL | ● | | ● | ● |
| D6 | 43 | UART TX to the PMS RXD | ● | ● | ● | |
| D7 | 44 | UART RX from the PMS TXD | ● | ● | ● | |
| D2 | 3 | PMS SET, fan sleep | ● | ● | ● | |
| D0 | 1 | button | ○ | ○ | ○ | ○ |
| D1 | 2 | WS2812 status LED | ○ | ○ | ○ | ○ |
| D3 | 4 | battery sense, Power board only | ○ | | | |
| D8 to D10 | 7, 8, 9 | LoRa SPI, taken by the Wio-SX1262 | ● | ○ | | ● |

● wired · ○ optional

The Smart Citizen firmware v5 only listens to the PMS on D7. The Meshtastic Bayu image also
uses D6 and D2 to sleep the fan between readings. Wire all three and the same node runs
either.

## Before you solder

- Solder the header into the XIAO only. The Wio-SX1262 clips on top of the XIAO, and its
  edge pads sit right over D0 to D4 carrying radio lines. Trim the stubs flush before the
  Wio goes on, because one pin through both boards ties the button, the LED, SET and SDA
  to the radio.
- Buy the XIAO and the Wio as Seeed's kit. The board-to-board radio is only sold that way,
  and a plain XIAO may come without the connector fitted.
- Put the antennas on before you power it. The SX1262 can be damaged transmitting into an
  open connector.

## Firmware

- Meshtastic with the Bayu sensors: branch `bayu` of
  [Meaningful-Design-Group/firmware](https://github.com/Meaningful-Design-Group/firmware/tree/bayu),
  build envs `seeed_xiao_s3_bayu` and `seeed_xiao_s3_bayu_t` for the PMS5003T. How to build,
  flash and set the region is in `BAYU.md` on that branch.
- Smart Citizen v5, which also reads the PMS5003, PMS5003T, SHT4x and SCD4x:
  [`../diy-node/firmware/diy_node_v5/`](../diy-node/firmware/diy_node_v5/).

## Folders

```
bayu-node/
├── README.md       this page
├── DESIGN.md       the design: roles, boards, costs, sourcing, mesh, firmware
└── circuits/
    ├── anchor/     ┐
    ├── dense/      │ each: wiring-breadboard.svg, wiring-core.svg,
    ├── indoor/     │ schematic.svg, placement.svg, README.md
    └── relay/      ┘
```

Hardware is CERN-OHL-W-2.0, documentation CC-BY-SA-4.0, software MIT, as for the
[DIY node](../diy-node/enclosure/LICENSES/).
