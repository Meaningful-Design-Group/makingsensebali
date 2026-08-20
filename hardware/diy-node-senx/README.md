# DIY Node SENX — the one-sensor variant

A third hardware variant of the DIY node, alongside
[Basic and Plus](../diy-node/README.md). Where those use a BME680 for
temperature/humidity/VOC and add an HM3301 for particulates, SENX uses a single
Sensirion SEN5x that does all of it.

**Read [`../diy-node/README.md`](../diy-node/README.md) first.** Platform
registration, the MQTT transport, the workshop tooling in
[`../diy-node/tools/`](../diy-node/tools/) and the general approach are
documented there and are not repeated here. This file covers only what is
different about the SEN5x build.

---

## Why a third variant

| | Basic | Plus | **SENX** |
|---|---|---|---|
| Parts | BME680 | BME680 + HM3301 | SEN55 |
| PM | — | PM1/2.5/10 | PM1/2.5/**4**/10 |
| T / RH | BME680 | BME680 | SEN55 internal |
| VOC | gas resistance (raw Ω) + open IAQ approximation | same | **calibrated VOC Index** |
| NOx | — | — | **NOx Index** |
| Particle counts | — | — | PN 0.5–10 µm + typical particle size |
| Approx cost | USD 15–25 | USD 35–60 | USD 55–75 |

Two things justify the price. The **VOC and NOx indices** are Sensirion's own
algorithms rather than our open approximation over raw gas resistance — still
relative to the sensor's own history, but a defined scale rather than something
we invented. And the **particle number channels** are the ones that answer a
question mass concentration cannot: whether 30 µg/m³ is fine combustion soot or
coarse construction dust. For a campaign documenting open burning, that
distinction is the point.

What you give up: no barometric pressure, and one sensor means one point of
failure. The SEN55's fan is a moving part in a humid, ashy climate — see the
device-status note below.

---

## Hardware

- **XIAO ESP32-S3** + Grove Shield for XIAO + **Sensirion SEN55** on the Grove
  I²C port. Same board as Basic/Plus, so the enclosure work carries over.
- SEN55 I²C address `0x69`. Bus maximum **100 kHz** — do not raise it.
- **Power is the trap.** The SEN55 needs **4.5–5.5 V**. The XIAO's 5V pad is USB
  VBUS, not a regulated rail, so a LiPo on the BAT pads gives you no 5 V at all
  and a fan that will not spin. Mains/USB or a boost converter. There is no
  third option, and this must be decided before the enclosure is built.
- Digital I/O is **3.3 V and not 5 V tolerant**. `SEL` must be tied to GND to
  select I²C.
- Grove I²C on the XIAO ESP32-S3 is D4/D5 = GPIO5/GPIO6. The firmware probes
  **both orientations** — swapped SDA/SCL is the most common wiring mistake and
  it presents as "sensor not found", which sends people hunting a power fault
  that isn't there.
- Put **100–470 µF** near the sensor's 5 V. Fan inrush plus ESP32 WiFi TX spikes
  trip the brownout detector, and a brownout reboot loop looks exactly like a
  flaky sensor. The firmware logs `esp_reset_reason()` on boot so you can tell
  them apart.

---

## Smart Citizen channels

The platform already carries the full SEN5X family under catalogue parent 192.
You do not need to ask anyone to create them, and the MQTT ingest attaches them
to your device automatically on first publish.

| ID | Channel | Unit | Appears on the SC dashboard |
|---|---|---|---|
| 193 | PM 1.0 | µg/m³ | yes |
| 194 | PM 2.5 | µg/m³ | yes |
| 195 | PM 4.0 | µg/m³ | yes |
| 196 | PM 10.0 | µg/m³ | yes |
| 197–201 | PN 0.5 / 1.0 / 2.5 / 4.0 / 10.0 | #/0.1l | no |
| 202 | Typical Particle Size | µm | no |
| 203 | Humidity | % | **no** |
| 204 | Temperature | °C | **no** |
| 205 | VOC Index | — | yes |
| 206 | NOx Index | — | yes |
| 207 / 208 | VOC Raw / NOx Raw | — | — |

