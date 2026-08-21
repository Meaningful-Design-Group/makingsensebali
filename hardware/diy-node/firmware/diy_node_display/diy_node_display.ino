// Making Sense Bali — DIY Node (display build)
// v2.1-display — XIAO + Seeed Expansion Base + Grove HM3301 + Grove BME680
//
// Target: Seeed XIAO ESP32-S3 or ESP32-C3, seated in the
//         Seeed Studio Expansion Base for XIAO (the one with the 0.96" OLED,
//         microSD slot, PCF8563 RTC, buzzer and Grove ports).
// Sensors: Grove HM3301 laser PM sensor (I2C 0x40)
//          Grove BME680 temperature / humidity / pressure / gas (I2C 0x76 or 0x77)
//
// WIRING — two Grove cables, nothing else
// ---------------------------------------------------------------------------
// Both sensors are 3.3V I2C parts and the Expansion Base has TWO Grove I2C
// ports. Plug one sensor into each. No soldering, no modified cables, no
// external supply. That is the whole hardware build.
//
//   Grove I2C port 1  ->  HM3301
//   Grove I2C port 2  ->  BME680
//
// (An earlier revision of this sketch targeted the Sensirion SEN5x. That part
// needs 5V at 63-80 mA and the Grove ports only supply 3.3V, so it required
// taking VCC off the board's servo header with a modified cable — and it would
// not run on battery at all, since the 5V rail is just USB VBUS. Dropped in
// favour of parts that plug straight in. The SEN5x revision is in the git
// history if anyone wants it.)
//
// WHY THIS EXISTS, AND HOW IT DIFFERS FROM diy_node.ino
// ---------------------------------------------------------------------------
// Same sensors as diy_node.ino, opposite priorities.
//
// diy_node.ino is a publisher: it reads, it uploads to Smart Citizen, and the
// only way to see a number is to go and look at a website. On 2026-08-20 we
// audited the pipeline behind that website and found (a) nothing had ever been
// archived at full resolution, (b) three separate jobs were racing to publish
// and clobbering each other, and (c) the platform's own history file had been
// stuck empty for months. A node whose readings are only visible after four
// network hops and a git push is a node you cannot trust in the field.
//
// So this build inverts it. The screen and the SD card are the primary
// outputs. Publishing is a compile-time option and it is OFF.
//
//   * OLED shows live readings on five pages, cycled with the user button.
//   * Every reading is appended to a CSV on the microSD, timestamped from the
//     battery-backed RTC. That file is the archive — no network required.
//   * An on-device detector flags likely burning events and sounds the buzzer.
//     It is not a threshold alarm; see the DETECTOR section for why, and what
//     the numbers are grounded in.
//
// PIN BUDGET (Expansion Base)
// ---------------------------------------------------------------------------
//   I2C  D4/D5   shared bus: SSD1306 OLED 0x3C, PCF8563 RTC 0x51,
//                HM3301 0x40, BME680 0x76 or 0x77 — no address collisions
//   D1           user button (active LOW, onboard pull-up)
//   D2           microSD chip select
//   D8/D9/D10    SPI for the microSD (SCK / MISO / MOSI)
//   A3           passive buzzer
//
// Bus runs at 100 kHz. The HM3301 datasheet does not state a maximum I2C
// clock, and the sensor has a reputation for being fussy, so we stay in
// standard mode rather than gamble. A full 128x64 OLED frame is ~92 ms at
// that rate, which is why the screen refreshes at 1 Hz. If you raise
// Wire.setClock() and the PM readings start failing checksum, that's why.
//
// LIBRARIES (Arduino Library Manager)
// ---------------------------------------------------------------------------
//   - U8g2                     (olikraus)                    — 2-clause BSD
//   - Adafruit BME680 Library  (+ Adafruit Unified Sensor)    — BSD
//   - ArduinoJson v7.x         (only when PUBLISH_TO_SMARTCITIZEN)
//   - PubSubClient             (only when PUBLISH_TO_SMARTCITIZEN)
//   - WiFiManager (tzapu)      (only when PUBLISH_TO_SMARTCITIZEN)
//
// The HM3301 and the PCF8563 are driven directly over I2C with no vendor
// library. For the HM3301 that is inherited from diy_node.ino: the Seeed
// library uses non-standard u8/u16/u32 type aliases and won't compile against
// the modern arduino-esp32 core. The protocol is simple enough to read
// ourselves, and the frame decode below is the same proven code.
//
// Requires arduino-esp32 core 3.x — the sketch uses tone(), which core 2.x
// does not provide.
//
// License: MIT. Every dependency above is MIT/BSD/permissive, no closed blobs.
// Repo: https://github.com/mdg-bali/makingsensebali

#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <U8g2lib.h>
#include <Preferences.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <math.h>

// ============================================================================
// FEATURE FLAGS — this is the main thing you edit
// ============================================================================

// Publishing is OFF by default. This build exists so you can read the node
// without a network. Turn this on only if you also want it to upload, and
// then fill in SC_DEVICE_TOKEN below.
#define PUBLISH_TO_SMARTCITIZEN 0

// Log every reading to microSD as CSV. The point of the exercise — leave on.
#define LOG_TO_SD 1

// On-device burning detector + buzzer. See the DETECTOR section.
#define ENABLE_DETECTOR 1

// Auto-advance the display pages every DISPLAY_CYCLE_MS. Press the button to
// take manual control; it reverts to auto after DISPLAY_MANUAL_TIMEOUT_MS.
#define DISPLAY_AUTO_CYCLE 1

// Basic kit with no HM3301? Set this to 0. The node then runs as a
// temperature / humidity / pressure / gas logger and the detector is inert
// (it needs PM2.5), which it will say on screen rather than pretend.
#define ENABLE_HM3301 1

// ============================================================================
// CONFIGURATION
// ============================================================================

const uint32_t SAMPLE_INTERVAL_MS   = 10UL * 1000UL;   // read the sensors
const uint32_t LOG_INTERVAL_MS      = 60UL * 1000UL;   // append a CSV row
const uint32_t DISPLAY_REFRESH_MS   = 1000UL;          // redraw the OLED
const uint32_t DISPLAY_CYCLE_MS     = 8000UL;          // auto page advance
const uint32_t DISPLAY_MANUAL_TIMEOUT_MS = 60000UL;    // back to auto after

// Buzzer: how long a single alert chirp lasts, and the minimum gap between
// chirps so a long event doesn't become a two-hour nuisance.
const uint32_t BUZZER_CHIRP_MS      = 180UL;
const uint32_t BUZZER_REPEAT_MS     = 10UL * 60UL * 1000UL;   // 10 min
const uint8_t  QUIET_HOUR_START     = 22;   // no buzzer 22:00-06:59 local
const uint8_t  QUIET_HOUR_END       = 7;

