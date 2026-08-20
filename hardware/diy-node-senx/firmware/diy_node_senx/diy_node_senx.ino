// Making Sense Bali - DIY Node SENX firmware
//
// Sensirion SEN5x variant of the DIY node. Sibling to hardware/diy-node/
// (BME680 + HM3301): one part, fourteen channels, no external RHT sensor.
//
// Target: Seeed Studio XIAO ESP32-S3 + Grove Shield for XIAO
//         Sensirion SEN55 on the Grove I2C port (I2C address 0x69)
//         Tools -> USB CDC On Boot: Enabled, or Serial output never appears.
// Power:  continuous 5V (USB / mains). The SEN55 needs 4.5-5.5V; the XIAO's
//         5V pad is USB VBUS, so a LiPo on the BAT pads gives you NO 5V rail
//         and a dead fan. Boost converter or mains, no third option.
// Platform: publishes to mqtt.smartcitizen.me:8883 over TLS
//
// Repo: https://github.com/mdg-bali/makingsensebali
// License: MIT
//
// Transport, auth and payload shape follow the working Making Sense Bali C3
// node. Specifically, and this is the part that is easy to get wrong:
//
//   * There is NO device_id. The Smart Citizen onboarding flow only issues a
//     numeric device id for actual Smart Citizen Kits, so the documented REST
//     endpoint POST /v0/devices/<id>/readings is unusable for a DIY node. The
//     device TOKEN is the whole identity.
//   * MQTT over TLS on port 8883, not 1883.
//   * The token is used as BOTH the MQTT client_id and the username, with an
//     empty password. Same as the SCK firmware.
//   * Topic: device/sck/<token>/readings
//   * Payload: {"data":[{"recorded_at":"ISO8601","sensors":[{"id":N,"value":V}]}]}
//     Reference: github.com/fablabbcn/smartcitizen-api/blob/master/docs/mqtt.md
//
// ---------------------------------------------------------------------------
// WHAT THIS ADDS over the BME680 + HM3301 node
// ---------------------------------------------------------------------------
//  * SEN55: PM1/2.5/4/10 mass, RH, temperature, VOC index, NOx index, and
//    optionally particle number concentration + typical particle size.
//  * Averaging. The SEN55 updates at 1 Hz; publishing one instantaneous
//    sample per minute throws away 59 of every 60 readings and makes PM look
//    far spikier than the air actually is. We sample at 1 Hz and publish the
//    mean.
//  * Offline buffer on LittleFS. A reading taken while the WiFi is down is
//    queued with its real timestamp and replayed on reconnect, instead of
//    leaving a hole in the record. Read the QoS caveat at section 6 before
//    trusting it further than it deserves.
//  * Device status polling. readDeviceStatus() reports fan failure, fan speed
//    out of range, laser failure. The fan is the part that dies first in
//    humidity and ash, and a dying fan degrades PM readings quietly long
//    before it fails loudly.
//  * Watchdog + reset-reason logging, so a node that reboots tells you
//    whether it was a brownout, the watchdog, or someone pulling the plug.
//
// ---------------------------------------------------------------------------
// SAME HONESTY RULES as the C3 node
// ---------------------------------------------------------------------------
//  * No fake zeros: a failed sensor read contributes nothing to the average.
//  * No NaN: every value is checked before it enters the payload.
//  * If nothing valid survives a cycle, we publish nothing rather than an
//    empty frame.
//  * Temperature and humidity are published RAW. See TEMP_OFFSET_C.
//
// Libraries (Arduino Library Manager):
//   Sensirion I2C SEN5X (+ Sensirion Core), PubSubClient (Nick O'Leary)
//
// Portions derived from Sensirion's SEN5x example code, BSD 3-Clause,
// Copyright (c) 2021 Sensirion AG - notice retained in LICENSE-sensirion.txt.

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <SensirionI2CSen5x.h>
#include <LittleFS.h>
#include <esp_task_wdt.h>
#include <esp_system.h>
#include <time.h>
#include <math.h>

// ============================================================================
// 1. CONFIGURATION - edit these and reflash
// ============================================================================

// WiFi credentials and the Smart Citizen device token live in secrets.h,
// which is gitignored. Copy secrets.h.example to secrets.h and fill it in.
//
// The token is not a convenience setting - it is this device's entire identity
// AND its write credential. Anyone holding it can publish arbitrary readings
// into your device, which for a campaign whose data is meant to be trusted is a
// worse problem than a leaked WiFi password. It does not belong in a tracked
// file in a public repo, and deleting it in a later commit does not remove it
// from git history.
#include "secrets.h"