Source of truth is the SCK firmware's own table:
[`fablabbcn/smartcitizen-kit-2x` → `lib/Sensors/Sensors.h`](https://github.com/fablabbcn/smartcitizen-kit-2x/blob/master/lib/Sensors/Sensors.h)
(`OneSensor` field order is `location, priority, type, shortTitle, title, ID,
enabled, everyNint, unit, oled_display` — the 6th field is the platform id, the
10th governs display).

### Temperature and humidity store but do not display

**This will look like a bug and is not one.** On a SENX node, channels 203 and
204 receive data, store it with correct timestamps, and are queryable via the
API — but do not appear on the Smart Citizen dashboard. Ids 203 and 204 carry
`oled_display = false` in the catalogue, because on a real SCK the SEN5x sits
beside a dedicated SHT31/SHT35 and its internal RHT is treated as diagnostic
rather than canonical. A bare SEN5x node has no SHT, so its internal RHT *is*
the canonical source — a case the default configuration doesn't anticipate.

Verify with the tools in [`../diy-node/tools/`](../diy-node/tools/)
(`show_sensors.py <device_id>`), or directly:

```bash
curl -s https://api.smartcitizen.me/v0/devices/<ID> \
  | jq '.data.sensors[] | {id, name, value, last_reading_at}'
```

If 203/204 show a `last_reading_at` matching the PM channels, the data is fine
and only the display is missing. To get them displayed, ask the Smart Citizen
team — and give the reason, because that is what gets it actioned in one reply:

> This node is a bare SEN5x with no SHT, so the SEN5X internal RHT is our only
> temperature and humidity source. Please enable display of sensors 203 and 204
> on device `<id>`.

**Do not** republish temperature to 55/56 or 224/225 to make the dashboard light
up. Those are SHT channels; using them files SEN55 readings as SHT data and
destroys the provenance that makes the dataset worth anything.

The general lesson, which cost us an afternoon: **check whether data is stored
before assuming it wasn't ingested.** Two curl commands separate the two, and
they are very different bugs in very different places.

---

## Dashboard registration

Publishing to Smart Citizen does not put a node on the campaign map. Add the
device id to `KNOWN_BALI_SCK_IDS` in [`../../data.js`](../../data.js) — same
class of problem as the one above, one layer up.

---

## Firmware

[`firmware/diy_node_senx/`](firmware/diy_node_senx/). Board **XIAO_ESP32S3**,
and **USB CDC On Boot: Enabled** or `Serial` goes to the UART pins and you see
nothing at all.

Credentials: `cp secrets.h.example secrets.h` and fill it in. `secrets.h` is
gitignored. The Smart Citizen device token is a **write** credential — anyone
holding it can publish arbitrary readings into your device, which for a campaign
whose data is meant to be trusted is a worse problem than a leaked WiFi
password. It never goes in a tracked file, and a cleanup commit does not remove
it from git history — revoke and reissue instead.

Libraries: `Sensirion I2C SEN5X` (pulls in `Sensirion Core`) and `PubSubClient`.
No ArduinoJson — the payload is small and built with `snprintf`.

### What this sketch does that `diy_node` does not

- **Averages.** The SEN55 updates at 1 Hz. Publishing one instantaneous sample
  per minute discards 59 of 60 readings and makes PM look far spikier than the
  air actually is. This samples at 1 Hz and publishes the mean.
- **Buffers offline.** Readings taken while WiFi is down are queued to LittleFS
  with their real timestamps and replayed on reconnect, instead of leaving holes.
  Note this cannot protect against a QoS 0 publish dropped downstream of the
  socket — see the transport notes in `../diy-node/README.md`.
- **Polls device status.** `readDeviceStatus()` reports fan failure, fan speed
  out of range, laser failure, RHT comms error. The fan is what dies first in
  humidity and ash, and a degrading fan corrupts PM readings quietly long before
  it fails loudly.
- **Watchdog and reset reason.** `esp_task_wdt` recovers a hung node;
  `esp_reset_reason()` on boot distinguishes brownout from watchdog from someone
  pulling the plug. Across a distributed fleet that is the difference between
  debugging and guessing.
- **Recovers without resetting.** See below — this one is subtle and matters.
- **Echoes the outgoing frame** to serial, not a byte count. When a channel goes
  missing the only question is whether its id left the node, and `1 reading(s),
  219 B -> sent` cannot answer it.

### VOC and NOx are relative, and reset

The VOC index is defined so that ~100 is the running mean of *that sensor's own*
recent history. It is not an absolute pollution level, it needs hours of
continuous operation before it means anything, and `deviceReset()` wipes the
algorithm state.

So the firmware does **not** reset on every recovery attempt: cold boot resets,
but a recovery tries once without resetting first. A node with a marginal bus or
flaky power that reset every time would restart its conditioning forever, and
the VOC channel would be permanently meaningless while looking perfectly healthy
on the dashboard. This is the same failure as the `gasBaselineOhm` IAQ baseline
in `diy_node`, which lives only in RAM and reseeds from a cold gas element on
every boot — worth fixing there too.

Do not read anything into VOC or NOx from a bench test. Indoors, over a few
hours, the index sits near its own baseline regardless of the air.

### Temperature is published raw

`TEMP_OFFSET_C` ships at `0.0`. The SEN55's built-in compensation assumes
Sensirion's reference geometry, not our enclosure, so expect it to read warm in
a sealed box — and since RH is derived from T, a wrong offset poisons humidity
too. Measure the offset against a trusted reference **in the actual enclosure**,
after the reading has flattened; the first couple of hours are the sensor
settling thermally, not the air changing. Until then, don't cite either channel
as calibrated. Same caveat as channels 237/238 on the BME680 build.

---

## Known open issue: particle number units may be 100× off

`ENABLE_PN_CHANNELS` ships at `0`, and the reason is not caution for its own
sake.

The SEN5x and the SPS30 both output number concentration in **#/cm³**. Both have
their Smart Citizen channels declared as **#/0.1l**, which is 100× larger
(0.1 L = 100 cm³). In the SCK firmware the SPS30 path converts explicitly:

```c
// Convert PN readings from #/cm3 to #/0.1l
pm_readings.nc_0p5 *= 100;
```

No equivalent scaling was visible on the SEN5X path, where values are assigned
straight through. **Unconfirmed** — we could not read all of
`Sck_SEN5X::update()`. To close it, read `sam/src/SckUrban.cpp` in a clone of
`smartcitizen-kit-2x`.

If there is no ×100 on the SEN5X path, then SEN5X and SPS30 nodes are publishing
values 100× apart into identically-labelled channels platform-wide. That is
upstream's to fix, and worth raising as an issue rather than silently correcting
on our own nodes — otherwise Bali becomes the one dataset that's right and
nobody knows why. Set `PN_SCALE` once it's settled.

Mass concentration (193–196) is unaffected.

Related, and not a bug: **identical PM2.5 / PM4.0 / PM10 readings**. The SEN5x
measures the fine fraction optically and derives the coarser bins, so they
converge when there is no coarse fraction. Identical values mean a sub-2.5 µm
aerosol — combustion, not dust. That is a finding, not a fault, and it is the
best argument for getting the PN channels switched on.

---

## Status

First unit running on office bench burn-in, publishing to device 19849.
Not yet through a workshop, not yet in an enclosure outdoors, offset not yet
measured. Treat this variant as validated-in-principle, not field-proven.