// Local time offset for the RTC and for filenames. Bali is WITA, UTC+8.
const int8_t   TZ_OFFSET_HOURS      = 8;

#if PUBLISH_TO_SMARTCITIZEN
// Per-device identity from your device page on smartcitizen.me.
const char* SC_DEVICE_TOKEN = "YOUR_SC_DEVICE_TOKEN";
// Smart Citizen global-catalog sensor IDs — same values as diy_node.ino, which
// are the dedicated catalog entries for this exact hardware. You normally do
// not touch these. Set any to 0 to skip publishing that channel.
const int SC_ID_PM1      = 233;  // µg/m³  — Seeed HM-3301 - PM1.0
const int SC_ID_PM25     = 234;  // µg/m³  — Seeed HM-3301 - PM2.5
const int SC_ID_PM10     = 235;  // µg/m³  — Seeed HM-3301 - PM10.0
const int SC_ID_TEMP     = 237;  // °C     — Bosch BME68X - Temperature
const int SC_ID_HUM      = 238;  // %RH    — Bosch BME68X - Humidity
const int SC_ID_PRESSURE = 239;  // kPa    — Bosch BME68X - Pressure
const int SC_ID_GAS      = 240;  // Ohm    — Bosch BME68X - Gas Resistance (RAW)
const int SC_ID_IAQ      = 241;  // index  — Bosch BME68X - IAQ (approximation)
const char* MQTT_HOST = "mqtt.smartcitizen.me";
const uint16_t MQTT_PORT = 8883;
const char* CONFIG_PORTAL_PASSWORD = "msb-setup";
#endif

// ============================================================================
// PINS
// ============================================================================

constexpr uint8_t PIN_BUTTON  = D1;
constexpr uint8_t PIN_SD_CS   = D2;
constexpr uint8_t PIN_BUZZER  = A3;

constexpr uint8_t HM3301_ADDR  = 0x40;
constexpr uint8_t PCF8563_ADDR = 0x51;
constexpr uint8_t HM3301_SELECT_I2C_CMD = 0x88;

// ============================================================================
// DISPLAY
// ============================================================================

// Full-frame buffer (1 KB). Plenty of RAM on S3/C3 and much simpler than
// paged mode when you're drawing mixed font sizes.
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE);

// ============================================================================
// HM3301 — direct I2C
//
// Init (once at boot): write 0x88 to 0x40 to select I2C mode. The sensor
//                      boots into UART mode by default.
// Read (every cycle):  requestFrom 29 bytes. Frame layout per the
//                      HM-3300/3600 datasheet and Seeed's own example:
//
//   buf[0..1]   frame header
//   buf[2..3]   sensor number
//   buf[4..5]   PM1.0  (CF=1, factory/indoor calibration)
//   buf[6..7]   PM2.5  (CF=1)
//   buf[8..9]   PM10   (CF=1)
//   buf[10..11] PM1.0  (atmospheric — what we publish and detect on)
//   buf[12..13] PM2.5  (atmospheric)
//   buf[14..15] PM10   (atmospheric)
//   buf[16..27] six 16-bit fields, understood to be particle counts per 0.1 L
//               above 0.3 / 0.5 / 1.0 / 2.5 / 5 / 10 µm
//   buf[28]     checksum, low byte of sum(buf[0..27])
//
// CAVEAT ON buf[16..27]: Seeed's datasheet for the HM3301 specifically does
// NOT document these bytes, and their own example decodes only the six mass
// values above. The bin layout is inherited from the HM3300/HM3600 family. We
// read and log them because storage is free and an unverified channel you
// kept beats a verified one you threw away — but treat them as UNVERIFIED. If
// your unit returns zeros there, that is the sensor, not this code. Do not
// build anything on them until someone checks against a reference.
// ============================================================================

struct PmReading {
  uint16_t pm1 = 0, pm25 = 0, pm10 = 0;          // atmospheric, µg/m³
  uint16_t pm1cf = 0, pm25cf = 0, pm10cf = 0;    // CF=1, µg/m³
  uint16_t bin[6] = {0, 0, 0, 0, 0, 0};          // see caveat above
  bool     valid = false;
};

bool hm3301Present = false;
uint32_t hm3301Fails = 0;   // consecutive failed reads, surfaced on the system page

bool hm3301Init() {
  Wire.beginTransmission(HM3301_ADDR);
  Wire.write(HM3301_SELECT_I2C_CMD);
  return Wire.endTransmission() == 0;
}

bool hm3301Read(PmReading &r) {
  uint8_t buf[29];
  size_t got = Wire.requestFrom((uint8_t)HM3301_ADDR, (uint8_t)29);
  if (got != 29) return false;
  for (int i = 0; i < 29; i++) {
    if (!Wire.available()) return false;
    buf[i] = Wire.read();
  }
  // Checksum: low byte of sum(buf[0..27]) must equal buf[28]. A corrupted
  // frame is discarded whole rather than partially trusted — a garbled PM
  // value looks exactly like a real spike and would poison the detector.
  uint8_t sum = 0;
  for (int i = 0; i < 28; i++) sum += buf[i];
  if (sum != buf[28]) return false;

  auto w = [&](int i) -> uint16_t { return (uint16_t)(((uint16_t)buf[i] << 8) | buf[i + 1]); };

  r.pm1cf  = w(4);   r.pm25cf = w(6);   r.pm10cf = w(8);
  r.pm1    = w(10);  r.pm25   = w(12);  r.pm10   = w(14);
  for (int b = 0; b < 6; b++) r.bin[b] = w(16 + b * 2);
  r.valid = true;
  return true;
}

// ============================================================================
// BME680
// ============================================================================

Adafruit_BME680 bme;
bool bmePresent = false;

struct EnvReading {
  float tempC = NAN, rh = NAN, pressureKPa = NAN, gasOhm = NAN, iaq = NAN;
  bool  valid = false;
};

// Clean-air gas-resistance reference for the IAQ approximation, learned at
// runtime. Persisted to NVS (see baselineSave) because it takes 24-48h of
// power-on to mean anything and a power cut used to reset it to zero.
float gasBaselineOhm = 0.0f;