const char*    MQTT_HOST = "mqtt.smartcitizen.me";
const uint16_t MQTT_PORT = 8883;                 // TLS

// --- I2C pins ---
// The SEN55 lives at 0x69. On a XIAO ESP32-S3 with the Grove shield the
// correct pair is SDA=D4=GPIO5, SCL=D5=GPIO6, and a bare Wire.begin() would
// resolve to it. We probe anyway, in both orientations, because swapped SDA
// and SCL at the connector is the single most common wiring mistake and it
// reports as "sensor not found" - which sends you hunting a power fault that
// isn't there.
struct I2CPins { int sda; int scl; };
const I2CPins I2C_CANDIDATES[] = {
  {5, 6},  {6, 5},     // XIAO ESP32-S3 Grove (D4/D5) - this board
  {6, 7},  {7, 6},     // XIAO ESP32-C3 Grove (D4/D5)
  {8, 9},  {9, 8},     // ESP32-C3 SuperMini default
  {4, 5},  {5, 4}      // spares
};
const int I2C_CANDIDATE_COUNT = sizeof(I2C_CANDIDATES) / sizeof(I2C_CANDIDATES[0]);
constexpr uint8_t SEN5X_I2C_ADDR = 0x69;

int I2C_SDA_PIN = -1;    // filled by bringUpSensor()
int I2C_SCL_PIN = -1;

// --- Smart Citizen sensor IDs ---
// Canonical source, not guesswork: the SCK firmware's own sensor table.
//   github.com/fablabbcn/smartcitizen-kit-2x
//   @54da65ea64b4afdeb2b67cbeddfc0e6356d47301 lib/Sensors/Sensors.h L429
// Field order of OneSensor is (location, priority, type, shortTitle, title,
// ID, enabled, everyNint, unit, oled_display) - the 6th field is the platform
// sensor id. Cross-checked against the live /v0/sensors catalogue.
//
//   193 SEN5X PM 1.0   ug/m3     197 SEN5X PN 0.5   #/0.1l    203 Humidity     %
//   194 SEN5X PM 2.5   ug/m3     198 SEN5X PN 1.0   #/0.1l    204 Temperature  C
//   195 SEN5X PM 4.0   ug/m3     199 SEN5X PN 2.5   #/0.1l    205 Vocs Index   -
//   196 SEN5X PM 10.0  ug/m3     200 SEN5X PN 4.0   #/0.1l    206 NOx Index    -
//                                201 SEN5X PN 10.0  #/0.1l
//                                202 Typical Particle Size um
//   207 Vocs Raw / 208 NOx Raw - readMeasuredRawValues(), not sampled here.
//   Humidity Raw and Temperature Raw carry id 0 upstream: no channel exists.
//
// Global catalogue ids, the same for every SEN55 node. Replicators only set
// WiFi + token above. Set any id to 0 to stop publishing that channel.
enum MetricIdx {
    M_PM1 = 0, M_PM25, M_PM4, M_PM10, M_RH, M_TEMP, M_VOC, M_NOX,
    M_PN0P5, M_PN1, M_PN2P5, M_PN4, M_PN10, M_TPS,
    M_COUNT
};

const char* METRIC_NAME[M_COUNT] = {
    "pm1", "pm2.5", "pm4", "pm10", "humidity", "temperature", "voc", "nox",
    "pn0.5", "pn1.0", "pn2.5", "pn4.0", "pn10.0", "tps"
};

const int SC_SENSOR_ID[M_COUNT] = {
    193, 194, 195, 196,        /* PM1, PM2.5, PM4.0, PM10   */
    203, 204,                  /* humidity, temperature     */
    205, 206,                  /* VOC index, NOx index      */
    197, 198, 199, 200, 201,   /* PN0.5 .. PN10.0           */
    202                        /* typical particle size     */
};

// --- particle number concentration ---
// Worth having: mass concentration alone cannot tell you whether 30 ug/m3 is
// fine combustion soot or coarse construction dust. The number/mass ratio and
// typical particle size can. For a campaign documenting open burning, that is
// the distinction that matters - and it is the one PM2.5 alone erases.
//
// UNRESOLVED, AND NOW SHARPER: the SEN5x reports number concentration in
// #/cm3. Both the catalogue and the SCK firmware declare these channels as
// #/0.1l, which is 100x larger (0.1 L = 100 cm3).
//
// In the SCK firmware the SPS30 path converts explicitly:
//     // Convert PN readings from #/cm3 to #/0.1l
//     pm_readings.nc_0p5 *= 100;   ... and so on
// No equivalent scaling was visible on the SEN5X path, whose values are
// assigned straight through:
//     case SENSOR_SEN5X_PN_05:
//         if (sck_sen5x.getReading(...)) { ...reading = String(sck_sen5x.pN0p5); }
//
// I could not read all of Sck_SEN5X::update() to rule out a conversion
// happening earlier, so this is unconfirmed rather than settled. If there is
// no x100 on the SEN5X path, then SEN5X and SPS30 nodes are publishing
// 100x-apart values into identically-labelled channels platform-wide - which
// is upstream's problem to fix, not ours to paper over.
//
// So: ships OFF. Check sam/src/SckUrban.cpp :: Sck_SEN5X::update() in a local
// clone, or ask the SC team. Then set PN_SCALE to 1.0 or 100.0 and flip the
// switch. Mass concentration (193-196) is unaffected and needs no conversion.
#define ENABLE_PN_CHANNELS 0
const float PN_SCALE = 1.0f;          // set to 100.0f if the platform wants #/0.1l

