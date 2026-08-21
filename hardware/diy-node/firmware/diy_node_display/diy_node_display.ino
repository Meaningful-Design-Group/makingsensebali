// Making Sense Bali — DIY Node (display build)
// v2.0-display — XIAO + Seeed Expansion Base + Grove Sensirion SEN5x
//
// Target: Seeed XIAO ESP32-S3 or ESP32-C3, seated in the
//         Seeed Studio Expansion Base for XIAO (the one with the 0.96" OLED,
//         microSD slot, PCF8563 RTC, buzzer and Grove ports).
// Sensor: Grove Sensirion SEN5x (SEN54 or SEN55) on a Grove I2C port.
//         Optional: BME680 (0x76/0x77) if the node already has one — it is
//         auto-detected and only adds barometric pressure + raw gas resistance.
//
// WHY THIS EXISTS, AND HOW IT DIFFERS FROM diy_node.ino
// ---------------------------------------------------------------------------
// diy_node.ino is a publisher: it reads, it uploads to Smart Citizen, and the
// only way to see a number is to go and look at a website. On 2026-08-20 we
// audited the pipeline behind that website and found (a) nothing had ever been
// archived at full resolution, (b) three separate jobs were racing to publish
// and clobbering each other, and (c) the platform's own history file had been
// stuck empty for months. A node whose readings are only visible after four
// network hops and a git push is a node you cannot trust in the field.
//
// So this build inverts the priority. The screen and the SD card are the
// primary outputs. Publishing is a compile-time option and it is OFF.
//
//   * OLED shows live readings on five pages, cycled with the user button.
//   * Every reading is appended to a CSV on the microSD, timestamped from the
//     battery-backed RTC. That file is the archive — no network required.
//   * An on-device detector flags likely burning events and sounds the buzzer.
//     It is not a threshold alarm; see the DETECTOR section for why, and what
//     the numbers are grounded in.
//
// THE ONE HARDWARE GOTCHA — READ THIS BEFORE WIRING
// ---------------------------------------------------------------------------
// The SEN5x needs 5V at 63-80 mA (it runs a laser and a fan). The Expansion
// Base's Grove ports supply 3.3V. Plugging the Grove SEN5x straight into a
// Grove I2C port will NOT work — you get an I2C timeout, or worse, a sensor
// that half-boots and returns garbage.
//
// The fix: the Expansion Base breaks out a 5V rail on its servo header. Take
// the SEN5x's VCC from there and leave SDA/SCL/GND on the Grove port — i.e.
// a Grove cable with the red wire re-routed. The SEN5x's I2C lines are 3.3V
// LVTTL, so no level shifter is needed; it is purely a power problem.
//
//   Grove port  ->  SDA, SCL, GND
//   5V header   ->  VCC
//
// Measure the VCC pin on your Grove port with a meter first — board revisions
// differ and if yours reads 5V you can skip all of the above and just plug in.
//
// Consequence for battery use: the 5V rail is USB VBUS. On battery alone there
// is no 5V, so the SEN5x will not run. This node is mains/USB powered unless
// you add a boost converter. The firmware detects the sensor's absence and
// says so on screen rather than silently logging zeros.
//
// PIN BUDGET (Expansion Base)
// ---------------------------------------------------------------------------
//   I2C  D4/D5   shared bus: SSD1306 OLED 0x3C, PCF8563 RTC 0x51,
//                SEN5x 0x69, optional BME680 0x76/0x77 — no address collisions
//   D1           user button (active LOW, onboard pull-up)
//   D2           microSD chip select
//   D8/D9/D10    SPI for the microSD (SCK / MISO / MOSI)
//   A3           passive buzzer
//
// Bus speed is pinned to 100 kHz because that is the SEN5x maximum (standard
// mode). A full 128x64 OLED frame is ~92 ms at that rate, which is why the
// screen refreshes at 1 Hz and not faster. Do not raise Wire.setClock().
//
// LIBRARIES (Arduino Library Manager)
// ---------------------------------------------------------------------------
//   - U8g2                    (olikraus)        — 2-clause BSD
//   - Adafruit BME680 Library (optional sensor)  — BSD
//   - ArduinoJson v7.x        (only when PUBLISH_TO_SMARTCITIZEN)
//   - PubSubClient            (only when PUBLISH_TO_SMARTCITIZEN)
//   - WiFiManager (tzapu)     (only when PUBLISH_TO_SMARTCITIZEN)
//
// The SEN5x and the PCF8563 are driven directly over I2C with no vendor
// library, same reasoning as the HM3301 in diy_node.ino: the protocols are
// small, and it keeps the dependency list short enough to audit. The SEN5x
// command words below are taken from Sensirion's own embedded-i2c-sen5x
// driver, so they are the vendor's numbers, just inlined.
//
// License: MIT. Every dependency above is MIT/BSD/permissive, no closed blobs.
// Repo: https://github.com/mdg-bali/makingsensebali

