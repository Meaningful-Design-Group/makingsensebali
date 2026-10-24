# Changelog

What changed in the Bayu node design and documentation, newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Dates are WITA.

## 2026-10-24

### Added

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