// --- SEN55 compensation ---
// PUBLISHED RAW. Channel 204 is plain "Temperature", but the SEN55 sits in a
// sealed box with a fan and its own electronics, and its built-in compensation
// assumes Sensirion's reference geometry, not yours. Expect it to read high in
// an enclosure, and remember RH is derived from T - a wrong offset poisons
// humidity too. Measure this against a trusted reference, in the actual
// enclosure, after 30+ minutes. Until you have, don't cite either channel as
// calibrated.
const float    TEMP_OFFSET_C  = 0.0f;
const uint16_t RHT_ACCEL_MODE = 0;    // 0 = sensor default. See Sensirion's
                                      // "SEN5x Temperature Compensation
                                      // Instruction" app note before changing.

// --- timing ---
const uint32_t SAMPLE_MS     = 1000;      // SEN55 updates at 1 Hz
const uint32_t PUBLISH_MS    = 60000;     // one averaged reading per minute
const uint32_t STATUS_MS     = 60000;     // device status poll
const uint32_t FAN_CLEAN_MS  = 0;         // 0 = rely on the SEN55's automatic
                                          // weekly clean, which is valid only
                                          // because we run continuously. If
                                          // this node ends up power-cycling
                                          // daily, that counter keeps resetting
                                          // and the fan never cleans - set this
                                          // to e.g. 7UL*24*3600*1000 then.
const uint32_t WDT_TIMEOUT_S = 60;
const uint8_t  SEN_FAIL_LIMIT = 10;       // consecutive failures before re-init

// --- offline buffer ---
const char*  QUEUE_PATH        = "/queue.jsonl";
const size_t QUEUE_MAX_BYTES   = 128 * 1024;   // ~8h at one reading/minute
const int    BATCH_MAX         = 5;            // readings per publish
const size_t OBJ_MAX_BYTES     = 640;          // one 14-channel reading
const size_t PAYLOAD_MAX_BYTES = 4096;         // batch envelope

#define VERBOSE_SERIAL 1

// ============================================================================
// 2. STATE
// ============================================================================

SensirionI2CSen5x sen5x;
WiFiClientSecure  net;
PubSubClient      mqtt(net);

static char g_topic[128];

struct Accum {
    double   sum = 0;
    uint32_t n   = 0;
    void  add(float v) { if (!isnan(v) && !isinf(v)) { sum += v; n++; } }
    bool  ok() const   { return n > 0; }
    float avg() const  { return n ? (float)(sum / n) : NAN; }
    void  reset()      { sum = 0; n = 0; }
};
static Accum g_acc[M_COUNT];

static uint32_t g_tSample = 0, g_tPublish = 0, g_tStatus = 0, g_tFanClean = 0;
static uint32_t g_tWifiTry = 0, g_tMqttTry = 0;
static uint32_t g_wifiBackoff = 1000, g_mqttBackoff = 1000;
static uint8_t  g_senFails  = 0;
static bool     g_senOnline = false;
static uint32_t g_published = 0, g_queued = 0;

// ============================================================================
// 3. HELPERS
// ============================================================================

static uint32_t growBackoff(uint32_t cur) {
    uint32_t next = cur * 2;
    return next > 60000 ? 60000 : next;
}

static void logSenError(const char* what, uint16_t err) {
    char msg[128];
    errorToString(err, msg, sizeof(msg));
    Serial.printf("[sen55] %s failed: %s\n", what, msg);
}