// computeIAQ — OPEN air-quality index, 0 (clean) … 500 (polluted).
//
// This is NOT Bosch's certified BSEC IAQ. BSEC is closed-source with license
// terms that don't fit an open-data project, so we approximate the same 0-500
// shape from two signals the BME68X gives us for free: gas resistance (high in
// clean air, drops as VOCs rise) scored against a slow clean-air baseline, and
// humidity, peaked around ~40 %RH. Weighted 75/25, then inverted to the Bosch
// convention so LOWER = cleaner.
//
// HONEST LIMITATIONS — read before citing this number:
//   - The baseline needs the gas sensor to burn in (~24-48h of power-on)
//     before it means anything. Early values trend artificially clean.
//   - It is uncalibrated and relative to THIS unit's environment, not
//     comparable unit-to-unit the way a reference instrument is.
//   - If you need a defensible, comparable index for policy work, that's the
//     trigger to integrate BSEC or co-locate with a reference monitor — not
//     this proxy.
float computeIAQ(float gasOhm, float humRH) {
  if (isnan(gasOhm) || isnan(humRH) || gasOhm <= 0.0f) return NAN;

  // Rise toward cleaner readings fairly quickly, fall very slowly, so a burst
  // of pollution doesn't drag the clean-air reference down with it.
  if (gasBaselineOhm <= 0.0f) {
    gasBaselineOhm = gasOhm;
  } else {
    float alpha = (gasOhm > gasBaselineOhm) ? 0.05f : 0.001f;
    gasBaselineOhm += alpha * (gasOhm - gasBaselineOhm);
  }

  float gasRatio = gasOhm / gasBaselineOhm;
  if (gasRatio > 1.0f) gasRatio = 1.0f;
  if (gasRatio < 0.0f) gasRatio = 0.0f;
  float gasScore = gasRatio * 75.0f;

  float humScore;
  if (humRH < 38.0f)      humScore = (humRH / 40.0f) * 25.0f;
  else if (humRH > 42.0f) humScore = ((100.0f - humRH) / 60.0f) * 25.0f;
  else                    humScore = 25.0f;
  if (humScore < 0.0f) humScore = 0.0f;

  float iaq = (100.0f - (gasScore + humScore)) * 5.0f;
  if (iaq < 0.0f)   iaq = 0.0f;
  if (iaq > 500.0f) iaq = 500.0f;
  return iaq;
}

bool bmeRead(EnvReading &e) {
  if (!bmePresent || !bme.performReading()) return false;
  e.tempC       = bme.temperature;
  e.rh          = bme.humidity;
  e.pressureKPa = bme.pressure / 1000.0f;   // Pa -> kPa, SC platform convention
  e.gasOhm      = bme.gas_resistance;       // raw ohms, channel 240 expects this
  e.iaq         = computeIAQ(e.gasOhm, e.rh);
  e.valid       = !(isnan(e.tempC) || isnan(e.rh));
  return e.valid;
}

void bmeBegin() {
  bmePresent = bme.begin(0x76) || bme.begin(0x77);
  if (bmePresent) {
    // Bosch's suggested defaults for outdoor environmental monitoring. Heater
    // at 320°C for 150 ms gives a stable gas reading without burning power.
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150);
    Serial.println(F("[bme680] online — heater + filter configured"));
    // Worth knowing: in a closed enclosure next to the XIAO this will read
    // several degrees hot, and the humidity will read correspondingly low.
    // Shield it or externalise it if the temperature number matters.
  } else {
    Serial.println(F("[bme680] NOT FOUND at 0x76 or 0x77 — check the Grove cable"));
  }
}

// ============================================================================
// PCF8563 REAL-TIME CLOCK — direct I2C
//
// Battery-backed by the CR1220 on the Expansion Base, so the node keeps time
// across power cuts. Without this, SD rows from an offline node are unusable:
// you would have a beautiful time series and no idea when any of it happened.
// ============================================================================

struct DateTimeRTC {
  uint16_t year = 2000;
  uint8_t  month = 1, day = 1, hour = 0, minute = 0, second = 0;
  bool     valid = false;   // false when the RTC reports lost integrity
};

inline uint8_t bcd2dec(uint8_t b) { return (uint8_t)((b >> 4) * 10 + (b & 0x0F)); }
inline uint8_t dec2bcd(uint8_t d) { return (uint8_t)(((d / 10) << 4) | (d % 10)); }

bool rtcPresent = false;

bool rtcRead(DateTimeRTC &dt) {
  Wire.beginTransmission(PCF8563_ADDR);
  Wire.write(0x02);                       // VL_seconds
  if (Wire.endTransmission() != 0) return false;
  if (Wire.requestFrom((uint8_t)PCF8563_ADDR, (uint8_t)7) != 7) return false;

  uint8_t s   = Wire.read();
  uint8_t mi  = Wire.read();
  uint8_t h   = Wire.read();
  uint8_t d   = Wire.read();
  Wire.read();                            // weekday, unused
  uint8_t mo  = Wire.read();
  uint8_t y   = Wire.read();

  // Bit 7 of the seconds register is the Voltage Low flag: set when the
  // oscillator stopped, i.e. the coin cell died or was never fitted. The time
  // it hands back after that is meaningless, so mark it invalid rather than
  // logging plausible-looking nonsense.
  dt.valid  = !(s & 0x80);
  dt.second = bcd2dec(s & 0x7F);
  dt.minute = bcd2dec(mi & 0x7F);
  dt.hour   = bcd2dec(h & 0x3F);
  dt.day    = bcd2dec(d & 0x3F);
  dt.month  = bcd2dec(mo & 0x1F);
  dt.year   = (uint16_t)(2000 + bcd2dec(y));
  if (mo & 0x80) dt.year = (uint16_t)(1900 + bcd2dec(y));   // century bit
  return true;
}

bool rtcWrite(const DateTimeRTC &dt) {
  Wire.beginTransmission(PCF8563_ADDR);
  Wire.write(0x02);
  Wire.write(dec2bcd(dt.second) & 0x7F);   // clears the VL flag
  Wire.write(dec2bcd(dt.minute));
  Wire.write(dec2bcd(dt.hour));
  Wire.write(dec2bcd(dt.day));
  Wire.write(0x00);                        // weekday, we don't track it
  Wire.write(dec2bcd(dt.month));
  Wire.write(dec2bcd((uint8_t)(dt.year % 100)));
  return Wire.endTransmission() == 0;
}

DateTimeRTC nowLocal;

void formatTimestamp(const DateTimeRTC &dt, char* buf, size_t n) {
  if (dt.valid) {
    snprintf(buf, n, "%04u-%02u-%02uT%02u:%02u:%02u%+03d:00",
             dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
             (int)TZ_OFFSET_HOURS);
  } else {
    // Explicit, greppable marker. Better a row you can filter out than a row
    // that silently claims to be from the year 2000.
    snprintf(buf, n, "NO_RTC+%lus", (unsigned long)(millis() / 1000UL));
  }
}

