# Bayu v3 · build your own

*For people who buy the parts themselves, print the case and flash the firmware. This is the plug-together build: no soldering. Allow an afternoon, plus delivery time for the parts. You need a computer with a USB-C port and access to a 3D printer.*

Received a finished sensor instead? See [SETUP-ASSEMBLED.md](SETUP-ASSEMBLED.md).

---

## 1. Buy the parts

Search terms are for Tokopedia. Shopee usually carries the same items.

| Part | Search for | Notes |
|---|---|---|
| Seeed XIAO ESP32-S3 | `XIAO ESP32S3` | About Rp 250–350k. The plain version; the *Sense* camera version works but costs more. It comes with a small antenna, which is enough indoors. |
| Grove Shield for XIAO | `Grove Shield XIAO` | The board the sensors plug into. Buy this one, because the case's bracket is shaped for it. |
| Seeed Grove Laser PM2.5 sensor (HM3301) | `Grove HM3301` | About Rp 450–600k, the most expensive part. If no local seller has it, ordering direct from Seeed takes about 3 weeks. |
| Seeed Grove BME680 | `Grove BME680` | Temperature, humidity, pressure, gas. Check the chip is marked **BME680**; sellers sometimes ship a BME280 or BMP280, which have no gas sensor. |
| 2 Grove cables | usually included with the sensors | |
| 5 V / 2 A USB-C wall charger and a USB-C cable | anywhere | Not a laptop port, which can't run the particle sensor's fan. |
| *Outdoors, optional:* SMA-to-U.FL pigtail and a 2.4 GHz SMA antenna | `pigtail ufl sma`, `antena wifi 2.4ghz sma` | For a sensor that hangs far from the router. |
| 2 cable ties (20–30 cm) or 2 wall screws | hardware shop | For mounting. |

A generic purple **BME680 breakout** (`GY-BME680`) also works and costs less. It needs a Grove-to-jumper cable instead of a plain Grove cable, and you print the "Bosch" sensor cover instead of the "Seeed" one.

## 2. Print the case

The files are in [`enclosure/node-v3.2/stl/`](enclosure/node-v3.2/stl/). Print **five** parts:

| Part | File |
|---|---|
| Main body | `MAIN_BODY_1_ANTENNA.stl` |
| Top cover | `TOP_COVER.stl` |
| PM sensor cover and board bracket | `COVER_HM3301_BRACKET_BOARD_GROVE_SHIELD.stl` |
| BME680 cover | `COVER_BME680_SEEED_STUDIO.stl` (or `COVER_BME680_BOSCH.stl` for the purple breakout) |
| Outflow duct | `OUTFLOW_DUCT_HM3301.stl` |

**Use PETG or ASA, not PLA.** PLA softens and warps on a sunny Bali wall.

We haven't published tested print settings yet. As a starting point, use 0.2 mm layers, 3–4 walls and 20–30 % infill. Lay each part on its largest flat face, because the files come in assembled orientation and you'll need to rotate them in the slicer. The case closes with snap-fit hooks rather than screws, and a hook printed with its layer lines running across its base snaps off the first time you press it. Print one set, test the fit, then print the rest. If you land on settings that work, please send them to us.

## 3. Flash the firmware

1. Install the [Arduino IDE](https://www.arduino.cc/en/software). In **Boards Manager**, install **esp32 by Espressif Systems**.
2. In **Library Manager**, install **WiFiManager** by tzapu (tested with 2.0.17), **Adafruit BME680 Library** (it will ask to add *Adafruit Unified Sensor*: yes), **PubSubClient** by Nick O'Leary, and **ArduinoJson** version 7.
3. Download this repository. Open [`firmware/diy_node_test/diy_node_test.ino`](firmware/diy_node_test/) first.
4. Choose **Tools → Board → XIAO_ESP32S3**, and set **Tools → USB CDC On Boot → Enabled**. Without that setting the Serial Monitor stays silent.
5. Plug the XIAO in, choose its port, and upload. If the upload fails with *No serial data received*, you probably have the wrong port selected: pick the one that belongs to the XIAO.

Keep the test sketch on for now. You'll use it in step 4.

## 4. Put it together

1. **Plug the XIAO into the Grove Shield**, with the USB-C port at the shield's edge.
2. **Plug both sensors into the shield's I²C Grove ports** (they share the same bus, so either port works for either sensor).
3. **Test before you close anything.** Connect USB, open **Tools → Serial Monitor** at **115200** baud, and check that both sensors appear with sensible readings. If one is missing, reseat its cable. Only go on once both show up.
4. **Upload the real firmware.** Open [`firmware/diy_node_v3/diy_node_v3.ino`](firmware/diy_node_v3/) and upload it with the same settings. It contains no passwords or tokens; you'll enter those from your phone.
5. **Assemble the case.** No screwdriver needed.
   - If you're using an external antenna, fit the pigtail through the hole in the body, tighten the nut, and clip the other end onto the XIAO's antenna socket.
   - Drop the BME680 into its pocket in the floor of the body and press its cover down until it clicks.
   - Seat the PM sensor in its compartment, fit the outflow duct into the exhaust channel, and press the PM cover over it until its hooks click.
   - Press the shield with the XIAO onto the hooks on top of the PM cover. Route the USB cable out.
   - Press the top cover down on all four sides until it clicks.

   Pictures of each step: [`enclosure/node-v3.2/README.md#assembly`](enclosure/node-v3.2/README.md#assembly).

## 5. Register, connect and hang it

From here it's exactly the same as a sensor we send out assembled. Follow [SETUP-ASSEMBLED.md](SETUP-ASSEMBLED.md) from **step 2**: register the device on Smart Citizen to get its token, join the `MSB-Node-xxxxxx` WiFi from your phone (password `makingsense`), enter your WiFi and the token, check the status page, and hang it.

Once it's live, tell the WhatsApp community and put it on the site card. New sensors run for a week next to a reference sensor before the campaign leans on their numbers.

---

## Known limits, before you rely on the numbers

- **Temperature reads 1 to 3 °C high**, and humidity correspondingly low, because the electronics warm the box. We correct it in the data, not in the sensor.
- **This case hasn't yet been compared side by side with a reference sensor.** PM2.5 is the number that matters, and short spikes may read a little low until we've measured how the case affects airflow.
- **The case's CAD source isn't published yet**, only the STL files, so it can't be modified easily. Full design notes, wiring for other boards, and the open issues are in [`enclosure/node-v3.2/`](enclosure/node-v3.2/) and [`README.md`](README.md).

*Making Sense Bali · Fab Lab Bali · Fab City Bali · Hardware CERN-OHL-W-2.0 · Docs CC-BY-SA-4.0*