static void printResetReason() {
    const char* r = "unknown";
    switch (esp_reset_reason()) {
        case ESP_RST_POWERON:   r = "power-on";               break;
        case ESP_RST_EXT:       r = "external reset";         break;
        case ESP_RST_SW:        r = "software restart";        break;
        case ESP_RST_PANIC:     r = "panic / exception";       break;
        case ESP_RST_INT_WDT:   r = "interrupt watchdog";      break;
        case ESP_RST_TASK_WDT:  r = "TASK WATCHDOG";           break;
        case ESP_RST_WDT:       r = "other watchdog";          break;
        case ESP_RST_BROWNOUT:  r = "BROWNOUT - check power";  break;
        case ESP_RST_DEEPSLEEP: r = "deep sleep wake";         break;
        default: break;
    }
    Serial.printf("[boot] last reset: %s\n", r);
}

static bool timeIsValid() {
    return time(nullptr) > 1735689600;      // 2025-01-01: NTP has clearly landed
}

static void isoNow(char* out, size_t cap) {
    time_t now = time(nullptr);
    struct tm t;
    gmtime_r(&now, &t);
    strftime(out, cap, "%Y-%m-%dT%H:%M:%SZ", &t);   // UTC, always
}

// ============================================================================
// 4. SENSOR BRING-UP AND SAMPLING
// ============================================================================

// Probe one candidate pin pair: does anything answer at the SEN5x address?
static bool probePins(int sda, int scl) {
    Wire.end();
    delay(5);
    if (!Wire.begin(sda, scl, 100000)) return false;   // SEN5x tops out at 100 kHz
    delay(20);
    Wire.beginTransmission(SEN5X_I2C_ADDR);
    bool hit = (Wire.endTransmission() == 0);
    if (hit) Serial.printf("      SDA=%2d SCL=%2d -> 0x%02X responding\n",
                           sda, scl, SEN5X_I2C_ADDR);
    return hit;
}

// doReset=false skips the device reset. That matters more than it looks:
// deviceReset() wipes the SEN55's VOC and NOx algorithm state, and those are
// self-calibrating indices - the VOC index is defined as ~100 for the running
// mean of this sensor's own recent history, and it needs hours of continuous
// operation before it means anything. Resetting on every recovery attempt
// means a node with a flaky bus or marginal power restarts that conditioning
// forever and the VOC channel is permanently meaningless. Same failure as the
// IAQ baseline in the C3 node, arriving from a different direction.
static bool sen55Configure(bool doReset) {
    uint16_t err;
    sen5x.begin(Wire);

    if (doReset) {
        err = sen5x.deviceReset();
        if (err) { logSenError("deviceReset()", err); return false; }
        delay(250);      // the reset has a real execution time; hitting the
                         // sensor immediately after is the most common cause
                         // of phantom NACKs on a cold boot
        Serial.println("[sen55] device reset - VOC/NOx conditioning cleared, "
                       "those indices need hours before they mean anything");
    } else {
        Serial.println("[sen55] soft recovery - preserving VOC/NOx conditioning");
    }

    unsigned char buf[32] = {0};
    if (!sen5x.getSerialNumber(buf, sizeof(buf)))  Serial.printf("[sen55] serial: %s\n",  (char*)buf);
    memset(buf, 0, sizeof(buf));
    if (!sen5x.getProductName(buf, sizeof(buf)))   Serial.printf("[sen55] product: %s\n", (char*)buf);

    uint8_t fwMaj, fwMin, hwMaj, hwMin, pMaj, pMin;
    bool fwDebug;
    if (!sen5x.getVersion(fwMaj, fwMin, fwDebug, hwMaj, hwMin, pMaj, pMin))
        Serial.printf("[sen55] fw %u.%u  hw %u.%u\n", fwMaj, fwMin, hwMaj, hwMin);

    err = sen5x.setTemperatureOffsetSimple(TEMP_OFFSET_C);
    if (err) logSenError("setTemperatureOffsetSimple()", err);
    else     Serial.printf("[sen55] temp offset: %.2f C (RAW if 0.00)\n", TEMP_OFFSET_C);

    if (RHT_ACCEL_MODE != 0) {
        err = sen5x.setRhtAccelerationMode(RHT_ACCEL_MODE);
        if (err) logSenError("setRhtAccelerationMode()", err);
    }

    err = sen5x.startMeasurement();
    if (err) {
        // On the no-reset path the device may already be measuring, which is
        // the outcome we want anyway - so this is only fatal if we reset.
        logSenError("startMeasurement()", err);
        if (doReset) return false;
        Serial.println("[sen55] ...treating as already-measuring");
    }

    Serial.println("[sen55] ONLINE - measuring");
    return true;
}

// Callable from setup() AND loop(). On native-USB boards the port doesn't
// enumerate until after boot, so anything setup() prints is often never
// delivered to the serial monitor. Re-running this from loop() while the
// sensor is missing makes the diagnostics visible, and lets a reseated Grove
// cable recover without a reboot.
static uint8_t g_softRecoveries = 0;