// ============================================================================
// DETECTOR — is something burning nearby?
//
// Grounded in the backtest written up in docs/sensor-strategy.md. The short
// version of why it is shaped like this:
//
//   * Absolute thresholds are useless. Hourly PM2.5 > 15 µg/m³ (the WHO 24h
//     guideline) fired 4.55 times a day at a comparatively CLEAN Bali site.
//     An alarm that goes off four times a day is wallpaper.
//   * Particle-size ratios do not discriminate combustion on low-cost optical
//     sensors. During a confirmed burning event 150 m from one of our kits,
//     PM2.5/PM10, PM1/PM2.5 and the number-concentration ratios all stayed
//     inside their normal range. Only magnitude moved. So there is no
//     composition gate here — we tried, it does not work, don't add one back
//     without new evidence.
//   * What did work: anomaly against an hour-of-day baseline, combined with
//     rate of rise. On the one event we can verify, that crossed threshold
//     47 minutes before the first human reported it.
//
// Baseline: 24 hour-of-day slots. Each keeps an EWMA of the level and an EWMA
// of the absolute deviation from that level. The deviation term is a cheap
// stand-in for MAD — it is not MAD, it is mean-absolute-deviation, which runs
// a bit larger on noisy data and therefore makes this slightly conservative.
// Slots persist to NVS so a power cut doesn't cost you the learning.
//
// HONEST LIMITATIONS:
//   * The thresholds come from ONE confirmed co-located event. There is no
//     established detection rate and no false-positive rate. Expect roughly
//     one alert every two to three days, most of which nobody will be able
//     to explain. That is the current state of the evidence, not a bug.
//   * Warm-up matters. Until a slot has seen WARMUP_SAMPLES readings the
//     detector stays quiet for that hour of the day. Give it a week.
// ============================================================================

Preferences prefs;

#if ENABLE_DETECTOR

const float    Z_THRESHOLD       = 4.0f;    // anomaly, in mean-abs-deviations
const float    Z_CLEAR           = 2.0f;    // hysteresis: drop below to clear
const float    RISE_THRESHOLD    = 15.0f;   // µg/m³ gained over 60 minutes
const float    DEV_FLOOR         = 1.5f;    // µg/m³, stops z exploding when a
                                            // slot's deviation is near zero
const uint16_t WARMUP_SAMPLES    = 60;      // per hour-slot before it can fire
const uint8_t  SUSTAIN_SAMPLES   = 2;       // consecutive hits before alerting
const float    ALPHA_LEVEL       = 0.02f;   // EWMA rate for the slot level
const float    ALPHA_DEV         = 0.02f;   // EWMA rate for the deviation

struct HourSlot {
  float    level = NAN;
  float    dev   = NAN;
  uint16_t count = 0;
};

HourSlot   slots[24];
uint32_t   lastBaselineSave = 0;
const uint32_t BASELINE_SAVE_MS = 15UL * 60UL * 1000UL;

// 60-minute lookback ring, one slot per logging interval.
const uint8_t  RISE_WINDOW = 61;
float          riseRing[RISE_WINDOW];
uint8_t        riseHead = 0;
uint8_t        riseFilled = 0;

bool     alertActive = false;
uint8_t  alertStreak = 0;
uint16_t alertsToday = 0;
uint8_t  alertsTodayDay = 0;
float    lastZ = NAN;
float    lastRise60 = NAN;
DateTimeRTC alertStartedAt;

#endif  // ENABLE_DETECTOR

void baselineLoad() {
  prefs.begin("msb-node", false);
#if ENABLE_DETECTOR
  if (prefs.getBytesLength("slots") == sizeof(slots)) {
    prefs.getBytes("slots", slots, sizeof(slots));
    Serial.println(F("[detector] baseline restored from NVS"));
  } else {
    Serial.println(F("[detector] no stored baseline — starting warm-up"));
  }
#endif
  gasBaselineOhm = prefs.getFloat("gasbase", 0.0f);
  if (gasBaselineOhm > 0.0f) {
    Serial.printf("[bme680] gas baseline restored: %.0f ohm\n", gasBaselineOhm);
  }
}

void baselineSave() {
#if ENABLE_DETECTOR
  prefs.putBytes("slots", slots, sizeof(slots));
  lastBaselineSave = millis();
#endif
  if (gasBaselineOhm > 0.0f) prefs.putFloat("gasbase", gasBaselineOhm);
}

#if ENABLE_DETECTOR
// Push a reading through the detector. Call once per logging interval so the
// rise window has a consistent time base.
void detectorUpdate(float pm25, uint8_t hourOfDay) {
  if (isnan(pm25)) return;

  HourSlot &s = slots[hourOfDay % 24];

  // Score against the CURRENT baseline before touching it, otherwise the
  // reading partly explains itself away.
  float z = NAN;
  if (s.count >= WARMUP_SAMPLES && !isnan(s.level)) {
    float d = fmaxf(isnan(s.dev) ? DEV_FLOOR : s.dev, DEV_FLOOR);
    z = (pm25 - s.level) / d;
  }

  // 60-minute rise from the ring buffer.
  float rise = NAN;
  if (riseFilled >= RISE_WINDOW) {
    float oldest = riseRing[riseHead];   // head points at the oldest entry
    if (!isnan(oldest)) rise = pm25 - oldest;
  }
  riseRing[riseHead] = pm25;
  riseHead = (uint8_t)((riseHead + 1) % RISE_WINDOW);
  if (riseFilled < RISE_WINDOW) riseFilled++;

  lastZ = z;
  lastRise60 = rise;

  bool hit = (!isnan(z) && z > Z_THRESHOLD) && (!isnan(rise) && rise > RISE_THRESHOLD);
  if (hit) {
    if (alertStreak < 255) alertStreak++;
    if (!alertActive && alertStreak >= SUSTAIN_SAMPLES) {
      alertActive = true;
      alertStartedAt = nowLocal;
      if (alertsTodayDay != nowLocal.day) { alertsToday = 0; alertsTodayDay = nowLocal.day; }
      alertsToday++;
      Serial.printf("[detector] ALERT  pm25=%.1f  z=%.2f  rise60=%+.1f\n", pm25, z, rise);
    }
  } else {
    alertStreak = 0;
    if (alertActive && (isnan(z) || z < Z_CLEAR)) {
      alertActive = false;
      Serial.println(F("[detector] cleared"));
    }
  }

  // Only fold NON-alerting samples into the baseline. Letting an event teach
  // the baseline that events are normal is how these detectors go deaf.
  if (!alertActive) {
    if (isnan(s.level)) {
      s.level = pm25;
      s.dev   = DEV_FLOOR;
    } else {
      float delta = fabsf(pm25 - s.level);
      s.level += ALPHA_LEVEL * (pm25 - s.level);
      s.dev    = isnan(s.dev) ? delta : s.dev + ALPHA_DEV * (delta - s.dev);
    }
    if (s.count < 0xFFFF) s.count++;
  }

  if (millis() - lastBaselineSave > BASELINE_SAVE_MS) baselineSave();
}
#endif  // ENABLE_DETECTOR

