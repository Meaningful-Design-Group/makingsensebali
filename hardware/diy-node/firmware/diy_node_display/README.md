# DIY Node — display build

*Firmware for the XIAO + Seeed Expansion Base + Grove Sensirion SEN5x.*

This is the local-first sibling of `../diy_node/diy_node.ino`. That one publishes
to Smart Citizen and you read the numbers on a website. This one puts them on the
OLED and writes them to the microSD, and does not need a network at all.

We built it after the August 2026 pipeline audit ([`docs/sensor-strategy.md`](../../../../docs/sensor-strategy.md)),
which found that nothing had ever been archived at full resolution and that three
jobs were racing to publish and overwriting each other. A node you can only read
through four network hops and a git push is a node you cannot trust in the field.

---

## ⚠️ Wire the power correctly or nothing works

**The SEN5x needs 5 V at 63–80 mA. The Expansion Base's Grove ports supply 3.3 V.**

Plugging the Grove SEN5x straight into a Grove I²C port does not work. You get an
I²C timeout, or — worse — a sensor that half-boots and returns plausible garbage.

The Expansion Base breaks out a 5 V rail on its **servo header**. Take the sensor's
VCC from there and leave everything else on the Grove port:

| SEN5x wire | Goes to |
|---|---|
| VCC (red) | **5 V servo header** |
| GND (black) | Grove GND |
| SDA (white) | Grove SDA |
| SCL (yellow) | Grove SCL |

The SEN5x's I²C lines are 3.3 V LVTTL, so there is no level-shifting to do. It is
purely a power problem.

**Check your board first.** Revisions differ — put a meter on the Grove VCC pin. If
it reads 5 V, ignore all of the above and just plug it in.

**Battery note.** That 5 V rail is USB VBUS. On the LiPo alone there is no 5 V, so
the SEN5x will not run. This node is USB-powered unless you add a boost converter.
The firmware detects the sensor's absence and says so on screen rather than
logging zeros.

## Bus map

Everything shares one I²C bus and nothing collides:

| Address | Device |
|---|---|
| 0x3C | SSD1306 OLED |
| 0x51 | PCF8563 RTC |
| 0x69 | SEN5x |
| 0x76 / 0x77 | BME680 (optional, auto-detected) |

Other pins: `D1` user button · `D2` SD chip select · `D8/D9/D10` SD SPI · `A3` buzzer.

The bus runs at **100 kHz** because that is the SEN5x maximum (standard mode). The
OLED would take 400 kHz happily but it shares the bus, which is why the screen
refreshes at 1 Hz. Don't raise `Wire.setClock()`.

## Flashing

Board: **XIAO_ESP32S3** (or XIAO_ESP32C3 — same sketch). Requires **arduino-esp32
core 3.x**; the sketch uses `tone()`, which core 2.x does not provide.

Libraries: U8g2 (olikraus). Adafruit BME680 + Adafruit Unified Sensor only if you
leave `ENABLE_BME680` on. ArduinoJson / PubSubClient / WiFiManager only if you turn
publishing on.

The SEN5x and PCF8563 are driven directly over I²C with no vendor library — same
reasoning as the HM3301 in the original sketch. The command words come from
Sensirion's own `embedded-i2c-sen5x` driver, just inlined.

## Feature flags

At the top of the sketch:

| Flag | Default | What it does |
|---|---|---|
| `PUBLISH_TO_SMARTCITIZEN` | `0` | MQTT upload. Off — that's the point of this build. |
| `LOG_TO_SD` | `1` | CSV to microSD, one file per day |
| `ENABLE_DETECTOR` | `1` | On-device burning detector + buzzer |
| `ENABLE_BME680` | `1` | Adds pressure + raw gas resistance if a BME680 is present |
| `DISPLAY_AUTO_CYCLE` | `1` | Pages advance on their own every 8 s |

## On the screen

Five pages. **Short press** the user button to advance, **long press (1.2 s)** to
mute or unmute the buzzer.