static void bringUpSensor(const char* reason) {
    Serial.printf("\n[sensor] bring-up (%s)\n", reason);
    Serial.println("[i2c] probing candidate pin pairs:");

    int foundSda = -1, foundScl = -1;
    for (int i = 0; i < I2C_CANDIDATE_COUNT && foundSda < 0; i++) {
        if (probePins(I2C_CANDIDATES[i].sda, I2C_CANDIDATES[i].scl)) {
            foundSda = I2C_CANDIDATES[i].sda;
            foundScl = I2C_CANDIDATES[i].scl;
        }
    }

    if (foundSda < 0) {
        Serial.println("      nothing at 0x69 on ANY candidate pair.");
        Serial.println("      -> Not a pin problem. Check power and cabling:");
        Serial.println("         SEN55 needs 4.5-5.5V. On battery the XIAO has NO 5V.");
        Serial.println("         SEL must be tied to GND to select I2C.");
        Serial.println("         Digital I/O is 3.3V and NOT 5V tolerant.");
        I2C_SDA_PIN = I2C_CANDIDATES[0].sda;
        I2C_SCL_PIN = I2C_CANDIDATES[0].scl;
        Wire.end();
        delay(5);
        Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000);
        g_senOnline = false;
        Serial.println();
        return;
    }

    I2C_SDA_PIN = foundSda;
    I2C_SCL_PIN = foundScl;
    Serial.printf("[i2c] USING SDA=%d SCL=%d\n", I2C_SDA_PIN, I2C_SCL_PIN);
    Wire.end();
    delay(5);
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000);

    // Cold boot always resets. A recovery tries once without resetting, to
    // keep the VOC/NOx conditioning; only if that fails do we reset and pay
    // the cost.
    bool coldBoot = (g_softRecoveries == 0xFF);
    bool doReset  = coldBoot || (g_softRecoveries >= 1);
    g_senOnline = sen55Configure(doReset);
    if (!coldBoot) g_softRecoveries = g_senOnline ? 0 : (uint8_t)(g_softRecoveries + 1);
    g_senFails = 0;
    Serial.println();
}

static void sen55Sample() {
    float pm1, pm25, pm4, pm10, rh, temp, voc, nox;
    uint16_t err = sen5x.readMeasuredValues(pm1, pm25, pm4, pm10, rh, temp, voc, nox);
    if (err) {
        logSenError("readMeasuredValues()", err);
        if (++g_senFails >= SEN_FAIL_LIMIT) {
            Serial.println("[sen55] too many consecutive failures");
            g_senOnline = false;                 // loop() will re-probe
        }
        return;                                  // contribute nothing
    }
    g_senFails = 0;

    g_acc[M_PM1 ].add(pm1);
    g_acc[M_PM25].add(pm25);
    g_acc[M_PM4 ].add(pm4);
    g_acc[M_PM10].add(pm10);
    g_acc[M_RH  ].add(rh);
    g_acc[M_TEMP].add(temp);
    g_acc[M_VOC ].add(voc);
    g_acc[M_NOX ].add(nox);

#if ENABLE_PN_CHANNELS
    // Second command: number concentrations + typical particle size. Mass
    // comes back here too; we ignore it and keep the values above.
    float mc1, mc25, mc4, mc10, pn0p5, pn1, pn2p5, pn4, pn10, tps;
    uint16_t pmErr = sen5x.readMeasuredPmValues(mc1, mc25, mc4, mc10,
                                                pn0p5, pn1, pn2p5, pn4, pn10, tps);
    if (pmErr) {
        logSenError("readMeasuredPmValues()", pmErr);
    } else {
        g_acc[M_PN0P5].add(pn0p5 * PN_SCALE);
        g_acc[M_PN1  ].add(pn1   * PN_SCALE);
        g_acc[M_PN2P5].add(pn2p5 * PN_SCALE);
        g_acc[M_PN4  ].add(pn4   * PN_SCALE);
        g_acc[M_PN10 ].add(pn10  * PN_SCALE);
        g_acc[M_TPS  ].add(tps);
    }
#endif

#if VERBOSE_SERIAL
    Serial.printf("[read] PM1=%.1f PM2.5=%.1f PM4=%.1f PM10=%.1f  "
                  "T=%.2f RH=%.1f  VOC=%.0f NOx=%.0f\n",
                  pm1, pm25, pm4, pm10, temp, rh, voc, nox);
#endif
}