// ============================================================================
// BUZZER
// ============================================================================

bool     buzzerMuted = false;
uint32_t lastChirp = 0;

void chirp(uint16_t freq, uint32_t ms) {
  tone(PIN_BUZZER, freq, ms);
}

void buzzerService() {
#if ENABLE_DETECTOR
  if (!alertActive || buzzerMuted) return;
  if (nowLocal.valid) {
    bool quiet = (QUIET_HOUR_START > QUIET_HOUR_END)
                   ? (nowLocal.hour >= QUIET_HOUR_START || nowLocal.hour < QUIET_HOUR_END)
                   : (nowLocal.hour >= QUIET_HOUR_START && nowLocal.hour < QUIET_HOUR_END);
    if (quiet) return;
  }
  if (lastChirp != 0 && millis() - lastChirp < BUZZER_REPEAT_MS) return;
  lastChirp = millis();
  chirp(2200, BUZZER_CHIRP_MS);
#endif
}

// ============================================================================
// SD LOGGING
//
// One CSV per day, named YYYYMMDD.CSV, header written on creation. Opened and
// closed per row: slower, but it means a yanked power cable costs you the
// current row rather than the whole file. For a node that logs once a minute
// that trade is obviously right.
// ============================================================================

bool sdPresent = false;
uint32_t sdRowsWritten = 0;
char sdCurrentFile[16] = {0};

const char* CSV_HEADER =
  "timestamp,pm1,pm25,pm10,pm1_cf,pm25_cf,pm10_cf,"
  "bin03,bin05,bin1,bin25,bin5,bin10,"
  "temp_c,rh_pct,pressure_kpa,gas_ohm,iaq,z,rise60,alert";

bool sdBegin() {
#if !LOG_TO_SD
  return false;
#else
  SPI.begin(D8, D9, D10, PIN_SD_CS);
  if (!SD.begin(PIN_SD_CS)) {
    Serial.println(F("[sd] no card — logging disabled, display still works"));
    return false;
  }
  Serial.printf("[sd] mounted, %llu MB\n", SD.cardSize() / (1024ULL * 1024ULL));
  return true;
#endif
}

#if LOG_TO_SD
void sdLogRow(const PmReading &p, bool pmOk, const EnvReading &e) {
  if (!sdPresent) return;

  char fname[16];
  if (nowLocal.valid) {
    snprintf(fname, sizeof(fname), "/%04u%02u%02u.CSV", nowLocal.year, nowLocal.month, nowLocal.day);
  } else {
    // No clock: everything goes in one file rather than scattering rows across
    // bogus dates. The rows carry NO_RTC markers so they stay filterable.
    snprintf(fname, sizeof(fname), "/NOCLOCK.CSV");
  }

  bool isNew = !SD.exists(fname);
  File f = SD.open(fname, FILE_APPEND);
  if (!f) {
    Serial.println(F("[sd] open failed"));
    sdPresent = false;      // stop hammering a dead card
    return;
  }
  if (isNew) f.println(CSV_HEADER);

  char ts[40];
  formatTimestamp(nowLocal, ts, sizeof(ts));

  // Empty field rather than "nan" or a fake zero when a sensor didn't read.
  // A zero in a PM column is a real measurement; a missing one is not.
  auto num = [](char* b, size_t n, float v, int dp) -> const char* {
    if (isnan(v)) { b[0] = '\0'; return b; }
    dtostrf(v, 0, dp, b);
    return b;
  };
  // One buffer per field. They must not be shared, because the order in which
  // printf's arguments are evaluated is unspecified — reusing a buffer across
  // two arguments of the same call is undefined behaviour, not a saving.
  char b[7][16];
  char pmf[12][8];
  for (int i = 0; i < 12; i++) pmf[i][0] = '\0';
  if (pmOk) {
    snprintf(pmf[0], 8, "%u", p.pm1);    snprintf(pmf[1], 8, "%u", p.pm25);
    snprintf(pmf[2], 8, "%u", p.pm10);   snprintf(pmf[3], 8, "%u", p.pm1cf);
    snprintf(pmf[4], 8, "%u", p.pm25cf); snprintf(pmf[5], 8, "%u", p.pm10cf);
    for (int i = 0; i < 6; i++) snprintf(pmf[6 + i], 8, "%u", p.bin[i]);
  }

  f.printf("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d\n",
           ts,
           pmf[0], pmf[1], pmf[2], pmf[3], pmf[4], pmf[5],
           pmf[6], pmf[7], pmf[8], pmf[9], pmf[10], pmf[11],
           num(b[0], 16, e.tempC, 2), num(b[1], 16, e.rh, 2),
           num(b[2], 16, e.pressureKPa, 3), num(b[3], 16, e.gasOhm, 0),
           num(b[4], 16, e.iaq, 0),
#if ENABLE_DETECTOR
           num(b[5], 16, lastZ, 2), num(b[6], 16, lastRise60, 1),
           alertActive ? 1 : 0
#else
           "", "", 0
#endif
  );
  f.close();
  sdRowsWritten++;
  strncpy(sdCurrentFile, fname + 1, sizeof(sdCurrentFile) - 1);
  sdCurrentFile[sizeof(sdCurrentFile) - 1] = '\0';
}
#endif

// ============================================================================
// BUTTON — short press cycles pages, long press mutes the buzzer
// ============================================================================

const uint32_t LONG_PRESS_MS = 1200;

uint8_t  page = 0;
const uint8_t PAGE_COUNT = 5;
uint32_t lastPageChange = 0;
uint32_t lastManualInput = 0;

bool     btnDown = false;
uint32_t btnDownAt = 0;
bool     btnLongFired = false;

