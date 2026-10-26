# Changelog

What changed in the Bayu node design and documentation, newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Dates are WITA.

## 2026-10-24

### Added

- Bayu firmware v6, in `../diy-node/firmware/diy_node_v6/`: v5 plus automatic detection of
  the Expansion Base, with the Fab City logo, readings and ISPU-based PM2.5 and CO2 alarms on
  the screen and buzzer, a microSD log, the clock, and a status LED. Not published by CI and
  not yet run on a board.
- `expansion-base/`: Bayu on Seeed's Expansion Base for XIAO. Bayu v3 on two Grove cables,
  and the three-PM node with no soldering, taking 5 V from the board's two 5V points. Pin
  map against Bayu, other variants, and a drawing with its generator.
- `seeed-proposal/`, replacing `grove-shield-mini/`: the Expansion Base already has the
  clock, microSD and four sockets the Mini proposed, so the ask to Seeed is now one 3V3 or
  5 V jumper on the UART socket and one I2C socket of the Grove Shield and the Expansion
  Base. New drawing and generator; the Mini concept is in git history.
- `grove/v3-three-pm/`, plug-in version: two Grove adapter leads with a 5 V module, a
  fixed buck-boost or an MT3608 from Tokopedia, so the bare SEN54 and the PMS5003 plug into
  Grove sockets, plus a Grove I2C hub for the third I2C sensor. Drawing and generator, parts,
  how to make and test a lead, and the 3V3 current budget.
- `grove/v3-three-pm/`: Bayu v3 on the Grove Shield with a bare SEN54 and a PMS5003 next to
  its HM3301, for comparing the three PM sensors in the field. Wiring drawing and its
  generator, connections, parts and build steps.
- `circuits/CONVENTIONS.md`: one Bayu Core with fixed designators J1 to J6, F1, CR1, JP1 and
  R1 to R3, one set of net names, schematic references U1 to U7 and one colour per net.
- `circuits/draw_circuits.py`: the breadboard, Core and schematic sheets of all four
  variants now come from this one script, which also checks itself for small text,
  overlapping labels and wires through labels.
- `bom.csv`: every part of the four new variants, in the same Open-Make columns as the
  [node-v3.2 bill of materials](../diy-node/enclosure/node-v3.2/bom.csv), with a `used_in`
  column. Bayu v3's own parts stay in that file.
- `LICENSES/` with the CERN-OHL-W-2.0, CC-BY-SA-4.0 and MIT texts, and a licence table on
  the Bayu page.
- The scripts that generate the Grove map and the Grove Shield Mini drawings, next to the
  drawings they make.
- Stage, audience and contact on the Bayu page.
- `grove/`: every variant mapped onto the Seeed Grove Shield for XIAO, from Seeed's pinout.
- `grove-shield-mini/`: the board proposed to Seeed, with a concept drawing.
- `circuits/`: breadboard wiring, Core connector map, schematic and placement drawings for
  Anchor, Dense, Indoor and Relay.
- `DESIGN.md` and the Bayu page.

### Fixed

- The HM3301 supply is settled from Seeed's [schematic](https://wiki.seeedstudio.com/Grove-Laser_PM2.5_Sensor-HM3301/) for the Grove HM3301: a
  step-down to 3.0 V and a step-up to 5 V on the board, so it runs from a 3.3 V or a 5 V
  socket. The node-v3.2 and node-v3.1 READMEs, in all three languages, and their bills of
  materials had called the 3.3 V in Fab Lab Bali's Grove Shield table an error. They now
  say the table was right. The board's 4.7 kΩ I2C pull-ups also answer the pull-up check
  in `grove/v3-three-pm/`.
- The docs called the node's own firmware "Smart Citizen v5". It is the Bayu firmware, v5 in
  [`../diy-node/firmware/`](../diy-node/firmware/); Smart Citizen is one of the platforms it
  publishes to. DESIGN.md also said that firmware stays on the old node and is not carried
  forward, when it already reads every Bayu sensor.
- A design review of the drawings found the Core drawn as four different boards: different
  designators, socket positions and USB-C direction, R1 meaning three different parts, a
  RESET pull-up on Dense only, and the LED resistor on Relay only. Wire colours also
  changed meaning between sheets, and text came out as small as 5 px on GitHub. The twelve
  circuit sheets were regenerated from the conventions.
- J5 now has the LED on pin 1 and the button on pin 2, so a stock Grove RGB LED plugs in.
  The first conventions had them the other way round.
- The placement sheets: every line at least 13 px at GitHub width, Bahasa on every Dense
  card, a pictogram for "sensor temperature is not air temperature", and keep-away rings
  drawn around the sources on all four sheets.
- The Grove Shield Mini put its microSD chip select on D1, where every Bayu variant has its
  status LED. The chip select moved to D0, the LED stays on D1 on the board, and the button
  is the XIAO's BOOT button. The proposal now says Bayu needs one build flag for the Mini,
  where it had claimed no firmware change.
- The Grove map counted one 5 V wire for the Anchor. A bare SEN54 makes it two. It also now
  says the D2 socket for the Plantower SET line is on the half that snaps off.
- Bayu was described as a new node after the DIY node. Bayu is the deployed node, Bayu v3,
  and the four variants are additions to it.
- The Relay drawings first had the XIAO and Wio-SX1262 stack the wrong way round. The Wio
  rides on top, so the stack goes into a breadboard pins-down, with the header in the XIAO
  only.
- DESIGN.md said the LoRa board takes no D pins. It takes D8 to D10 for SPI.
- DESIGN.md named `ROUTER_CLIENT` for the Relay. It is deprecated; a Relay with WiFi uses
  `CLIENT`.
- DESIGN.md planned the bridge on Meshtastic's MQTT JSON, which firmware 2.8.0 removed. The
  bridge decodes protobuf.
- The Dense and Relay drawings rendered as thumbnails on GitHub because their SVGs carry no
  size. The page now gives every image a width.

### Open

- Whether the Grove SEN54 runs on 3.3 V, as one review says.
- KiCad source for the Bayu Core board. It is specified in DESIGN.md and not drawn yet.
- No drawing has been checked against a built node.