// Bit positions below are the ones I am reasonably confident of. The raw value
// is always printed so anything unexpected can be checked against the SEN5x
// datasheet's Device Status register table.
static void sen55Status() {
    uint32_t st = 0;
    uint16_t err = sen5x.readDeviceStatus(st);
    if (err) { logSenError("readDeviceStatus()", err); return; }
    if (st == 0) return;

    Serial.printf("[sen55] device status 0x%08lX", (unsigned long)st);
    if (st & (1UL <<  4)) Serial.print("  FAN-FAILURE(blocked/broken)");
    if (st & (1UL <<  5)) Serial.print("  RHT-COMMS-ERROR");
    if (st & (1UL <<  6)) Serial.print("  LASER-FAILURE");
    if (st & (1UL << 21)) Serial.print("  FAN-SPEED-OUT-OF-RANGE");
    Serial.println();
}

// ============================================================================
// 5. PAYLOAD
// ============================================================================

static size_t buildReadingObject(char* out, size_t cap) {
    char ts[32];
    isoNow(ts, sizeof(ts));

    size_t n = snprintf(out, cap, "{\"recorded_at\":\"%s\",\"sensors\":[", ts);
    bool first = true;
    for (int i = 0; i < M_COUNT; i++) {
        if (SC_SENSOR_ID[i] == 0 || !g_acc[i].ok()) continue;   // no id, no data
        n += snprintf(out + n, (n < cap ? cap - n : 0), "%s{\"id\":%d,\"value\":%.2f}",
                      first ? "" : ",", SC_SENSOR_ID[i], g_acc[i].avg());
        first = false;
    }
    if (first) return 0;                    // nothing valid - caller sends nothing
    n += snprintf(out + n, (n < cap ? cap - n : 0), "]}");
    return (n < cap) ? n : 0;               // 0 also means "truncated"
}

static size_t buildBatchPayload(char* out, size_t cap,
                                const char objs[][OBJ_MAX_BYTES], int count) {
    size_t n = snprintf(out, cap, "{\"data\":[");
    for (int i = 0; i < count; i++) {
        n += snprintf(out + n, (n < cap ? cap - n : 0), "%s%s", i ? "," : "", objs[i]);
        if (n >= cap) return 0;
    }
    n += snprintf(out + n, (n < cap ? cap - n : 0), "]}");
    return (n < cap) ? n : 0;
}

static bool sendObjects(const char objs[][OBJ_MAX_BYTES], int count) {
    if (count <= 0 || !mqtt.connected()) return false;

    static char payload[PAYLOAD_MAX_BYTES];
    size_t n = buildBatchPayload(payload, sizeof(payload), objs, count);
    if (n == 0) { Serial.println("[mqtt] payload overflow, refusing to send"); return false; }

    bool ok = mqtt.publish(g_topic, payload, false);

    // PubSubClient publishes at QoS 0. A true return means the bytes reached
    // the socket - NOT that the broker acknowledged them, and NOT that the
    // platform ingested them. Checking the link is still up afterwards catches
    // the common half-open-TCP case, which is most of what actually goes
    // wrong; it is still not an ack. If you need real delivery guarantees for
    // data the campaign cites, that is the trigger to move to a QoS-1 client
    // (256dpi/arduino-mqtt), not to trust this line harder.
    if (ok && !mqtt.connected()) ok = false;

    Serial.printf("[mqtt] %d reading(s), %u B -> %s\n",
                  count, (unsigned)n, ok ? "sent" : "FAILED");

    // Echo the payload. When a channel is missing on the platform, the only
    // question that matters is whether its id left the node at all - and a
    // byte count cannot answer it. Printing the frame separates "the firmware
    // never sent id 204" from "the platform dropped id 204", which are
    // completely different bugs in completely different places.
#if VERBOSE_SERIAL
    Serial.printf("[mqtt] %s\n", payload);
#else
    static bool firstPublish = true;
    if (firstPublish) { Serial.printf("[mqtt] first frame: %s\n", payload); firstPublish = false; }
#endif

    if (ok) g_published += count;
    return ok;
}

// ============================================================================
// 6. OFFLINE QUEUE (LittleFS, one JSON reading object per line)
//
// Protects against the WiFi or the broker being unreachable, which is the
// failure that actually happens. It cannot protect against a QoS 0 publish
// being dropped downstream of the socket - see sendObjects().
// ============================================================================

static uint32_t queueCount() {
    File f = LittleFS.open(QUEUE_PATH, "r");
    if (!f) return 0;
    uint32_t lines = 0;
    uint8_t  buf[512];
    while (f.available()) {
        size_t r = f.read(buf, sizeof(buf));
        for (size_t i = 0; i < r; i++) if (buf[i] == '\n') lines++;
    }
    f.close();
    return lines;
}