void buttonService() {
  bool pressed = (digitalRead(PIN_BUTTON) == LOW);

  if (pressed && !btnDown) {
    btnDown = true;
    btnDownAt = millis();
    btnLongFired = false;
  } else if (pressed && btnDown && !btnLongFired && millis() - btnDownAt > LONG_PRESS_MS) {
    btnLongFired = true;
    buzzerMuted = !buzzerMuted;
    chirp(buzzerMuted ? 700 : 1600, 120);
    Serial.printf("[ui] buzzer %s\n", buzzerMuted ? "muted" : "unmuted");
  } else if (!pressed && btnDown) {
    btnDown = false;
    if (!btnLongFired) {
      page = (uint8_t)((page + 1) % PAGE_COUNT);
      lastPageChange = millis();
      lastManualInput = millis();
    }
  }
}

// ============================================================================
// DISPLAY PAGES
// ============================================================================

PmReading  latestPm;
bool       latestPmOk = false;
EnvReading latestEnv;

void drawHeader(const char* title) {
  oled.setFont(u8g2_font_5x7_tf);
  oled.drawStr(0, 6, title);
  char t[10];
  if (nowLocal.valid) snprintf(t, sizeof(t), "%02u:%02u", nowLocal.hour, nowLocal.minute);
  else                snprintf(t, sizeof(t), "--:--");
  int w = oled.getStrWidth(t);
  oled.drawStr(128 - w, 6, t);
  oled.drawHLine(0, 9, 128);
}

void drawFooterHint() {
  oled.setFont(u8g2_font_5x7_tf);
  char f[26];
  snprintf(f, sizeof(f), "%u/%u%s", page + 1, PAGE_COUNT, buzzerMuted ? "  MUTE" : "");
  int w = oled.getStrWidth(f);
  oled.drawStr(128 - w, 63, f);
}

void valueOrDash(char* buf, size_t n, float v, int dp, const char* suffix = "") {
  if (isnan(v)) snprintf(buf, n, "--%s", suffix);
  else {
    char t[16];
    dtostrf(v, 0, dp, t);
    snprintf(buf, n, "%s%s", t, suffix);
  }
}

void pageOverview() {
  drawHeader("MAKING SENSE BALI");

  char big[12];
  if (!latestPmOk) snprintf(big, sizeof(big), "--");
  else             snprintf(big, sizeof(big), "%u", latestPm.pm25);

  oled.setFont(u8g2_font_logisoso20_tf);
  oled.drawStr(0, 34, big);
  int w = oled.getStrWidth(big);
  oled.setFont(u8g2_font_5x7_tf);
  oled.drawStr(w + 4, 34, "ug/m3");
  oled.drawStr(w + 4, 25, "PM2.5");

#if ENABLE_DETECTOR
  char line[28];
  if (alertActive) {
    // Invert the strip so it reads across a room.
    oled.drawBox(0, 38, 128, 12);
    oled.setDrawColor(0);
    oled.setFont(u8g2_font_6x12_tf);
    snprintf(line, sizeof(line), "! SMOKE  %02u:%02u",
             alertStartedAt.valid ? alertStartedAt.hour : 0,
             alertStartedAt.valid ? alertStartedAt.minute : 0);
    oled.drawStr(2, 48, line);
    oled.setDrawColor(1);
  } else if (!isnan(lastZ)) {
    oled.setFont(u8g2_font_6x12_tf);
    snprintf(line, sizeof(line), "steady  z=%+.1f", lastZ);
    oled.drawStr(0, 48, line);
  } else {
    oled.setFont(u8g2_font_6x12_tf);
    oled.drawStr(0, 48, "learning baseline");
  }
#endif

  oled.setFont(u8g2_font_5x7_tf);
  char sub[30], a[12], b[12];
  valueOrDash(a, sizeof(a), latestEnv.tempC, 1);
  valueOrDash(b, sizeof(b), latestEnv.rh, 0);
  snprintf(sub, sizeof(sub), "%sC  %s%%", a, b);
  oled.drawStr(0, 63, sub);
  drawFooterHint();
}

void pageParticulates() {
  drawHeader("PARTICULATES");
  oled.setFont(u8g2_font_6x12_tf);
  char l[30];

  if (!latestPmOk) {
    oled.drawStr(0, 26, "HM3301 no reading");
    oled.setFont(u8g2_font_5x7_tf);
    oled.drawStr(0, 38, "check the Grove cable");
    drawFooterHint();
    return;
  }

  snprintf(l, sizeof(l), "PM1   %u", latestPm.pm1);
  oled.drawStr(0, 22, l);
  snprintf(l, sizeof(l), "PM2.5 %u", latestPm.pm25);
  oled.drawStr(0, 34, l);
  snprintf(l, sizeof(l), "PM10  %u", latestPm.pm10);
  oled.drawStr(0, 46, l);

  oled.setFont(u8g2_font_5x7_tf);
  snprintf(l, sizeof(l), "CF1 %u/%u/%u  ug/m3",
           latestPm.pm1cf, latestPm.pm25cf, latestPm.pm10cf);
  oled.drawStr(0, 57, l);
  drawFooterHint();
}

void pageClimate() {
  drawHeader("CLIMATE + GAS");
  oled.setFont(u8g2_font_6x12_tf);
  char l[30], a[12];

  if (!bmePresent) {
    oled.drawStr(0, 30, "BME680 not found");
    drawFooterHint();
    return;
  }

  valueOrDash(a, sizeof(a), latestEnv.tempC, 2);
  snprintf(l, sizeof(l), "Temp  %s C", a);
  oled.drawStr(0, 21, l);

  valueOrDash(a, sizeof(a), latestEnv.rh, 1);
  snprintf(l, sizeof(l), "Humid %s %%", a);
  oled.drawStr(0, 33, l);

  valueOrDash(a, sizeof(a), latestEnv.pressureKPa, 2);
  snprintf(l, sizeof(l), "Press %s kPa", a);
  oled.drawStr(0, 45, l);

  oled.setFont(u8g2_font_5x7_tf);
  char g[14], q[12];
  valueOrDash(g, sizeof(g), latestEnv.gasOhm / 1000.0f, 1);
  valueOrDash(q, sizeof(q), latestEnv.iaq, 0);
  snprintf(l, sizeof(l), "gas %skOhm  IAQ~%s", g, q);
  oled.drawStr(0, 57, l);
  drawFooterHint();
}

