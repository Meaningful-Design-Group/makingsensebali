# DIY Node — display build

*Firmware for the XIAO + Seeed Expansion Base + Grove HM3301 + Grove BME680.*

This is the local-first sibling of [`../diy_node/diy_node.ino`](../diy_node/diy_node.ino).
Same two sensors, opposite priorities. That one publishes to Smart Citizen and
you read the numbers on a website; this one puts them on the OLED and writes
them to the microSD, and needs no network at all.

We built it after the August 2026 pipeline audit ([`docs/sensor-strategy.md`](../../../../docs/sensor-strategy.md)),
which found that nothing had ever been archived at full resolution and that
three jobs were racing to publish and overwriting each other. A node you can
only read through four network hops and a git push is a node you cannot trust
in the field.

---

## Wiring: two Grove cables, nothing else

Both sensors are 3.3 V I²C parts and the Expansion Base has **two** Grove I²C
ports. One sensor in each. No soldering, no modified cables, no external
supply.

| Port | Sensor |
|---|---|
| Grove I²C #1 | HM3301 |
| Grove I²C #2 | BME680 |

> An earlier revision of this sketch targeted the Sensirion SEN5x. That part
> needs 5 V at 63–80 mA while the Grove ports supply 3.3 V, so it needed VCC
> taken off the servo header with a modified cable — and it wouldn't run on
> battery at all, since the 5 V rail is just USB VBUS. Dropped in favour of
> parts that plug straight in. It's in the git history if you want it.

## Bus map

Everything shares one I²C bus and nothing collides:

| Address | Device |
|---|---|
| 0x3C | SSD1306 OLED |
| 0x40 | HM3301 |
| 0x51 | PCF8563 RTC |
| 0x76 or 0x77 | BME680 (both tried at boot) |

Other pins: `D1` user button · `D2` SD chip select · `D8/D9/D10` SD SPI · `A3` buzzer.

The bus runs at **100 kHz**. The HM3301 datasheet doesn't state a maximum I²C
clock and the sensor has a reputation for being fussy, so we stay in standard
mode rather than gamble. A full 128×64 OLED frame takes ~92 ms at that rate,
which is why the screen refreshes at 1 Hz. If you raise `Wire.setClock()` and
PM frames start failing checksum, that's why.

## Flashing

Board: **XIAO_ESP32S3** or **XIAO_ESP32C3** — same sketch. Requires
**arduino-esp32 core 3.x**; the sketch uses `tone()`, which core 2.x does not
provide.

Libraries: U8g2 (olikraus), Adafruit BME680 + Adafruit Unified Sensor.
ArduinoJson / PubSubClient / WiFiManager only if you turn publishing on.

The HM3301 and PCF8563 are driven directly over I²C with no vendor library.
For the HM3301 that's inherited from `diy_node.ino`: Seeed's library uses
non-standard `u8`/`u16`/`u32` type aliases and won't compile against a modern
arduino-esp32 core. The frame decode is the same proven code.

### If you see "Multiple libraries were found for SD.h"

Harmless. The IDE picks the ESP32 core's `SD`, which is the right one. To
silence it, delete the stray `~/Library/Arduino15/libraries/SD` (the AVR-era
copy) — nothing in this sketch wants it.

### Two rules if you edit this sketch

The Arduino IDE auto-generates a forward declaration for every function in a
`.ino` and injects them **immediately before the first function definition**.
That produces two failure modes that look nothing like their cause:

1. **Every struct must be defined above the first function.** There's a
   `TYPES` block near the top for exactly this. Put a new struct anywhere
   below and you get `'YourType' was not declared in this scope` pointing at
   a line that is obviously fine.
2. **No default arguments on top-level functions.** The IDE copies the
   default into the generated prototype and leaves it on the definition;
   the compiler rejects the redefinition.

`tools/ino_check.py` in this repo reproduces the IDE's preprocessing and
catches both offline, which plain `g++` cannot.

## Feature flags

At the top of the sketch:

| Flag | Default | What it does |
|---|---|---|
| `PUBLISH_TO_SMARTCITIZEN` | `0` | MQTT upload. Off — that's the point of this build. |
| `LOG_TO_SD` | `1` | CSV to microSD, one file per day |
| `ENABLE_DETECTOR` | `1` | On-device burning detector + buzzer |
| `ENABLE_HM3301` | `1` | Set `0` for a Basic kit — node becomes a T/RH/P/gas logger and the detector goes inert (it needs PM2.5), which it says on screen |
| `DISPLAY_AUTO_CYCLE` | `1` | Pages advance on their own every 8 s |

## On the screen

Five pages. **Short press** the user button to advance, **long press (1.2 s)**
to mute or unmute the buzzer.

1. **Overview** — big PM2.5, detector state, temperature and humidity
2. **Particulates** — PM1 / PM2.5 / PM10 atmospheric, plus the CF=1 values
3. **Climate + gas** — temperature, humidity, pressure, gas resistance, IAQ
4. **Detector** — this hour's baseline, spread, sample count, current z and 60-min rise
5. **System** — sensor status and bad-frame count, SD status, RTC status, uptime

## Serial commands

115200 baud.

