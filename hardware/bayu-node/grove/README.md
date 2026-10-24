# Bayu on the Grove Shield

How every Bayu variant goes together on the
[Seeed Grove Shield for XIAO](https://wiki.seeedstudio.com/Grove-Shield-for-Seeeduino-XIAO-embedded-battery-management-chip/),
with Grove cables and no soldering beyond the XIAO's header. Fab Lab Bali already builds
Bayu v3 on this shield, and it is part of the kit we have discussed with Seeed.

![Bayu on the Seeed Grove Shield for XIAO: socket map and which module goes where](grove-shield-map.svg)

## What the shield gives you

Eight Grove sockets, all powered at 3V3: two I2C, one UART, and five digital ones on D0,
D1, D2, D8 and D9. The board snaps in two. The half that keeps the XIAO has the D0, D1,
I2C and UART sockets, which is enough for every Bayu variant except the ones with two I2C
sensors and a Plantower.

The pin map is the same as Bayu's. I2C is on D4 and D5, the PMS5003 UART on D6 and D7, its
SET line on D2, the button on D0 and the LED on D1, so the same firmware runs on the
shield and on the Bayu Core board.

With the Wio-SX1262 fitted for LoRa, the D8 and D9 sockets are gone, because D8 to D10 are
the radio's SPI bus. Everything else stays usable. Solder the header into the XIAO only
and trim the stubs, as for any Bayu with LoRa.

## Variant by variant

**Bayu v3, the node deployed today,** is fully plug and play: Grove BME680 in one I2C
socket, Grove HM3301 in the other.

**Relay** is plug and play too: a Grove SHT40 in an I2C socket and the LoRa stack.

**Anchor, Dense and Indoor** each carry a Plantower PMS5003 or PMS5003T, and that breaks
plug and play in two ways. There is no Grove PMS5003, so its 8-pin 1.25 mm cable needs a
Grove adapter cable for the UART socket, plus one more wire to the D2 socket if you want
the fan to sleep between readings. And its fan needs 5 V, which no socket on this shield
gives, so one wire goes from the PMS VCC to the shield's 5V header pin.

On the Anchor, the Grove SEN54 takes one I2C socket and the Grove SHT40 the other. One
review says Seeed fitted the Grove SEN54 with a regulator so it runs on 3.3 V. We have not
tested that yet. The bare Sensirion SEN54 needs 5 V and would need the same wire as the
Plantower.

On Indoor, Seeed's Grove CO2 module is the SCD41, not the SCD40 in the design. It sells
for USD 55 to 65 at retail against about 22 for an SCD40 breakout, which pushes the Indoor
kit past USD 100.

## Check on the bench first

- **The HM3301 supply:** Seeed rates the Grove HM3301 at 3.3 or 5 V, and the deployed
  nodes run it on the socket's 3V3, as the
  [node-v3.2 breadboard drawing](../../diy-node/enclosure/node-v3.2/img/10-breadboard-grove-shield.png)
  shows. The [node-v3.2 README](../../diy-node/enclosure/node-v3.2/README.md#wiring) says
  it needs 5 V. One of the two is wrong. A side-by-side run of two units, one per supply,
  settles it.
- **The 3V3 budget:** the XIAO's regulator feeds every socket. An Indoor node with an SCD41
  peaking around 200 mA and the WiFi radio transmitting is close to its limit.

## What would make it all plug and play

A Grove socket that can switch to 5 V, and a Grove cable for the Plantower. Both are in the
[Grove Shield Mini proposal](../grove-shield-mini/).
