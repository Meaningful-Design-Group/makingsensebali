# Changelog

What changed in the Bayu node design and documentation, newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Dates are WITA.

## 2026-10-24

### Added

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

- The HM3301 supply. The node-v3.2 README and bill of materials say it needs 5 V. Its own
  wiring drawing powers it from a 3V3 Grove socket, and Seeed rates it for both.
- Whether the Grove SEN54 runs on 3.3 V, as one review says.
- KiCad source for the Bayu Core board. It is specified in DESIGN.md and not drawn yet.
- No drawing has been checked against a built node.