1. **Overview** — big PM2.5, detector state, temperature and humidity
2. **Particulates** — PM1 / 2.5 / 4 / 10, typical particle size, number concentrations
3. **Air + climate** — temperature, humidity, VOC index, NOx index (SEN55) or pressure
4. **Detector** — this hour's baseline, spread, sample count, current z and 60-min rise
5. **System** — sensor model and fault flags, SD status, RTC status, uptime

## Serial commands

115200 baud.

```
SETTIME 2026-08-21 14:32:00     set the RTC (local time)
FANCLEAN                        run the SEN5x fan cleaning cycle (~10 s)
BASELINE RESET                  wipe the learned baseline, restart warm-up
```

Set the clock once, fit the CR1220, and the node keeps time through power cuts.
Without a valid RTC, rows are written to `NOCLOCK.CSV` and timestamped
`NO_RTC+<seconds>` — greppable, so you can filter them out rather than mistake
them for real dates.

## The CSV

`/YYYYMMDD.CSV`, header written on creation, one row per minute. The file is
opened and closed per row: slower, but a yanked power cable costs you the current
row rather than the whole file.

```
timestamp,pm1,pm25,pm4,pm10,nc05,nc1,nc25,nc4,nc10,tps_um,
temp_c,rh_pct,voc_index,nox_index,pressure_kpa,gas_ohm,z,rise60,alert
```

Empty fields mean the sensor returned its "no valid value" sentinel. They are left
blank rather than filled with zeros, because a zero in a PM column is a real
reading and a missing one is not.

### One number to watch: `tps_um`

Typical particle size is scaled by **1000**, not 10. Our Smart Citizen kits publish
this channel with values of 39–58 "µm", which is physically impossible for ambient
aerosol — it looks like the factor-10 PM divisor applied to a factor-1000 channel,
i.e. exactly 100× too large. The real figure is around 0.4–0.6 µm, which is what
you'd expect where combustion aerosol dominates. **This node writes the correct
value.** If you compare its CSV against the platform's TPS channel, expect a 100×
discrepancy and trust this one.

## The detector

Not a threshold alarm. Thresholds don't work here: hourly PM2.5 above the WHO 24 h
guideline of 15 µg/m³ fired **4.55 times a day** at a comparatively clean Bali
site. An alarm that goes off four times a day is wallpaper.

Instead it scores each reading against a **learned baseline for that hour of the
day** and requires a **rate of rise** at the same time:

```
alert  when   z > 4      (deviations above this hour's normal)
        AND   rise > +15 µg/m³ over the last 60 minutes
        AND   sustained for 2 consecutive readings
clear  when   z < 2
```

Twenty-four hour-of-day slots, each an EWMA of the level and an EWMA of the
absolute deviation. Slots persist to NVS, so a power cut doesn't cost you the
learning. Readings taken *during* an alert are deliberately excluded from the
baseline update — letting an event teach the baseline that events are normal is
how these detectors go deaf.

There is **no particle-size composition gate**, and this is deliberate. We tried
it. During a confirmed burning event 150 m from one of our kits, PM2.5/PM10,
PM1/PM2.5 and PN0.5/PN10 all stayed inside their normal range — only magnitude
moved. Low-cost optical sensors derive the coarse bins from an assumed
distribution rather than measuring them. Don't add a composition gate back without
new evidence.

**What did work:** on that one event, this logic crossed threshold **47 minutes
before the first human reported it.**

### Honest limitations

- The thresholds come from **one** confirmed co-located event. There is no
  established detection rate and no false-positive rate.
- Expect roughly **one alert every two to three days**, most of which nobody will
  be able to explain. That is the current state of the evidence, not a bug.
- Give it a week before trusting it. Each hour-slot needs 60 readings before it
  will fire; page 4 shows the warm-up count.

Buzzer stays quiet 22:00–07:00, chirps at most once every 10 minutes during an
event, and long-pressing the button mutes it.

## Status

Compile-checked across all six feature-flag combinations. **Not yet run on
hardware** — the enclosure also needs a display window cut, which the current
v5 core doesn't have.