```
SETTIME 2026-08-21 14:32:00     set the RTC (local time)
BASELINE RESET                  wipe the PM hour-of-day baseline, restart warm-up
GASBASE RESET                   wipe the BME680 clean-air gas reference
```

Set the clock once, fit the CR1220, and the node keeps time through power
cuts. Without a valid RTC, rows go to `NOCLOCK.CSV` timestamped
`NO_RTC+<seconds>` — greppable, so you can filter them out rather than mistake
them for real dates.

## The CSV

`/YYYYMMDD.CSV`, header written on creation, one row per minute. Opened and
closed per row: slower, but a yanked power cable costs you the current row
rather than the whole file.

```
timestamp,pm1,pm25,pm10,pm1_cf,pm25_cf,pm10_cf,
bin03,bin05,bin1,bin25,bin5,bin10,
temp_c,rh_pct,pressure_kpa,gas_ohm,iaq,z,rise60,alert
```

Empty fields mean that sensor didn't read on that cycle. They're left blank
rather than zero-filled, because a zero in a PM column is a real measurement
and a missing one is not.

`pm*` are the atmospheric values — that's what the detector and the platform
use. `pm*_cf` are the CF=1 factory/indoor-calibrated values, logged because
they're free and occasionally diagnostic.

### The bin columns are unverified

`bin03`…`bin10` come from bytes 16–27 of the HM3301 frame and are *understood*
to be particle counts per 0.1 L above 0.3 / 0.5 / 1.0 / 2.5 / 5 / 10 µm. But
Seeed's HM3301 datasheet does not document those bytes, and their own example
decodes only the six mass values. The layout is inherited from the
HM3300/HM3600 family.

We log them anyway — storage is free, and an unverified channel you kept beats
a verified one you threw away. **But don't build anything on them.** If your
unit returns zeros there, that's the sensor, not the code. Someone needs to
check against a reference before these mean anything.

Related: the backtest found that size *ratios* on low-cost optical sensors
carry no combustion signal at all, so the prior probability that these bins
are useful discriminators is low. Log, don't trust.

## The detector

Not a threshold alarm. Thresholds don't work here: hourly PM2.5 above the WHO
24 h guideline of 15 µg/m³ fired **4.55 times a day** at a comparatively clean
Bali site. An alarm that goes off four times a day is wallpaper.

Instead it scores each reading against a **learned baseline for that hour of
the day** and requires a **rate of rise** at the same time:

```
alert  when   z > 4      (deviations above this hour's normal)
        AND   rise > +15 µg/m³ over the last 60 minutes
        AND   sustained for 2 consecutive readings
clear  when   z < 2
```

Twenty-four hour-of-day slots, each an EWMA of the level and an EWMA of the
absolute deviation. Slots persist to NVS, so a power cut doesn't cost you the
learning. Readings taken *during* an alert are deliberately excluded from the
baseline update — letting an event teach the baseline that events are normal
is how these detectors go deaf.

There is **no particle-size composition gate**, deliberately. We tried it.
During a confirmed burning event 150 m from one of our kits, PM2.5/PM10,
PM1/PM2.5 and the number-concentration ratios all stayed inside their normal
range — only magnitude moved. Low-cost optical sensors derive the coarse bins
from an assumed distribution rather than measuring them. Don't add a
composition gate back without new evidence.

**What did work:** on that one event, this logic crossed threshold **47 minutes
before the first human reported it.**

### Honest limitations

- The thresholds come from **one** confirmed co-located event. There is no
  established detection rate and no false-positive rate.
- Expect roughly **one alert every two to three days**, most of which nobody
  will be able to explain. That is the state of the evidence, not a bug.
- Give it a week. Each hour-slot needs 60 readings before it will fire; page 4
  shows the warm-up count.

Buzzer stays quiet 22:00–07:00, chirps at most once per 10 minutes during an
event, and a long press mutes it.

## Two numbers not to over-trust

**IAQ** is an open approximation, not Bosch BSEC. It scores gas resistance
against a slowly-learned clean-air baseline, weighted 75/25 with humidity, and
inverted so lower is cleaner. The gas element needs **24–48 h of power-on**
before the baseline means anything, and it's relative to this unit's own
environment — not comparable between nodes. The baseline now persists to NVS
so a power cut no longer resets it to zero (an improvement over
`diy_node.ino`). If you ever need a defensible comparable index, that's the
trigger to integrate BSEC or co-locate with a reference, not this proxy.

**Temperature** will read several degrees hot in a closed enclosure next to
the XIAO, with humidity correspondingly low. Shield the BME680 or externalise
it if the temperature number matters — buried sensors have been measured
+2.7…+5.3 °C off.

## Status

Compile-checked across all seven feature-flag combinations with `-Wall
-Wextra -Wformat=2` against stub headers, **and** through
`tools/ino_check.py`, which reproduces the Arduino IDE's prototype injection.
That second check exists because the first one shipped a sketch that built
fine as plain C++ and failed in the IDE — it's the difference between
"compiles" and "compiles the way you'll actually build it". The HM3301 frame
decode is separately unit-tested offline against a synthetic packet (offsets,
big-endian assembly, and checksum rejection of a corrupted frame).

**Not yet run on hardware.** The v5 enclosure also has no display window cut.
