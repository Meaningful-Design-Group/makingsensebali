# Bayu firmware v6

v6 is v5 with the Seeed Expansion Base for XIAO added. If the node sits on that board,
it uses the OLED, the buzzer, the button, the microSD slot and the PCF8563 clock. On a
Grove Shield it does what v5 does: same sensors, same publishing (PLANETAI node first,
then Smart Citizen), same portal and status page. The XIAO ESP32-S3 also gets a status
LED, whatever board it sits on.

It has not run on a board yet. CI does not build or publish it (see below).

## How it finds the board

After the I2C scan, on the bus the scan picked, the node asks two addresses:

| OLED 0x3C | Clock 0x51 | Board | What v6 does |
|---|---|---|---|
| yes | yes | Expansion Base | screen, alarms, LED; on the S3 build also button D1, buzzer D3, microSD (CS D2, SPI D8/D9/D10) |
| yes | no | display | screen, alarms, LED |
| no | either | Grove Shield | v5, plus the LED on the S3 |

D1, D2 and D3 are only configured on an Expansion Base under the S3 build. The C3 build
is for the MakerGO SuperMini, which does not fit the Expansion Base, so on C3 an OLED
gives you the screen and nothing else. The Plantower stays RX-only on D7 and its SET pin
is never driven: on this board D2 is the microSD chip select.

The board shows up in the serial boot inventory (`[board] ...`), on the status page, and
as `"board"` in the `meta` message a PLANETAI node receives (`grove-shield`, `display`,
`expansion-base`). The Smart Citizen payload is the same as v5.

One thing v5 already did: the boot pin scan tries GPIO4/5 as I2C for a few
milliseconds, and GPIO4 is D3, the buzzer. On a screen board v6 does not repeat that
scan every 5 minutes, because the OLED already told it where the bus is.

## Screen

The Fab City logo alone for 2 s, then "Bayu", the firmware, the board and the sensors for
3 s. While the node joins its WiFi, the screen shows an animation: the WiFi arcs filling in,
"joining WiFi" and the network name. Then "WiFi connected" with the IP, or "WiFi offline",
for 2 seconds.

After that two pages take turns, 15 seconds each:

| Page | What it shows |
|---|---|
| Air | PM2.5 as a big number from the best sensor, its ISPU category on the 15-minute mean, and which sensor. The bottom line has every PM sensor's PM2.5 when there is more than one, PM10 otherwise. |
| Climate | Temperature and humidity, naming the sensor (SHT4x, else SEN5x, else BME680, else PMS5003T). CO2 with "ventilate" from 1000 ppm when an SCD4x is fitted, otherwise pressure, VOC index and IAQ. |

A short press on D1 steps through air, climate and status. The status page (WiFi, where it
publishes, last success, microSD, time, firmware) only comes up that way and goes back to
air after 15 seconds. The screen redraws once a second at most. The I2C bus stays at 100 kHz: U8g2 would otherwise set
400 kHz before every frame, which is what the display build
actually runs at.

## Alarms

| What | Threshold | Source |
|---|---|---|
| PM2.5 category | Baik ≤ 15.5, Sedang ≤ 55.4, Tidak Sehat ≤ 150.4, Sangat Tidak Sehat ≤ 250.4, Berbahaya above (µg/m³) | ISPU, Permen LHK P.14/2020 |
| PM2.5 alarm on | 15-minute mean in Tidak Sehat or worse (above 55.4) | ISPU, applied to a 15-min mean |
| PM2.5 alarm off | mean below 49.9 (55.4 minus 10 %) for 5 minutes | our hysteresis |
| CO2 "VENTILATE" | 1000 ppm | common room ventilation guideline |
| CO2 alarm on / off | 1500 ppm / below 1350 for 5 minutes | our choice |

PM2.5 comes from the best sensor present: SEN5x, then PMS5003, then HM3301. ISPU is
defined on a 24-hour mean, so on a 15-minute mean this is an indicative local warning,
not an ISPU reading. Please don't report a node in alarm as "ISPU Tidak Sehat". Every
threshold is a named constant near the top of `diy_node_v6.ino`.

When an alarm is on, every page gets an inverted banner and the LED stays lit. On an
Expansion Base with an S3 the buzzer gives 1, 2 or 3 beeps for Tidak Sehat, Sangat Tidak
Sehat and Berbahaya, one long beep for CO2, and repeats every 10 minutes. It stays silent
from 22:00 to 06:59 WITA. A long press on D1 (2 s) mutes it for 60 minutes; a short press
shows the next page.

The burning detector from the display build is here too, on screen boards, as a second
and separate alert: a "smoke?" banner and one chirp. Its numbers come from a single
confirmed event, so expect alerts nobody can explain.

## Status LED (XIAO ESP32-S3, GPIO21)