void pageDetector() {
  drawHeader("DETECTOR");
  oled.setFont(u8g2_font_6x12_tf);

#if ENABLE_DETECTOR
  char l[30], a[12];
  uint8_t h = nowLocal.valid ? nowLocal.hour : 0;
  HourSlot &s = slots[h % 24];

  valueOrDash(a, sizeof(a), s.level, 1);
  snprintf(l, sizeof(l), "base %02u:00  %s", h, a);
  oled.drawStr(0, 21, l);

  oled.setFont(u8g2_font_5x7_tf);
  valueOrDash(a, sizeof(a), s.dev, 2);
  snprintf(l, sizeof(l), "spread %s   n=%u", a, s.count);
  oled.drawStr(0, 31, l);

  oled.setFont(u8g2_font_6x12_tf);
  char zb[12], rb[12];
  valueOrDash(zb, sizeof(zb), lastZ, 2);
  valueOrDash(rb, sizeof(rb), lastRise60, 1);
  snprintf(l, sizeof(l), "z %-8s d60 %s", zb, rb);
  oled.drawStr(0, 44, l);

  oled.setFont(u8g2_font_5x7_tf);
  if (!latestPmOk) {
    snprintf(l, sizeof(l), "no PM sensor - inert");
  } else if (s.count < WARMUP_SAMPLES) {
    snprintf(l, sizeof(l), "warm-up %u/%u this hour", s.count, WARMUP_SAMPLES);
  } else {
    snprintf(l, sizeof(l), "%s   alerts today %u",
             alertActive ? "ALERT" : "armed", alertsToday);
  }
  oled.drawStr(0, 56, l);
#else
  oled.drawStr(0, 30, "detector disabled");
#endif
  drawFooterHint();
}

void pageSystem() {
  drawHeader("SYSTEM");
  oled.setFont(u8g2_font_5x7_tf);
  char l[34];

#if ENABLE_HM3301
  if (!hm3301Present)     snprintf(l, sizeof(l), "hm3301 NOT FOUND");
  else if (hm3301Fails)   snprintf(l, sizeof(l), "hm3301 %lu bad frames", (unsigned long)hm3301Fails);
  else                    snprintf(l, sizeof(l), "hm3301 ok");
#else
  snprintf(l, sizeof(l), "hm3301 disabled (Basic)");
#endif
  oled.drawStr(0, 19, l);

  snprintf(l, sizeof(l), "bme680 %s", bmePresent ? "ok" : "NOT FOUND");
  oled.drawStr(0, 29, l);

#if LOG_TO_SD
  if (sdPresent) snprintf(l, sizeof(l), "sd %s  %lu rows", sdCurrentFile, (unsigned long)sdRowsWritten);
  else           snprintf(l, sizeof(l), "sd NO CARD - not logging");
#else
  snprintf(l, sizeof(l), "sd logging disabled");
#endif
  oled.drawStr(0, 39, l);

  if (!rtcPresent)          snprintf(l, sizeof(l), "rtc NOT FOUND");
  else if (!nowLocal.valid) snprintf(l, sizeof(l), "rtc UNSET - fit CR1220");
  else snprintf(l, sizeof(l), "rtc %04u-%02u-%02u", nowLocal.year, nowLocal.month, nowLocal.day);
  oled.drawStr(0, 49, l);

  uint32_t up = millis() / 1000UL;
  snprintf(l, sizeof(l), "up %lud %02luh %02lum",
           (unsigned long)(up / 86400UL), (unsigned long)((up % 86400UL) / 3600UL),
           (unsigned long)((up % 3600UL) / 60UL));
  oled.drawStr(0, 59, l);
  drawFooterHint();
}

void drawScreen() {
  oled.clearBuffer();
  switch (page) {
    case 0: pageOverview();     break;
    case 1: pageParticulates(); break;
    case 2: pageClimate();      break;
    case 3: pageDetector();     break;
    default: pageSystem();      break;
  }
  oled.sendBuffer();
}

void splash(const char* line1, const char* line2) {
  oled.clearBuffer();
  oled.setFont(u8g2_font_7x13B_tf);
  oled.drawStr(0, 20, "Making Sense");
  oled.drawStr(0, 34, "Bali");
  oled.setFont(u8g2_font_5x7_tf);
  if (line1) oled.drawStr(0, 50, line1);
  if (line2) oled.drawStr(0, 60, line2);
  oled.sendBuffer();
}

// ============================================================================
// OPTIONAL PUBLISHING
// ============================================================================

#if PUBLISH_TO_SMARTCITIZEN
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>

WiFiClientSecure net;
PubSubClient mqtt(net);
WiFiManager wm;

String uniqueApName() {
  String mac = WiFi.macAddress();
  mac.replace(":", "");
  return "MakingSenseBali-" + mac.substring(6);
}

void provisionWiFi() {
  WiFi.mode(WIFI_STA);
  wm.setConnectTimeout(15);
  wm.setConfigPortalTimeout(180);
  splash("wifi: connecting", "or open the portal");
  if (!wm.autoConnect(uniqueApName().c_str(), CONFIG_PORTAL_PASSWORD)) {
    Serial.println(F("[wifi] portal timed out — continuing offline"));
    // Deliberately NOT restarting. The screen and the SD card are the point;
    // no network must never stop the node from doing its actual job.
  }
}

void connectMQTT() {
  if (mqtt.connected() || WiFi.status() != WL_CONNECTED) return;
  net.setInsecure();
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(768);
  mqtt.connect(SC_DEVICE_TOKEN, SC_DEVICE_TOKEN, "");
}

void publishReadings(const PmReading &p, bool pmOk, const EnvReading &e) {
  if (!mqtt.connected()) return;
  JsonDocument doc;
  JsonArray data = doc["data"].to<JsonArray>();
  JsonObject reading = data.add<JsonObject>();
  time_t now = time(nullptr);
  struct tm tmu; gmtime_r(&now, &tmu);
  char ts[32]; strftime(ts, sizeof(ts), "%Y-%m-%dT%H:%M:%SZ", &tmu);
  reading["recorded_at"] = ts;
  JsonArray sensors = reading["sensors"].to<JsonArray>();
  auto add = [&](int id, float v) {
    if (id == 0 || isnan(v)) return;
    JsonObject s = sensors.add<JsonObject>();
    s["id"] = id; s["value"] = v;
  };
  add(SC_ID_TEMP, e.tempC);       add(SC_ID_HUM, e.rh);
  add(SC_ID_PRESSURE, e.pressureKPa); add(SC_ID_GAS, e.gasOhm);
  add(SC_ID_IAQ, e.iaq);
  if (pmOk) {
    add(SC_ID_PM1,  (float)p.pm1);
    add(SC_ID_PM25, (float)p.pm25);
    add(SC_ID_PM10, (float)p.pm10);
  }
  String json; serializeJson(doc, json);
  String topic = String("device/sck/") + SC_DEVICE_TOKEN + "/readings";
  mqtt.publish(topic.c_str(), json.c_str(), false);
}
#endif