#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <U8g2lib.h>
#include <Preferences.h>
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

// Optional BME680 for barometric pressure + raw gas resistance. Auto-detected
// at boot; if it isn't on the bus the node just carries on without it.
#define ENABLE_BME680 1

// ============================================================================
// CONFIGURATION
// ============================================================================

const uint32_t SAMPLE_INTERVAL_MS   = 10UL * 1000UL;   // read the sensor
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
// Smart Citizen global-catalog sensor IDs for the SEN5x channels. Confirm
// these against your own device page before trusting them — the SEN5x entries
// were added later than the BME68X/HM-3301 ones this project started with.
const int SC_ID_PM1   = 0;   // set from your device page
const int SC_ID_PM25  = 0;
const int SC_ID_PM4   = 0;
const int SC_ID_PM10  = 0;
const int SC_ID_TEMP  = 0;
const int SC_ID_HUM   = 0;
const int SC_ID_VOC   = 0;
const int SC_ID_NOX   = 0;
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

constexpr uint8_t SEN5X_ADDR   = 0x69;
constexpr uint8_t PCF8563_ADDR = 0x51;

// ============================================================================
// DISPLAY
// ============================================================================

// Full-frame buffer (1 KB). Plenty of RAM on S3/C3 and much simpler than
// paged mode when you're drawing mixed font sizes.
U8G2_SSD1306_128X64_NONAME_F_HW_I2C oled(U8G2_R0, U8X8_PIN_NONE);

// ============================================================================
// SEN5x — direct I2C
//
// Command words and execution delays are lifted from Sensirion's
// embedded-i2c-sen5x driver. Every 2 data bytes on the wire are followed by a
// CRC-8 byte (poly 0x31, init 0xFF, no final XOR), so an N-word read is 3N
// bytes on the wire.
// ============================================================================

constexpr uint16_t SEN5X_CMD_START_MEASUREMENT      = 0x0021;
constexpr uint16_t SEN5X_CMD_START_MEASUREMENT_NOPM = 0x0037;
constexpr uint16_t SEN5X_CMD_STOP_MEASUREMENT       = 0x0104;
constexpr uint16_t SEN5X_CMD_READ_DATA_READY        = 0x0202;
constexpr uint16_t SEN5X_CMD_READ_MEASURED_VALUES   = 0x03C4;  // 8 words
constexpr uint16_t SEN5X_CMD_READ_MEASURED_PM       = 0x0413;  // 10 words
constexpr uint16_t SEN5X_CMD_START_FAN_CLEANING     = 0x5607;
constexpr uint16_t SEN5X_CMD_GET_PRODUCT_NAME       = 0xD014;  // 16 words
constexpr uint16_t SEN5X_CMD_READ_DEVICE_STATUS     = 0xD206;  // 2 words
constexpr uint16_t SEN5X_CMD_DEVICE_RESET           = 0xD304;

// Sensirion CRC-8: polynomial 0x31, initialisation 0xFF, MSB first.
uint8_t sen5xCrc(const uint8_t* data, size_t len) {
  uint8_t crc = 0xFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (uint8_t b = 0; b < 8; b++) {
      crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x31) : (uint8_t)(crc << 1);
    }
  }
  return crc;
}