| Pattern | Meaning |
|---|---|
| fast blink, 5 Hz | setup portal open |
| blink, 1 Hz | joining WiFi at boot |
| one 50 ms flash every 5 s | online, last publish OK |
| two quick flashes every 5 s | offline, or publishing fails |
| on, solid | alarm |

The C3 SuperMini has no status LED in v6: its LED is on GPIO8, which is one of the I2C
pins the scan tries.

## microSD and clock

On an Expansion Base with an S3, each reading cycle (once a minute) adds a row to
`/bayu/YYYY-MM-DD.csv`. A new file starts with a header: time, time source, then every
channel v6 knows, left empty when that sensor is not fitted. The file is closed after
every row. If the card is missing, full or failing, the node keeps going, says so on the
screen and the status page, and tries the card again every 5 minutes.

Time comes from NTP and is written into the PCF8563 on every sync. If NTP fails at
boot, the clock is read from the PCF8563 instead. With no valid time at all, rows go to
`/bayu/NOCLOCK.csv` stamped `NO_TIME+<seconds since boot>`.

A node with a screen keeps working when the setup portal times out (screen, alarms,
microSD) and retries the saved WiFi every 15 s. A Grove Shield node still reboots into
the portal as v5 does.

## Self-update

v6 only installs a manifest build whose version starts with `v6-`. The flash page
manifest serves v5 today, so a v6 node reads it, writes on the status page that it is
not a v6 build, and stays where it is. A build from the IDE has no build tag and never
updates itself.

## Flashing by hand

Libraries, all pinned: WiFiManager from tzapu master
`4131fe617d01d746677e8b909379597162c2ca58` (the 2.0.17 release lacks two methods v5 and
v6 use), PubSubClient 2.8, ArduinoJson 7.4.2, Adafruit BME680 2.0.5, Adafruit Unified
Sensor 1.1.15, U8g2 2.36.19. Core esp32 3.3.12.

```sh
arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default diy_node_v6
arduino-cli upload  --fqbn esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default -p <port> diy_node_v6

arduino-cli compile --fqbn esp32:esp32:esp32c3:CDCOnBoot=cdc,PartitionScheme=min_spiffs diy_node_v6
```

In the IDE: USB CDC On Boot enabled on both boards, and Minimal SPIFFS on the C3.
Built on 26 Oct 2026: S3 1,429,651 bytes of 3,342,336 (v5: 1,352,804), C3 1,582,863 of
1,966,080 (v5: 1,497,363).

To test the self-update refusal, give the build a tag so it checks the manifest:
`--build-property "compiler.cpp.extra_flags=-DFW_BUILD_TAG=v6-bench"`.

The alarm logic has a laptop check:
`c++ -std=c++17 -Wall -Wextra -o /tmp/alarms_test test/alarms_test.cpp && /tmp/alarms_test`.

## Why CI does not publish it

`firmware-build` compiles `diy_node_v5/` and publishes it to the manifest every v5 node
reads once a day. v5 installs any build that is not its own, so publishing v6 there sends
it to the whole fleet the next day. v6 stays out of CI until it has passed the bench
test below. Promoting it means pointing `SKETCH` at `diy_node_v6`, adding `U8g2@2.36.19`
to `LIBS`, and accepting that every v5 node moves to v6.

## Bench test

1. Grove Shield node with the sensors it has in the field: same inventory and the same
   published bytes as v5, `[board] Grove Shield`, LED flashing once every 5 s.
2. Expansion Base node on an S3: logo, info frame, the WiFi animation, then air and
   climate taking turns every 15 s, `[board] Expansion
   Base`, a file in `/bayu/` with one row a minute. Check the HM3301 reads cleanly at
   100 kHz with the OLED redrawing.
3. Same node without a card: "no card" on screen and status page, everything else works.
   Insert the card and logging should start within 5 minutes.
4. Offline: switch the router off. The node keeps logging and the LED gives two flashes.
   Reboot it with the router still off: portal for 3 minutes, then it carries on and the
   rows say `rtc`. Take the coin cell out, power-cycle, and the rows go to `NOCLOCK.csv`.
5. Alarm with a smoke source (incense near the inlet): banner and beeps once the
   15-minute mean passes 55.4, and the alarm ends 5 minutes after the mean drops below
   49.9. Breathe on an SCD4x for the CO2 alarm.
6. Quiet hours: set the clock or wait for 22:00. The banner stays, no sound.
7. Long press D1 for 2 s: one low chirp, MUTE on the status page, no beeps for an hour.
   A short press changes the page.
8. Self-update: flash a `v6-bench` build. The status page should say the flash page
   serves a v5 build and it is not installed.
9. C3 SuperMini with an OLED: screen works, nothing driven on D1/D2/D3.