static void queueTrimIfNeeded() {
    File f = LittleFS.open(QUEUE_PATH, "r");
    if (!f) return;
    size_t sz = f.size();
    if (sz <= QUEUE_MAX_BYTES) { f.close(); return; }

    f.seek(sz / 2);
    char discard[OBJ_MAX_BYTES];
    f.readBytesUntil('\n', discard, sizeof(discard));   // align to a line start

    File out = LittleFS.open("/queue.tmp", "w");
    if (!out) { f.close(); return; }
    uint8_t buf[512];
    while (f.available()) { size_t r = f.read(buf, sizeof(buf)); out.write(buf, r); }
    out.close();
    f.close();
    LittleFS.remove(QUEUE_PATH);
    LittleFS.rename("/queue.tmp", QUEUE_PATH);
    Serial.println("[queue] buffer full - dropped the oldest half");
}

static void queuePush(const char* obj) {
    File f = LittleFS.open(QUEUE_PATH, "a");
    if (!f) { Serial.println("[queue] open failed - reading LOST"); return; }
    f.print(obj);
    f.print('\n');
    f.close();
    g_queued++;
    queueTrimIfNeeded();
    Serial.printf("[queue] stored (%lu pending)\n", (unsigned long)g_queued);
}

static void queueDrain() {
    if (!mqtt.connected()) return;
    File f = LittleFS.open(QUEUE_PATH, "r");
    if (!f) return;
    if (f.size() == 0) { f.close(); LittleFS.remove(QUEUE_PATH); return; }

    static char batch[BATCH_MAX][OBJ_MAX_BYTES];
    size_t sentUpTo = 0;
    bool   stalled  = false;

    while (f.available() && !stalled) {
        int n = 0;
        size_t mark = f.position();
        while (n < BATCH_MAX && f.available()) {
            size_t len = f.readBytesUntil('\n', batch[n], OBJ_MAX_BYTES - 1);
            batch[n][len] = '\0';
            mark = f.position();
            if (len > 2) n++;
        }
        if (n == 0) break;
        if (sendObjects(batch, n)) {
            sentUpTo = mark;
            g_queued = (g_queued > (uint32_t)n) ? g_queued - (uint32_t)n : 0;
        } else {
            stalled = true;
        }
        mqtt.loop();
        esp_task_wdt_reset();
    }

    if (!f.available() && !stalled) {
        f.close();
        LittleFS.remove(QUEUE_PATH);
        g_queued = 0;
        Serial.println("[queue] drained");
        return;
    }

    if (sentUpTo > 0) {                      // keep the unsent tail
        f.seek(sentUpTo);
        File out = LittleFS.open("/queue.tmp", "w");
        if (out) {
            uint8_t buf[512];
            while (f.available()) { size_t r = f.read(buf, sizeof(buf)); out.write(buf, r); }
            out.close();
            f.close();
            LittleFS.remove(QUEUE_PATH);
            LittleFS.rename("/queue.tmp", QUEUE_PATH);
            return;
        }
    }
    f.close();
}

// ============================================================================
// 7. CONNECTIVITY (non-blocking, exponential backoff)
// ============================================================================

static void wifiTick() {
    if (WiFi.status() == WL_CONNECTED) { g_wifiBackoff = 1000; return; }
    uint32_t now = millis();
    if (now - g_tWifiTry < g_wifiBackoff) return;
    g_tWifiTry = now;
    Serial.printf("[wifi] connecting to %s\n", WIFI_SSID);
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    g_wifiBackoff = growBackoff(g_wifiBackoff);
}

static void mqttTick() {
    if (WiFi.status() != WL_CONNECTED) return;
    if (mqtt.connected()) { g_mqttBackoff = 1000; mqtt.loop(); return; }

    uint32_t now = millis();
    if (now - g_tMqttTry < g_mqttBackoff) return;
    g_tMqttTry = now;

    Serial.printf("[mqtt] connecting to %s:%u (TLS)\n", MQTT_HOST, MQTT_PORT);

    // The token is client_id AND username; password is empty. Same as the SCK
    // firmware, and the reason a DIY node needs no device id at all.
    if (mqtt.connect(SC_DEVICE_TOKEN, SC_DEVICE_TOKEN, "")) {
        Serial.printf("[mqtt] connected - RSSI %d dBm\n", WiFi.RSSI());
        g_mqttBackoff = 1000;
        queueDrain();
    } else {
        Serial.printf("[mqtt] failed (rc=%d) - will retry\n", mqtt.state());
        g_mqttBackoff = growBackoff(g_mqttBackoff);
    }
}

// ============================================================================
// 8. SETUP / LOOP
// ============================================================================