bool sen5xSendCommand(uint16_t cmd, uint16_t delayMs) {
  Wire.beginTransmission(SEN5X_ADDR);
  Wire.write((uint8_t)(cmd >> 8));
  Wire.write((uint8_t)(cmd & 0xFF));
  if (Wire.endTransmission() != 0) return false;
  if (delayMs) delay(delayMs);
  return true;
}

// Reads `count` 16-bit words, verifying the CRC on each. Returns false on any
// short read or CRC mismatch — a bad frame is discarded whole rather than
// partially trusted, because a corrupted PM value looks exactly like a real
// spike and would poison the detector's baseline.
bool sen5xReadWords(uint16_t cmd, uint16_t* out, size_t count, uint16_t delayMs) {
  if (!sen5xSendCommand(cmd, delayMs)) return false;

  const size_t wireBytes = count * 3;
  size_t got = Wire.requestFrom((uint8_t)SEN5X_ADDR, (uint8_t)wireBytes);
  if (got != wireBytes) return false;

  for (size_t i = 0; i < count; i++) {
    uint8_t buf[3];
    for (uint8_t b = 0; b < 3; b++) {
      if (!Wire.available()) return false;
      buf[b] = Wire.read();
    }
    if (sen5xCrc(buf, 2) != buf[2]) return false;
    out[i] = ((uint16_t)buf[0] << 8) | buf[1];
  }
  return true;
}

// 0xFFFF is the SEN5x's "no valid value" sentinel for unsigned channels;
// 0x7FFF is the signed equivalent. Both become NAN so they never reach the
// CSV or the detector as a real number.
inline float sen5xScaleU(uint16_t raw, float divisor) {
  return (raw == 0xFFFF) ? NAN : (float)raw / divisor;
}
inline float sen5xScaleS(uint16_t raw, float divisor) {
  int16_t s = (int16_t)raw;
  return (s == 0x7FFF) ? NAN : (float)s / divisor;
}

struct Sen5xReading {
  // From READ_MEASURED_VALUES (0x03C4)
  float pm1 = NAN, pm25 = NAN, pm4 = NAN, pm10 = NAN;   // µg/m³
  float rh = NAN, tempC = NAN;                          // %RH, °C
  float vocIndex = NAN, noxIndex = NAN;                 // 1-500 index
  // From READ_MEASURED_PM (0x0413) — the channels the platform discards
  float nc05 = NAN, nc1 = NAN, nc25 = NAN, nc4 = NAN, nc10 = NAN;  // #/cm³
  float tps = NAN;                                      // µm
  bool  valid = false;
};

char     sen5xProductName[17] = {0};
bool     sen5xPresent = false;
bool     sen5xIsSen55 = false;      // NOx only exists on the SEN55
uint32_t sen5xStatusFlags = 0;

bool sen5xReadProductName() {
  uint16_t w[16];
  if (!sen5xReadWords(SEN5X_CMD_GET_PRODUCT_NAME, w, 16, 50)) return false;
  size_t n = 0;
  for (size_t i = 0; i < 16 && n < 16; i++) {
    char hi = (char)(w[i] >> 8), lo = (char)(w[i] & 0xFF);
    if (!hi) break;
    sen5xProductName[n++] = hi;
    if (!lo) break;
    sen5xProductName[n++] = lo;
  }
  sen5xProductName[n] = '\0';
  sen5xIsSen55 = (strstr(sen5xProductName, "55") != nullptr);
  return n > 0;
}

// Device status bits we care about. Bit meanings per the SEN5x datasheet.
bool sen5xReadStatus() {
  uint16_t w[2];
  if (!sen5xReadWords(SEN5X_CMD_READ_DEVICE_STATUS, w, 2, 20)) return false;
  sen5xStatusFlags = ((uint32_t)w[0] << 16) | w[1];
  return true;
}
inline bool sen5xFanFault()   { return sen5xStatusFlags & (1UL << 4); }
inline bool sen5xLaserFault() { return sen5xStatusFlags & (1UL << 5); }
inline bool sen5xRhtFault()   { return sen5xStatusFlags & (1UL << 6); }
inline bool sen5xGasFault()   { return sen5xStatusFlags & (1UL << 7); }
inline bool sen5xFanClean()   { return sen5xStatusFlags & (1UL << 19); }