// ============================================================================
// SETUP
// ============================================================================

uint32_t lastSample = 0, lastLog = 0, lastDisplay = 0, lastRtcRead = 0;

void setup() {
  Serial.begin(115200);
  delay(600);
  Serial.println(F("\n=== Making Sense Bali — DIY Node (v2.1-display, HM3301 + BME680) ==="));

  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_BUZZER, OUTPUT);

  Wire.begin();
  Wire.setClock(100000);   // see the bus note in the header

  oled.begin();
  oled.setContrast(180);
  splash("booting...", "");

  // RTC first, so any later log line has a real timestamp.
  rtcPresent = rtcRead(nowLocal);
  if (!rtcPresent) {
    Serial.println(F("[rtc] PCF8563 not responding at 0x51"));
  } else if (!nowLocal.valid) {
    Serial.println(F("[rtc] clock integrity lost — fit a CR1220 and set the time"));
    Serial.println(F("[rtc] send: SETTIME YYYY-MM-DD HH:MM:SS   (local time)"));
  } else {
    Serial.printf("[rtc] %04u-%02u-%02u %02u:%02u:%02u local\n",
                  nowLocal.year, nowLocal.month, nowLocal.day,
                  nowLocal.hour, nowLocal.minute, nowLocal.second);
  }

  splash("sensors: starting", "");
  bmeBegin();

#if ENABLE_HM3301
  hm3301Present = hm3301Init();
  Serial.println(hm3301Present ? F("[hm3301] online at 0x40")
                               : F("[hm3301] NOT FOUND — check the Grove cable"));
#endif

#if LOG_TO_SD
  sdPresent = sdBegin();
#endif

#if ENABLE_DETECTOR
  for (uint8_t i = 0; i < RISE_WINDOW; i++) riseRing[i] = NAN;
#endif
  baselineLoad();

#if PUBLISH_TO_SMARTCITIZEN
  provisionWiFi();
  configTime(TZ_OFFSET_HOURS * 3600, 0, "pool.ntp.org", "time.google.com");
#endif

  // The HM3301's fan and laser need a moment before the first frame settles,
  // and the BME680's gas element needs far longer. Say so rather than showing
  // a confident-looking number the sensor doesn't mean yet.
  splash("warming up", "gas baseline: 24-48h");
  chirp(1800, 90);
}

// ============================================================================
// SERIAL COMMANDS — set the clock without another tool
//   SETTIME 2026-08-21 14:32:00
//   BASELINE RESET      wipe the PM hour-of-day baseline
//   GASBASE RESET       wipe the BME680 clean-air gas reference
// ============================================================================

void handleSerial() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.startsWith("SETTIME")) {
    DateTimeRTC dt;
    int y, mo, d, h, mi, s;
    if (sscanf(line.c_str(), "SETTIME %d-%d-%d %d:%d:%d", &y, &mo, &d, &h, &mi, &s) == 6) {
      dt.year = (uint16_t)y; dt.month = (uint8_t)mo; dt.day = (uint8_t)d;
      dt.hour = (uint8_t)h; dt.minute = (uint8_t)mi; dt.second = (uint8_t)s;
      Serial.println(rtcWrite(dt) ? "[rtc] set" : "[rtc] write failed");
    } else {
      Serial.println(F("[rtc] usage: SETTIME YYYY-MM-DD HH:MM:SS"));
    }
  } else if (line.startsWith("GASBASE RESET")) {
    gasBaselineOhm = 0.0f;
    prefs.putFloat("gasbase", 0.0f);
    Serial.println(F("[bme680] gas baseline cleared — 24-48h to re-learn"));
#if ENABLE_DETECTOR
  } else if (line.startsWith("BASELINE RESET")) {
    for (uint8_t i = 0; i < 24; i++) { slots[i].level = NAN; slots[i].dev = NAN; slots[i].count = 0; }
    baselineSave();
    Serial.println(F("[detector] baseline cleared — warm-up restarts"));
#endif
  }
}

// ============================================================================
// LOOP
// ============================================================================

void loop() {
  handleSerial();
  buttonService();

  uint32_t ms = millis();

  // Keep the clock fresh for the header and the quiet-hours check.
  if (rtcPresent && ms - lastRtcRead >= 1000UL) {
    lastRtcRead = ms;
    rtcRead(nowLocal);
  }

  if (ms - lastSample >= SAMPLE_INTERVAL_MS || lastSample == 0) {
    lastSample = ms;

#if ENABLE_HM3301
    if (hm3301Present) {
      PmReading r;
      if (hm3301Read(r)) { latestPm = r; latestPmOk = true; hm3301Fails = 0; }
      else               { hm3301Fails++; if (hm3301Fails > 6) latestPmOk = false; }
    }
#endif
    EnvReading e;
    if (bmeRead(e)) latestEnv = e;
  }

  if (ms - lastLog >= LOG_INTERVAL_MS || lastLog == 0) {
    lastLog = ms;
    if (latestPmOk || latestEnv.valid) {
#if ENABLE_DETECTOR
      if (latestPmOk) detectorUpdate((float)latestPm.pm25, nowLocal.valid ? nowLocal.hour : 0);
#endif
#if LOG_TO_SD
      sdLogRow(latestPm, latestPmOk, latestEnv);
#endif
      Serial.printf("[read] PM1=%u PM2.5=%u PM10=%u  T=%.2f RH=%.2f P=%.3f Gas=%.0f IAQ~%.0f (pm=%d bme=%d)\n",
                    latestPm.pm1, latestPm.pm25, latestPm.pm10,
                    latestEnv.tempC, latestEnv.rh, latestEnv.pressureKPa,
                    latestEnv.gasOhm, latestEnv.iaq, latestPmOk, latestEnv.valid);
#if PUBLISH_TO_SMARTCITIZEN
      connectMQTT();
      mqtt.loop();
      publishReadings(latestPm, latestPmOk, latestEnv);
#endif
    }
  }

  buzzerService();

#if DISPLAY_AUTO_CYCLE
  if (ms - lastManualInput > DISPLAY_MANUAL_TIMEOUT_MS &&
      ms - lastPageChange  > DISPLAY_CYCLE_MS) {
    page = (uint8_t)((page + 1) % PAGE_COUNT);
    lastPageChange = ms;
  }
#endif

  if (ms - lastDisplay >= DISPLAY_REFRESH_MS) {
    lastDisplay = ms;
    drawScreen();
  }

  delay(20);
}
