# Drawing conventions

Every circuit drawing for Bayu follows this page: the four variants, the breadboard views,
the Bayu Core connector maps and the schematics. If a drawing and this page disagree, the
drawing is wrong. Change this page first, then regenerate with `draw_circuits.py`.

## One Bayu Core board

There is one Core board. A variant leaves parts unfitted, it never renames or moves them.

| Ref | Part | Nets |
|---|---|---|
| U1 | XIAO ESP32-S3, in 2 × 7 female headers | all |
| U2 | Wio-SX1262, clipped on top of U1 through the board-to-board connector | LoRa SPI, GPIO 38 to 42 |
| J1 | SEN54 socket, JST GH 1.25 mm 6-pin | 1 `+5V_F`, 2 `GND`, 3 `I2C_SDA`, 4 `I2C_SCL`, 5 `GND` (SEL, I2C mode), 6 not connected |
| J2 | Plantower socket, Molex PicoBlade 1.25 mm 8-pin | 1 `+5V_F`, 2 `GND`, 3 `PMS_SET`, 4 `UART_TX`, 5 `UART_RX`, 6 RESET open, 7 and 8 not connected |
| J3 | Grove I2C socket A | 1 `I2C_SCL`, 2 `I2C_SDA`, 3 `3V3`, 4 `GND` |
| J4 | Grove I2C socket B | same as J3 |
| J5 | Grove GPIO socket | 1 `LED_DIN` (D1, after R3), 2 `BTN` (D0), 3 `3V3`, 4 `GND` |
| J6 | 5 V input from the Bayu Power board, JST PH 2-pin | 1 `+5V_IN`, 2 `GND` |
| F1 | Resettable fuse, 1 A | `+5V_USB` to `+5V_F` |
| CR1 | Schottky diode | `+5V_IN` to `+5V_USB`, so USB power never flows back into the Power board, as Seeed asks for any external 5 V on the XIAO's 5V pin |
| JP1 | Solder jumper, open by default | connects R1 and R2 |
| R1, R2 | 4.7 kΩ | I2C pull-ups to `3V3` through JP1, for a bare SEN54 only |
| R3 | 330 Ω | in series on `LED_DIN`, fitted on every variant |

J5 puts the LED on pin 1 because a stock Grove module takes its signal on pin 1, so Seeed's
Grove RGB LED plugs straight in. The button on pin 2 is a bare switch to GND, on a split
cable. Most nodes don't need it: the XIAO has its BOOT button and the Wio-SX1262 has its own.

PMS5003 RESET (J2 pin 6) is left open: the sensor pulls SET and RESET up inside. There is no
resistor on it.

### Layout

The board is 60 × 40 mm, drawn at 12 px per mm. U1 sits left of centre with USB-C at the
left edge. J6, CR1 and F1 sit along the top-left edge, J1 top-right, J2 bottom-right, J3 and
J4 on the right edge, J5 bottom-left with R3 beside it, JP1 with R1 and R2 next to J3. The
antenna pigtail from U2 leaves upwards.

### Per variant

| Ref | Bayu v3 | Anchor | Dense | Indoor | Relay |
|---|---|---|---|---|---|
| U2 Wio-SX1262 | optional | fitted | optional | — | fitted |
| J1 SEN54 | — | SEN54 | — | — | — |
| J2 Plantower | — | PMS5003 | PMS5003T | PMS5003 | — |
| J3 Grove I2C | BME680 | SHT40 | — | SCD40 | SHT40 |
| J4 Grove I2C | HM3301 | — | — | SHT40 | — |
| J5 Grove GPIO | optional | optional | optional | optional | optional |
| JP1 | open | closed for a bare SEN54 | open | open | open |
| R1, R2 | fitted | fitted | fitted | fitted | fitted |
| R3, F1 | fitted | fitted | fitted | fitted | fitted |
| J6, CR1 | only with the Power board | same | same | same | same |

Unfitted parts are drawn in grey outline, labelled "not fitted".

## Net names

From the XIAO's point of view.

| Net | XIAO pin | Meaning |
|---|---|---|
| `+5V_USB` | 5V (VBUS) | USB 5 V |
| `+5V_F` | | after F1, feeds J1 and J2 |
| `+5V_IN` | | from J6, before CR1 |
| `3V3` | 3V3 | XIAO regulator output |
| `GND` | GND | |
| `I2C_SDA` | D4, GPIO5 | |
| `I2C_SCL` | D5, GPIO6 | |
| `UART_TX` | D6, GPIO43 | to PMS RXD |
| `UART_RX` | D7, GPIO44 | from PMS TXD |
| `PMS_SET` | D2, GPIO3 | high or open = running |
| `BTN` | D0, GPIO1 | to GND, internal pull-up |
| `LED_DIN` | D1, GPIO2 | WS2812 data, through R3 |
| `VBAT_SENSE` | D3, GPIO4 | Power board only |
| `LORA_SPI` | D8 to D10, GPIO 7, 8, 9 | taken by U2 |

## Schematic references

| Ref | Part |
|---|---|
| U1 | XIAO ESP32-S3 |
| U2 | Wio-SX1262 |
| U3 | SEN54 |
| U4 | PMS5003 or PMS5003T |
| U5 | SHT40 |
| U6 | SCD40 |
| U7 | WS2812B |
| SW1 | Button |

## Wire colours

One colour per net on every sheet, in the breadboard views, the Core maps and the
schematics.

| Net | Colour | Hex |
|---|---|---|
| `+5V_USB`, `+5V_F`, `+5V_IN` | red | `#d0312d` |
| `3V3` | orange | `#ef7d00` |
| `GND` | black | `#1d2433` |
| `I2C_SDA` | blue | `#1f5fbf` |
| `I2C_SCL` | yellow, dark outline | `#e6b400` |
| `UART_TX` | light green | `#4cae4f` |
| `UART_RX` | dark green | `#1b6b3a` |
| `PMS_SET` | purple | `#7a3fb3` |
| `BTN` | grey | `#8a8f99` |
| `LED_DIN` | pink | `#d63384` |
| `VBAT_SENSE` | teal | `#2a9d8f` |
| `LORA_SPI` and U2's lines | slate | `#4a5873` |
| antenna coax | brown, dashed | `#8a5a2b` |

Breadboard rails: the top pair is `+5V_USB` (red stripe) and `GND`, the bottom pair is
`3V3` (orange stripe) and `GND`. A red stripe always means 5 V.

## Sheet layout

- Canvas 1100 px wide. Height as needed.
- Title top-left: "Bayu Variant · Drawing type", 26 px bold, then a one-line subtitle.
- Legend in a box at the top right, same position on every sheet.
- No text smaller than 13 px. Labels are horizontal, never rotated.
- XIAO pin labels read "D4 · GPIO5" on schematics and Core maps. On the breadboard the
  2.54 mm pitch only fits them on two lines, D4 above GPIO5.
- Breadboard: a half-size board, 30 columns, rows a to j with row a at the top. The XIAO
  straddles the centre channel with USB-C to the left, its pins in rows b and g. Its top edge, left to right, is 5V,
  GND, 3V3, D10, D9, D8, D7. Its bottom edge is D0 to D6.
- Footer stamp, 52 px, on every sheet: variant, drawing type, revision date, licence and
  source.