bool sen5xBegin() {
  // The sensor needs up to 50 ms after power-up before it answers at all.
  delay(60);
  if (!sen5xReadProductName()) return false;
  if (!sen5xSendCommand(SEN5X_CMD_START_MEASUREMENT, 50)) return false;
  return true;
}

bool sen5xDataReady() {
  uint16_t w;
  if (!sen5xReadWords(SEN5X_CMD_READ_DATA_READY, &w, 1, 20)) return false;
  return (w & 0x00FF) != 0;
}

bool sen5xRead(Sen5xReading &r) {
  uint16_t v[8];
  if (!sen5xReadWords(SEN5X_CMD_READ_MEASURED_VALUES, v, 8, 20)) return false;

  r.pm1      = sen5xScaleU(v[0], 10.0f);
  r.pm25     = sen5xScaleU(v[1], 10.0f);
  r.pm4      = sen5xScaleU(v[2], 10.0f);
  r.pm10     = sen5xScaleU(v[3], 10.0f);
  r.rh       = sen5xScaleS(v[4], 100.0f);
  r.tempC    = sen5xScaleS(v[5], 200.0f);
  r.vocIndex = sen5xScaleS(v[6], 10.0f);
  r.noxIndex = sen5xScaleS(v[7], 10.0f);

  // Second frame: particle number concentrations and typical particle size.
  //
  // NOTE ON typical_particle_size — the divisor here is 1000, not 10.
  // Our Smart Citizen kits publish this channel as "TPS" with values of
  // 39-58 "µm", which is physically impossible for ambient aerosol and is
  // almost certainly the factor-10 PM divisor applied to a factor-1000
  // channel — exactly 100x too large. The real figure is ~0.4-0.6 µm, which
  // is what you would expect where combustion aerosol dominates. This node
  // writes the correct value; if you compare its CSV against the platform's
  // TPS channel, expect a 100x discrepancy and trust this one.
  uint16_t p[10];
  if (sen5xReadWords(SEN5X_CMD_READ_MEASURED_PM, p, 10, 20)) {
    r.nc05 = sen5xScaleU(p[4], 10.0f);
    r.nc1  = sen5xScaleU(p[5], 10.0f);
    r.nc25 = sen5xScaleU(p[6], 10.0f);
    r.nc4  = sen5xScaleU(p[7], 10.0f);
    r.nc10 = sen5xScaleU(p[8], 10.0f);
    r.tps  = sen5xScaleU(p[9], 1000.0f);
  }

  r.valid = !isnan(r.pm25);
  return r.valid;
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
  // oscillator stopped, i.e. the coin cell died or was never fitted. The
  // time it hands back after that is meaningless, so mark it invalid rather
  // than logging plausible-looking nonsense.
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
//     PM2.5/PM10, PM1/PM2.5 and PN0.5/PN10 all stayed inside their normal
//     range. Only magnitude moved. So there is no composition gate here —
//     we tried, it does not work, don't add one back without new evidence.
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

#if ENABLE_DETECTOR

const float    Z_THRESHOLD       = 4.0f;    // anomaly, in mean-abs-deviations
const float    Z_CLEAR           = 2.0f;    // hysteresis: drop below to clear
const float    RISE_THRESHOLD    = 15.0f;   // µg/m³ gained over 60 minutes
const float    DEV_FLOOR         = 1.5f;    // µg/m³, stops z exploding when
                                            // a slot's deviation is near zero
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
Preferences prefs;
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
uint32_t alertStartedMs = 0;
DateTimeRTC alertStartedAt;

void baselineLoad() {
  prefs.begin("msb-node", false);
  size_t n = prefs.getBytesLength("slots");
  if (n == sizeof(slots)) {
    prefs.getBytes("slots", slots, sizeof(slots));
    Serial.println(F("[detector] baseline restored from NVS"));
  } else {
    Serial.println(F("[detector] no stored baseline — starting warm-up"));
  }
}

void baselineSave() {
  prefs.putBytes("slots", slots, sizeof(slots));
  lastBaselineSave = millis();
}

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

  // Alert state machine.
  bool hit = (!isnan(z) && z > Z_THRESHOLD) && (!isnan(rise) && rise > RISE_THRESHOLD);
  if (hit) {
    if (alertStreak < 255) alertStreak++;
    if (!alertActive && alertStreak >= SUSTAIN_SAMPLES) {
      alertActive = true;
      alertStartedMs = millis();
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
  "timestamp,pm1,pm25,pm4,pm10,nc05,nc1,nc25,nc4,nc10,tps_um,"
  "temp_c,rh_pct,voc_index,nox_index,pressure_kpa,gas_ohm,z,rise60,alert";

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
void sdLogRow(const Sen5xReading &r, float pressureKPa, float gasOhm) {
  if (!sdPresent) return;

  char fname[16];
  if (nowLocal.valid) {
    snprintf(fname, sizeof(fname), "/%04u%02u%02u.CSV", nowLocal.year, nowLocal.month, nowLocal.day);
  } else {
    // No clock: everything goes in one file rather than scattering rows
    // across bogus dates. The rows carry NO_RTC markers so they're filterable.
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

  // A tiny helper so NAN lands as an empty field, not the string "nan".
  auto num = [](char* b, size_t n, float v, int dp) -> const char* {
    if (isnan(v)) { b[0] = '\0'; return b; }
    dtostrf(v, 0, dp, b);
    return b;
  };
  char b[18][16];

  f.printf("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d\n",
           ts,
           num(b[0],  16, r.pm1,  1), num(b[1],  16, r.pm25, 1),
           num(b[2],  16, r.pm4,  1), num(b[3],  16, r.pm10, 1),
           num(b[4],  16, r.nc05, 1), num(b[5],  16, r.nc1,  1),
           num(b[6],  16, r.nc25, 1), num(b[7],  16, r.nc4,  1),
           num(b[8],  16, r.nc10, 1), num(b[9],  16, r.tps,  3),
           num(b[10], 16, r.tempC, 2), num(b[11], 16, r.rh,   2),
           num(b[12], 16, r.vocIndex, 1), num(b[13], 16, r.noxIndex, 1),
           num(b[14], 16, pressureKPa, 3), num(b[15], 16, gasOhm, 0),
#if ENABLE_DETECTOR
           num(b[16], 16, lastZ, 2), num(b[17], 16, lastRise60, 1),
           alertActive ? 1 : 0
#else
           "", "", 0
#endif
  );
  f.close();
  sdRowsWritten++;
  strncpy(sdCurrentFile, fname + 1, sizeof(sdCurrentFile) - 1);
}
#endif

// ============================================================================
// OPTIONAL BME680 (pressure + raw gas resistance)
// ============================================================================

#if ENABLE_BME680
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
Adafruit_BME680 bme;
bool bmePresent = false;

void bmeBegin() {
  bmePresent = bme.begin(0x76) || bme.begin(0x77);
  if (bmePresent) {
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150);
    Serial.println(F("[bme680] present — logging pressure + gas resistance"));
  } else {
    Serial.println(F("[bme680] absent — fine, SEN5x covers T/RH"));
  }
}
#endif

float lastPressureKPa = NAN;
float lastGasOhm      = NAN;

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

Sen5xReading latest;

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
  if (isnan(latest.pm25)) snprintf(big, sizeof(big), "--");
  else                    dtostrf(latest.pm25, 0, 1, big);

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
  char sub[30];
  char a[12], b[12];
  valueOrDash(a, sizeof(a), latest.tempC, 1);
  valueOrDash(b, sizeof(b), latest.rh, 0);
  snprintf(sub, sizeof(sub), "%sC  %s%%", a, b);
  oled.drawStr(0, 63, sub);
  drawFooterHint();
}

void pageParticulates() {
  drawHeader("PARTICULATES");
  oled.setFont(u8g2_font_6x12_tf);
  char l[30], a[12], b[12];

  valueOrDash(a, sizeof(a), latest.pm1, 1);
  valueOrDash(b, sizeof(b), latest.pm25, 1);
  snprintf(l, sizeof(l), "PM1  %-7s PM2.5 %s", a, b);
  oled.drawStr(0, 22, l);

  valueOrDash(a, sizeof(a), latest.pm4, 1);
  valueOrDash(b, sizeof(b), latest.pm10, 1);
  snprintf(l, sizeof(l), "PM4  %-7s PM10  %s", a, b);
  oled.drawStr(0, 34, l);

  oled.setFont(u8g2_font_5x7_tf);
  valueOrDash(a, sizeof(a), latest.tps, 3);
  snprintf(l, sizeof(l), "typical size %s um", a);
  oled.drawStr(0, 46, l);

  valueOrDash(a, sizeof(a), latest.nc05, 0);
  valueOrDash(b, sizeof(b), latest.nc10, 0);
  snprintf(l, sizeof(l), "n0.5 %-8s n10 %s  /cm3", a, b);
  oled.drawStr(0, 56, l);
  drawFooterHint();
}

void pageClimate() {
  drawHeader("AIR + CLIMATE");
  oled.setFont(u8g2_font_6x12_tf);
  char l[30], a[12];

  valueOrDash(a, sizeof(a), latest.tempC, 2);
  snprintf(l, sizeof(l), "Temp   %s C", a);
  oled.drawStr(0, 22, l);

  valueOrDash(a, sizeof(a), latest.rh, 1);
  snprintf(l, sizeof(l), "Humid  %s %%", a);
  oled.drawStr(0, 34, l);

  valueOrDash(a, sizeof(a), latest.vocIndex, 0);
  snprintf(l, sizeof(l), "VOC    %s", a);
  oled.drawStr(0, 46, l);

  if (sen5xIsSen55) {
    valueOrDash(a, sizeof(a), latest.noxIndex, 0);
    snprintf(l, sizeof(l), "NOx    %s", a);
  } else if (!isnan(lastPressureKPa)) {
    valueOrDash(a, sizeof(a), lastPressureKPa, 2);
    snprintf(l, sizeof(l), "Press  %s kPa", a);
  } else {
    snprintf(l, sizeof(l), "NOx    n/a (SEN54)");
  }
  oled.drawStr(0, 58, l);
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
  if (s.count < WARMUP_SAMPLES) {
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

  snprintf(l, sizeof(l), "sensor %s", sen5xPresent ? sen5xProductName : "NOT FOUND");
  oled.drawStr(0, 19, l);

  if (sen5xPresent && (sen5xFanFault() || sen5xLaserFault() || sen5xRhtFault() || sen5xGasFault())) {
    snprintf(l, sizeof(l), "FAULT%s%s%s%s",
             sen5xFanFault() ? " fan" : "", sen5xLaserFault() ? " laser" : "",
             sen5xRhtFault() ? " rht" : "", sen5xGasFault() ? " gas" : "");
  } else if (sen5xFanClean()) {
    snprintf(l, sizeof(l), "fan cleaning in progress");
  } else {
    snprintf(l, sizeof(l), "status ok");
  }
  oled.drawStr(0, 29, l);

#if LOG_TO_SD
  if (sdPresent) snprintf(l, sizeof(l), "sd %s  %lu rows", sdCurrentFile, (unsigned long)sdRowsWritten);
  else           snprintf(l, sizeof(l), "sd NO CARD - not logging");
#else
  snprintf(l, sizeof(l), "sd logging disabled");
#endif
  oled.drawStr(0, 39, l);

  if (!rtcPresent)        snprintf(l, sizeof(l), "rtc NOT FOUND");
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

void publishReadings(const Sen5xReading &r) {
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
  add(SC_ID_PM1, r.pm1);   add(SC_ID_PM25, r.pm25);
  add(SC_ID_PM4, r.pm4);   add(SC_ID_PM10, r.pm10);
  add(SC_ID_TEMP, r.tempC); add(SC_ID_HUM, r.rh);
  add(SC_ID_VOC, r.vocIndex); add(SC_ID_NOX, r.noxIndex);
  String json; serializeJson(doc, json);
  String topic = String("device/sck/") + SC_DEVICE_TOKEN + "/readings";
  mqtt.publish(topic.c_str(), json.c_str(), false);
}
#endif

// ============================================================================
// SETUP
// ============================================================================

uint32_t lastSample = 0, lastLog = 0, lastDisplay = 0;

void setup() {
  Serial.begin(115200);
  delay(600);
  Serial.println(F("\n=== Making Sense Bali — DIY Node (v2.0-display, SEN5x) ==="));

  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_BUZZER, OUTPUT);

  // 100 kHz: the SEN5x is a standard-mode device and will NAK faster clocks.
  // The OLED would happily run at 400 kHz but it shares this bus.
  Wire.begin();
  Wire.setClock(100000);

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

  splash("sensor: starting", "SEN5x warm-up ~60s");
  sen5xPresent = sen5xBegin();
  if (sen5xPresent) {
    sen5xReadStatus();
    Serial.printf("[sen5x] online — %s (%s)\n", sen5xProductName,
                  sen5xIsSen55 ? "PM+RH/T+VOC+NOx" : "PM+RH/T+VOC");
  } else {
    Serial.println(F("[sen5x] NOT FOUND at 0x69."));
    Serial.println(F("[sen5x] It needs 5V at ~80mA — the Grove port is 3.3V."));
    Serial.println(F("[sen5x] Feed VCC from the 5V servo header, I2C from Grove."));
  }

#if ENABLE_BME680
  bmeBegin();
#endif

#if LOG_TO_SD
  sdPresent = sdBegin();
#endif

#if ENABLE_DETECTOR
  for (uint8_t i = 0; i < RISE_WINDOW; i++) riseRing[i] = NAN;
  baselineLoad();
#endif

#if PUBLISH_TO_SMARTCITIZEN
  provisionWiFi();
  configTime(TZ_OFFSET_HOURS * 3600, 0, "pool.ntp.org", "time.google.com");
#endif

  // The SEN5x needs about a minute of fan runtime before its first PM values
  // mean anything. Say so rather than showing a confident-looking zero.
  splash("warming up", "first values ~60s");
  chirp(1800, 90);
}

// ============================================================================
// SERIAL COMMANDS — set the clock without another tool
//   SETTIME 2026-08-21 14:32:00
//   FANCLEAN
//   BASELINE RESET
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
      if (rtcWrite(dt)) Serial.println(F("[rtc] set"));
      else              Serial.println(F("[rtc] write failed"));
    } else {
      Serial.println(F("[rtc] usage: SETTIME YYYY-MM-DD HH:MM:SS"));
    }
  } else if (line.startsWith("FANCLEAN")) {
    Serial.println(sen5xSendCommand(SEN5X_CMD_START_FAN_CLEANING, 20)
                     ? "[sen5x] fan cleaning started (~10s)"
                     : "[sen5x] fan clean command failed");
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
  if (rtcPresent && (ms % 1000) < 50) rtcRead(nowLocal);

  if (ms - lastSample >= SAMPLE_INTERVAL_MS || lastSample == 0) {
    lastSample = ms;
    if (sen5xPresent && sen5xDataReady()) {
      Sen5xReading r;
      if (sen5xRead(r)) latest = r;
      sen5xReadStatus();
    }
#if ENABLE_BME680
    if (bmePresent && bme.performReading()) {
      lastPressureKPa = bme.pressure / 1000.0f;
      lastGasOhm      = bme.gas_resistance;
    }
#endif
  }

  if (ms - lastLog >= LOG_INTERVAL_MS || lastLog == 0) {
    lastLog = ms;
    if (latest.valid) {
#if ENABLE_DETECTOR
      detectorUpdate(latest.pm25, nowLocal.valid ? nowLocal.hour : 0);
#endif
#if LOG_TO_SD
      sdLogRow(latest, lastPressureKPa, lastGasOhm);
#endif
      Serial.printf("[read] PM2.5=%.1f PM10=%.1f T=%.1f RH=%.0f VOC=%.0f NOx=%.0f TPS=%.3f\n",
                    latest.pm25, latest.pm10, latest.tempC, latest.rh,
                    latest.vocIndex, latest.noxIndex, latest.tps);
#if PUBLISH_TO_SMARTCITIZEN
      connectMQTT();
      mqtt.loop();
      publishReadings(latest);
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