void setup() {
    Serial.begin(115200);
    // Bounded wait. An unbounded `while (!Serial)` means a node that boots
    // after a power cut with nobody plugged in never leaves setup().
    uint32_t t0 = millis();
    while (!Serial && millis() - t0 < 3000) delay(10);
    delay(500);

    Serial.println("\n=== Making Sense Bali - SEN55 node (XIAO ESP32-S3) ===");
    printResetReason();

#if ESP_IDF_VERSION_MAJOR >= 5
    esp_task_wdt_config_t wdtCfg = {
        .timeout_ms     = WDT_TIMEOUT_S * 1000,
        .idle_core_mask = 0,
        .trigger_panic  = true
    };
    esp_task_wdt_init(&wdtCfg);          // already-initialised is fine
#else
    esp_task_wdt_init(WDT_TIMEOUT_S, true);
#endif
    esp_task_wdt_add(NULL);

    if (!LittleFS.begin(true)) {
        Serial.println("[fs] mount failed - offline buffering disabled");
    } else {
        g_queued = queueCount();
        if (g_queued) Serial.printf("[queue] %lu reading(s) survived the reboot\n",
                                    (unsigned long)g_queued);
    }

    g_softRecoveries = 0xFF;      // marks cold boot: always reset
    bringUpSensor("boot");
    g_softRecoveries = 0;

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);                // modem sleep adds seconds of latency
    wifiTick();

    configTime(0, 0, "pool.ntp.org", "time.google.com");   // UTC

    // For a node whose data a campaign cites, replace setInsecure() with
    // net.setCACert(ISRG_ROOT_X1_PEM) - the broker uses Let's Encrypt certs.
    // Skipping validation means anyone on the LAN can MITM the device token.
    net.setInsecure();

    snprintf(g_topic, sizeof(g_topic), "device/sck/%s/readings", SC_DEVICE_TOKEN);
    Serial.printf("[sc] topic: %s\n", g_topic);
    mqtt.setServer(MQTT_HOST, MQTT_PORT);
    if (!mqtt.setBufferSize(PAYLOAD_MAX_BYTES))
        Serial.println("[mqtt] could not grow buffer - publishes will be dropped");

    Serial.println("[sc] channel map:");
    int mapped = 0;
    for (int i = 0; i < M_COUNT; i++) {
        if (SC_SENSOR_ID[i]) { mapped++;
            Serial.printf("      %-12s -> id %d\n", METRIC_NAME[i], SC_SENSOR_ID[i]); }
        else
            Serial.printf("      %-12s -> (off)\n", METRIC_NAME[i]);
    }
    if (mapped == 0) Serial.println("[sc] WARNING: no channels mapped, nothing will publish");

    uint32_t now = millis();
    g_tSample = g_tPublish = g_tStatus = g_tFanClean = now;
}

void loop() {
    esp_task_wdt_reset();
    uint32_t now = millis();

    wifiTick();
    mqttTick();

    if (now - g_tSample >= SAMPLE_MS) {
        g_tSample = now;
        if (g_senOnline) sen55Sample();
        else             bringUpSensor("retry - sensor missing");
    }

    if (now - g_tStatus >= STATUS_MS) {
        g_tStatus = now;
        if (g_senOnline) sen55Status();
    }

    if (now - g_tPublish >= PUBLISH_MS) {
        g_tPublish = now;

        if (!timeIsValid()) {
            // A reading with a bogus timestamp is worse than no reading - the
            // platform may drop it or file it in 1970. Discard the interval.
            Serial.println("[sc] clock not set - discarding this interval");
            for (int i = 0; i < M_COUNT; i++) g_acc[i].reset();
        } else {
            static char obj[OBJ_MAX_BYTES];
            size_t len = buildReadingObject(obj, sizeof(obj));
            for (int i = 0; i < M_COUNT; i++) g_acc[i].reset();

            if (len == 0) {
                Serial.println("[sc] no valid readings this cycle - nothing published");
            } else {
                static char one[1][OBJ_MAX_BYTES];
                memcpy(one[0], obj, len + 1);
                if (!sendObjects(one, 1)) queuePush(obj);
                else                      queueDrain();
            }
        }
        Serial.printf("[stats] published=%lu queued=%lu heap=%lu\n",
                      (unsigned long)g_published, (unsigned long)g_queued,
                      (unsigned long)ESP.getFreeHeap());
    }

    if (FAN_CLEAN_MS && now - g_tFanClean >= FAN_CLEAN_MS) {
        g_tFanClean = now;
        if (g_senOnline) {
            uint16_t err = sen5x.startFanCleaning();
            if (err) logSenError("startFanCleaning()", err);
            else     Serial.println("[sen55] manual fan cleaning started");
        }
    }

    delay(5);
}
