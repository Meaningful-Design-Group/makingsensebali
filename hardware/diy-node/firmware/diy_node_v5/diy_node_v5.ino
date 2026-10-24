// Making Sense Bali — DIY Node firmware
// v5 (one image for every sensor combination: HM3301, SEN5x, BME680,
//     PMS5003/PMS5003T, SHT4x, SCD4x)
//    ESP32-C3 SuperMini AND XIAO ESP32-S3
//
// Boards:  MakerGO ESP32-C3 SuperMini  |  Seeed XIAO ESP32-S3
//          Tools -> USB CDC On Boot: Enabled (BOTH boards, or Serial is silent)
// Sensors: any of, detected at boot, no build flags —
//            Seeed Grove HM3301         I2C 0x40   PM1 / PM2.5 / PM10
//            Sensirion SEN50/54/55      I2C 0x69   PM1 / 2.5 / 4 / 10, T, RH, VOC, NOx
//              (e.g. Seeed "Grove - All in one Environmental Sensor SEN5X")
//            Bosch BME680               I2C 0x76/0x77   T, RH, pressure, gas
//            Sensirion SHT40/41/45      I2C 0x44   T, RH
//            Sensirion SCD40/41         I2C 0x62   CO2, T, RH
//            Plantower PMS5003(T)       UART RX on XIAO D7 (GPIO44 S3, GPIO20 C3)
//                                       PM1 / PM2.5 / PM10, and T, RH on the T
// Platform: publishes to the Mosquitto of a PLANETAI node on the same network
//           first (plain MQTT, the node's broker user and password), and to
//           mqtt.smartcitizen.me over TLS when there is no node or it stops
//           answering.
// Updates:  checks makingsense.fablabbali.com/flash/ once a day and installs
//           a newer build by itself; a build that cannot get back online is
//           rolled back by the bootloader.
//
// Repo: https://github.com/Meaningful-Design-Group/makingsensebali
// License: MIT
//
// ---------------------------------------------------------------------------
// WHAT GREW IN v5 AFTER v5-c3a5418 (the build on the flash page, 20 Oct 2026)
// ---------------------------------------------------------------------------
//  * THREE MORE SENSORS, SAME RULE. SHT4x (0x44), SCD4x (0x62) and a Plantower
//    PMS5003 or PMS5003T on the UART join the boot inventory. Absent is "not
//    fitted", silent, as before. A node built for v5-c3a5418 sees no change.
//    The Plantower is only listened to: RX on XIAO D7, the node never drives
//    a pin for it, so a board with something else wired there is not touched.
//    Published on the IDs the SCK publishes the same parts on:
//      PMS5003   89 PM1   87 PM2.5   88 PM10   (118 T, 119 RH from a PMS5003T)
//      SCD4x    258 CO2  259 T   260 RH
//    Smart Citizen has no SHT4x entry (checked 24 Oct 2026), so the SHT4x goes
//    on 79 / 80, its "External Sensirion SHT31" channels: the kits' own
//    external T/RH probe, the same family one generation older.
//
//  * PLANETAI NODE FIRST, SMART CITIZEN SECOND. With a node set in the portal
//    the device publishes there. If the node misses 3 connections in a row,
//    the device publishes to Smart Citizen directly (same topic, same bytes)
//    and tries the node again every 10 minutes. A portal box turns that
//    fallback off, for a sensor whose readings should only ever reach the
//    node. With no node set it publishes to Smart Citizen, exactly as before.
//    The setup QR can now carry the node too: /t?token=..&host=..&port=..
//    &user=..&pass=.. fills all five fields in one scan.
//
//  * IT UPDATES ITSELF. Once a day (first check 5 minutes after boot) the node
//    reads the flash page's manifest.json over HTTPS, verified against the
//    core's CA bundle, and if the build there is not the one it runs it
//    downloads that chip's app.bin into the spare OTA slot and reboots. The
//    new build has 30 minutes to fetch the manifest again; until it does, the
//    bootloader keeps the old one, and a reboot in that window rolls back. A
//    rolled-back build is remembered and not tried again. Builds from the IDE
//    carry no build tag and never update themselves. A portal box turns
//    updates off.
//
// ---------------------------------------------------------------------------
// WHAT CHANGED vs v4
// ---------------------------------------------------------------------------
//  * ONE FIRMWARE, WHATEVER IS PLUGGED IN. At boot the node scans the bus
//    and brings up whichever of HM3301 (0x40), SEN5x (0x69) and BME680
//    (0x76/0x77) answer. There are no build flags to set and nothing to
//    configure. A sensor that is not plugged in is "not fitted", which is a
//    normal state: it gets one line in the boot inventory and nothing else —
//    no "not found" warnings every minute, no red on the status page.
//
//  * SEN5x SUPPORT. Driven over raw I2C (no Sensirion library), command words
//    and CRC from Sensirion's embedded-i2c-sen5x. The model is read from the
//    sensor itself, so SEN50 (PM only), SEN54 (+T/RH/VOC) and SEN55 (+NOx)
//    all work: a channel the model does not have comes back as Sensirion's
//    "no value" sentinel and is simply not published.
//    Published on the Smart Citizen catalogue IDs the SCK 2.3 uses for the
//    same part (fablabbcn/smartcitizen-kit-2x, lib/Sensors/Sensors.h):
//      193 PM1   194 PM2.5   195 PM4   196 PM10
//      203 RH    204 T       205 VOC index   206 NOx index
//    so a DIY node with a SEN5x is directly comparable with the kits.
//    Particle number and typical particle size are NOT published: the kits
//    publish TPS 100x too large (see diy_node_display), and copying that bug
//    or contradicting it on the same channel are both worse than leaving it.
//
//  * BOTH PM SENSORS AT ONCE IS ALLOWED, AND USEFUL. HM3301 and SEN5x have
//    different addresses and different channel IDs, so with both fitted the
//    node publishes both. That is a co-location in one box: the shared
//    correction curve for the HM3301 can be checked against a SEN5x on every
//    node that carries one, not only at two sites.
//
//  * SENSORS CAN COME AND GO. Every 5 minutes the node quietly checks for a
//    sensor that was not there at boot and brings it up if it now answers. A
//    fitted sensor that fails 3 reads in a row is marked as stopped and logged
//    once (that one IS a fault — a loose cable or a dead fan); it is picked
//    up again by the same 5-minute check when it comes back.
//
//  * POWER, the thing firmware cannot fix: the SEN5x runs a laser and a fan
//    and needs 5 V (Sensirion: 4.5–5.5 V, ~70 mA while measuring); its I2C
//    lines are fine at 3.3 V. If it does not appear in the boot inventory,
//    check the Grove port's supply before suspecting anything else.
//
//  * SEN5x temperature and humidity are published as the sensor reports
//    them, with Sensirion's temperature offset left at 0. Inside an enclosure
//    they will read warm like the BME680 does. Same rule: correct in the
//    pipeline, don't cite as calibrated.
//
// ---------------------------------------------------------------------------
// WHAT CHANGED vs v3
// ---------------------------------------------------------------------------
//  * WHERE IT PUBLISHES IS A SETTING. Four new portal fields — broker host,
//    port, user, password — stored in NVS. Left alone, the node behaves exactly
//    as v3: mqtt.smartcitizen.me:8883, TLS, the token as its identity. Pointed
//    at a PLANETAI node (`planetai broker` on that machine prints the values),
//    it publishes the SAME topic and the SAME bytes there, over plain MQTT on
//    1883 with the broker's user and password. Nothing about the readings
//    changes; only who hears them first. The node keeps them with this
//    device's own timestamp and, for a token listed in its SC_FORWARD, passes
//    the message on to Smart Citizen unchanged — so the device keeps its page
//    there and the campaign dashboard keeps reading it, and a reading taken
//    while the internet was down is no longer lost.
//
//  * THE NODE CAN SAY WHERE IT IS. When the broker is a PLANETAI node, the
//    name, site and height from the portal are published once per connection
//    as a retained `device/sck/<token>/meta` message, with a new portal
//    checkbox: indoors. That checkbox matters — a PLANETAI node never lets an
//    indoor sensor into an outdoor average. Nothing of this is sent to Smart
//    Citizen; the Smart Citizen path stays byte-for-byte what v3 sent.
//
//  * A LOCAL BROKER NEEDS NO SMART CITIZEN ACCOUNT. The token is still the
//    device's identity on the wire, but for a node that will only ever talk
//    to a PLANETAI node, any six characters you choose will do.
//
// ---------------------------------------------------------------------------
// WHAT CHANGED vs v2
// ---------------------------------------------------------------------------
//  * THE NODE NOW HAS A NAME. Three new portal fields — name, site, mounting
//    height — stored in NVS beside the token. They give the node an identity
//    you can reach and read without a laptop.
//
//  * READ IT WITHOUT A LAPTOP. After setup the node serves a status page on
//    the local network: live readings, which sensors answered, WiFi signal,
//    whether the last publish left the node, uptime. Reachable two ways:
//        http://<name>.local        (mDNS — most phones and laptops)
//        http://<the node's IP>     (printed on the portal's success page)
//    This replaces the serial monitor for everything except first-boot
//    diagnosis, which is the single biggest workshop simplification here.
//
//  * RECONFIGURE FROM THAT PAGE. A button reopens the setup portal without
//    the BOOT-button timing trick. The portal stays password-protected, so
//    the button on an open LAN page cannot hand the node to a stranger — it
//    only reboots into a portal that still needs PORTAL_PASSWORD to join.
//
// ---------------------------------------------------------------------------
// WHAT THE NEW FIELDS DO *NOT* DO — read this before promising anything
// ---------------------------------------------------------------------------
// Name and site are LOCAL ONLY. They do not reach Smart Citizen.
//
// Verified against the platform, not assumed:
//   - The MQTT topics a device may publish are readings, readings/raw, info,
//     hello and device/inventory. None carries name, location or any other
//     metadata.  (fablabbcn/smartcitizen-api, docs/mqtt.md)
//   - The `info` topic carries time, hw_ver, id, sam_ver, sam_bd, mac,
//     esp_ver — hardware only.  (SckBase.cpp, the JSON built for it)
//   - A DIY node has no numeric device id to PUT metadata to, and the REST
//     API authenticates device updates with a *user* key, not the device
//     token.
//
// So a node's display name and its coordinates are still set by hand on its
// device page at smartcitizen.me. These fields exist so the node is
// identifiable on your own network and in your own records — nothing more.
// Do not let a participant believe filling them in registers anything.
//
// There is deliberately NO latitude/longitude field. The captive portal is
// served over plain HTTP at 192.168.4.1, and browsers refuse the Geolocation
// API outside a secure context, so the phone's GPS is unavailable — it would
// mean typing coordinates by hand, which at a workshop table produces wrong
// coordinates. The paper site card already captures the place properly, and
// the campaign's records are where a location belongs.
//
// ---------------------------------------------------------------------------
// SETUP FLOW
// ---------------------------------------------------------------------------
//  FIRST BOOT (or no saved WiFi): the node opens an access point named
//  MSB-Node-xxxxxx (xxxxxx = last 3 bytes of its MAC). Join it from a phone
//  (password below), the portal opens — or browse to 192.168.4.1. Pick the
//  real WiFi, type its password, fill what's asked, Save.
//
//  CONFIGURED BOOT: connects in seconds, no portal.
//
//  SAVED WIFI UNREACHABLE: portal opens for 3 minutes, then the node reboots
//  and tries the saved network again. Deliberate — a router power blip must
//  NOT strand the node in AP mode forever.
//
//  RECONFIGURE: the button on the status page, or hold BOOT while the node
//  starts (~2 s after plugging in), or power it up out of range of its
//  saved WiFi. Saved values are prefilled.
//
//  BATCH PREP (the real simplification): flash the fleet, then set each
//  node's token and name once at the bench over its own portal, and label
//  the enclosure. A participant then only ever picks their WiFi and types
//  its password — the six-character token, which is the step that actually
//  goes wrong, never reaches the workshop table.
//
// Everything else — I2C pin auto-detect, no-fake-zeros, no-NaN, the IAQ
// approximation and its honest limitations — is carried over unchanged.
//
// KNOWN LIMITATION, still not fixed here: channels 237/238 are labelled
// "heat-compensated" in the Smart Citizen catalog but this firmware
// publishes bme.temperature / bme.humidity RAW. Expect T ~1-3 °C high and
// RH correspondingly low in an enclosure. Corrections belong in the data
// pipeline, not here. Don't cite this as calibrated temperature.
//
// Libraries (Arduino Library Manager):
//   - WiFiManager              (tzapu)  — tested with 2.0.17
//   - Adafruit BME680 Library  (depends on Adafruit Unified Sensor)
//   - PubSubClient             (Nick O'Leary)
//   - ArduinoJson v7.x
//   ESPmDNS and WebServer ship with the arduino-esp32 core — no install.

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WiFiManager.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <ArduinoJson.h>
#include <ESPmDNS.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <HTTPUpdate.h>
#include <esp_ota_ops.h>
#include <time.h>
#include "decoders.h"   // PMS5003, SHT4x, SCD4x and the Sensirion CRC: tested off the board

// HM3301 is read directly over I2C without the Seeed_HM330X library — the
// Seeed library's u8/u16 typedefs don't compile against the modern
// arduino-esp32 core. The protocol is simple; see readHM3301().

// ============================================================================
// CONFIGURATION — fleet-wide constants only. Nothing device-specific here.
// ============================================================================

const char* PORTAL_PASSWORD = "makingsense";   // AP join password
const uint16_t PORTAL_TIMEOUT_S = 180;         // portal lifetime before reboot

// PMS_RX_PIN is XIAO D7 on both XIAOs, the pin the PMS5003's TX goes to (and
// RX on the C3 SuperMini). OTA_CHIP is the chipFamily name in the manifest.
#if defined(CONFIG_IDF_TARGET_ESP32S3)
  const int BOOT_BTN_PIN = 0;
  const int PMS_RX_PIN   = 44;
  const char* OTA_CHIP   = "ESP32-S3";
#elif defined(CONFIG_IDF_TARGET_ESP32C3)
  const int BOOT_BTN_PIN = 9;
  const int PMS_RX_PIN   = 20;
  const char* OTA_CHIP   = "ESP32-C3";
#else
  const int BOOT_BTN_PIN = 0;
  const int PMS_RX_PIN   = -1;
  const char* OTA_CHIP   = "";
#endif

// Smart Citizen sensor IDs — SC global-catalog IDs for Bosch BME68X and
// Seeed HM-3301. Same for every node. For a Basic kit (no HM-3301), set the
// three PM IDs to 0 to skip publishing them.
const int SC_ID_PM1      = 233;
const int SC_ID_PM25     = 234;
const int SC_ID_PM10     = 235;
const int SC_ID_TEMP     = 237;
const int SC_ID_HUM      = 238;
const int SC_ID_PRESSURE = 239;
const int SC_ID_GAS      = 240;
const int SC_ID_IAQ      = 241;

// Sensirion SEN5x — the IDs the SCK 2.3 publishes the same part on
// (fablabbcn/smartcitizen-kit-2x, lib/Sensors/Sensors.h, OneSensor id field).
const int SC_ID_SEN_PM1  = 193;
const int SC_ID_SEN_PM25 = 194;
const int SC_ID_SEN_PM4  = 195;
const int SC_ID_SEN_PM10 = 196;
const int SC_ID_SEN_HUM  = 203;
const int SC_ID_SEN_TEMP = 204;
const int SC_ID_SEN_VOC  = 205;
const int SC_ID_SEN_NOX  = 206;

// Plantower PMS5003 — the IDs the SCK 2.x publishes its PM board on
// (api.smartcitizen.me/v0/sensors: 86 "PMS5003_AVG" and its children).
const int SC_ID_PMS_PM1  = 89;
const int SC_ID_PMS_PM25 = 87;
const int SC_ID_PMS_PM10 = 88;
const int SC_ID_PMS_TEMP = 118;   // PMS5003T only: its own element, inside the sensor's case
const int SC_ID_PMS_HUM  = 119;

// Sensirion SCD4x — the IDs the SCK 2.3 publishes it on (Sensors.h).
const int SC_ID_SCD_CO2  = 258;
const int SC_ID_SCD_TEMP = 259;
const int SC_ID_SCD_HUM  = 260;

// Sensirion SHT4x — no SHT4x entry on Smart Citizen; "External Sensirion SHT31".
// Change these two if the platform adds one.
const int SC_ID_SHT_TEMP = 79;
const int SC_ID_SHT_HUM  = 80;

const char*    FW_VERSION = "v5";
const char*    DEFAULT_MQTT_HOST = "mqtt.smartcitizen.me";   // Smart Citizen's broker: TLS, token as identity
const uint16_t DEFAULT_MQTT_PORT = 8883;

// The build's own tag, stamped by CI (-DFW_BUILD_TAG=v5-<sha>) and compared
// with the manifest's "version". A build from the IDE has none, and a node
// running one never updates itself: the published build would overwrite a
// bench build within a day.
#define XSTR_(x) #x
#define XSTR(x) XSTR_(x)
#ifdef FW_BUILD_TAG
const char* FW_BUILD = XSTR(FW_BUILD_TAG);
#else
const char* FW_BUILD = "";
#endif

const char*    OTA_MANIFEST_URL       = "https://makingsense.fablabbali.com/flash/firmware/diy-node/manifest.json";
const uint32_t OTA_FIRST_CHECK_MS     = 5UL * 60UL * 1000UL;
const uint32_t OTA_INTERVAL_MS        = 24UL * 60UL * 60UL * 1000UL;
const uint32_t OTA_VERIFY_RETRY_MS    = 60UL * 1000UL;        // a fresh build retries its first check this often
const uint32_t OTA_VERIFY_DEADLINE_MS = 30UL * 60UL * 1000UL; // ... and is rolled back if none succeeds by then

const uint32_t MQTT_RETRY_MS              = 10UL * 1000UL;
const uint8_t  NODE_FAILS_BEFORE_FALLBACK = 3;
const uint32_t NODE_RETRY_MS              = 10UL * 60UL * 1000UL;  // from Smart Citizen, try the node again

const uint32_t PUBLISH_INTERVAL_MS     = 60UL * 1000UL;
const uint32_t WIFI_RETRY_INTERVAL_MS  = 15UL * 1000UL;
const uint32_t SENSOR_RESCAN_MS        = 5UL * 60UL * 1000UL;  // look for sensors that weren't there
const uint8_t  SENSOR_LOST_AFTER       = 3;                    // consecutive failed reads = stopped

// A Smart Citizen device token is six characters — verified against the SCK
// firmware, lib/Shared/Config.h: `struct Token { ... char token[7]="null"; }`.
// The field is sized larger so a paste with stray characters is visible and
// correctable rather than silently truncated.
const int TOKEN_FIELD_LEN = 16;
const int NAME_FIELD_LEN  = 32;
const int SITE_FIELD_LEN  = 64;
const int HOST_FIELD_LEN  = 64;
const int USER_FIELD_LEN  = 32;
const int PASS_FIELD_LEN  = 64;

struct I2CPins { int sda; int scl; };
const I2CPins I2C_CANDIDATES[] = {
  {5, 6},  {6, 5},     // Seeed XIAO ESP32-S3 Grove (D4/D5) — fleet standard
  {8, 9},  {9, 8},     // C3 SuperMini default
  {6, 7},  {7, 6},     // Seeed XIAO ESP32-C3 Grove (D4/D5)
  {10, 9}, {9, 10},    // seen on a hand-wired Bali unit
  {10, 8}, {8, 10},    // also seen in a bench scan of that unit
  {4, 5},  {5, 4}      // safe spares, off the strapping pins
};
const int I2C_CANDIDATE_COUNT = sizeof(I2C_CANDIDATES) / sizeof(I2C_CANDIDATES[0]);

int I2C_SDA_PIN = -1;
int I2C_SCL_PIN = -1;

// ============================================================================
// STATE
// ============================================================================

Adafruit_BME680 bme;

constexpr uint8_t HM3301_I2C_ADDR       = 0x40;
constexpr uint8_t HM3301_SELECT_I2C_CMD = 0x88;
constexpr uint8_t SEN5X_ADDR            = 0x69;
constexpr uint8_t BME680_ADDR_A         = 0x76;
constexpr uint8_t BME680_ADDR_B         = 0x77;
constexpr uint8_t SHT4X_ADDR            = 0x44;
constexpr uint8_t SCD4X_ADDR            = 0x62;

// One SEN5x measurement. NAN = the sensor has no such channel (SEN50 has no
// T/RH/VOC, SEN54 no NOx) or did not have a valid value yet.
struct Sen5xReading {
  float pm1 = NAN, pm25 = NAN, pm4 = NAN, pm10 = NAN;   // µg/m³
  float rh = NAN, tempC = NAN;                          // %RH, °C
  float voc = NAN, nox = NAN;                           // Sensirion index, 1–500
};

// Two transports, one MQTT client: TLS for Smart Citizen on 8883, plain TCP
// for a PLANETAI node's Mosquitto on 1883. connectMQTT() picks by port.
WiFiClientSecure tlsNet;
WiFiClient       plainNet;
PubSubClient mqtt(tlsNet);
Preferences prefs;
WebServer status(80);

// --- identity, from NVS ---
String scToken;      // Smart Citizen device token — the publishing identity
String nodeName;     // human name, local only
String nodeSite;     // where it hangs, local only
String nodeHeight;   // metres above ground, local only
bool   nodeIndoor = false;   // published in `meta` to a PLANETAI node; never to Smart Citizen

// --- where it publishes, from NVS ---
// brokerHost is the PLANETAI node; Smart Citizen's host (or nothing) means no node.
String   brokerHost;
uint16_t brokerPort = DEFAULT_MQTT_PORT;
String   brokerUser;         // empty = the Smart Citizen way: token as username, no password
String   brokerPass;
bool     scFallback = true;  // publish to Smart Citizen while the node does not answer
bool     otaEnabled = true;

// --- where it is publishing right now ---
bool     onNode        = false;   // the live connection is to the PLANETAI node
uint8_t  nodeFails     = 0;
uint32_t fallbackSince = 0;       // millis() the node was given up on; 0 = not falling back
uint32_t lastMqttTry   = 0;

// --- self-update ---
bool     otaPendingVerify = false;   // this build arrived by OTA and has not proved itself yet
uint32_t lastOtaCheck     = 0;
String   otaStatus        = "not checked yet";

uint32_t lastPublish   = 0;
uint32_t lastWifiRetry = 0;

bool g_bmeOnline = false;
bool g_hmOnline  = false;
bool g_senOnline = false;
bool g_shtOnline = false;
bool g_scdOnline = false;
bool g_pmsOnline = false;

// "Was fitted, then stopped answering" — the only sensor state that is a fault.
bool g_bmeLost = false, g_hmLost = false, g_senLost = false;
bool g_shtLost = false, g_scdLost = false, g_pmsLost = false;
uint8_t bmeFails = 0, hmFails = 0, senFails = 0, shtFails = 0, scdFails = 0, pmsFails = 0;
uint32_t lastSensorScan = 0;

bool     pmsIsT   = false;   // a PMS5003T, told apart by its frames (see PLANTOWER below)
uint32_t pmsSince = 0;       // when it was found; nothing is published for its first 30 s

char sen5xModel[17] = "";      // product name as the sensor reports it, e.g. "SEN55"

// Last cycle, for the status page.
float  lastT = NAN, lastRH = NAN, lastP = NAN, lastGas = NAN, lastIAQ = NAN;
uint16_t lastPM1 = 0, lastPM25 = 0, lastPM10 = 0;
bool   lastBmeOk = false, lastHmOk = false, lastSenOk = false;
Sen5xReading lastSen;
float  lastShtT = NAN, lastShtRH = NAN;
Scd4xReading lastScd;
PmsReading   lastPms;
bool   lastShtOk = false, lastScdOk = false, lastPmsOk = false;
bool   lastPublishOk = false;
String lastPublishAt = "never";
uint32_t publishCount = 0, publishFailCount = 0;

float gasBaselineOhm = 0.0f;
volatile bool reopenPortalRequested = false;

// ============================================================================
// IDENTITY HELPERS
// ============================================================================

String macSuffix() {
  return String((uint32_t)(ESP.getEfuseMac() & 0xFFFFFF), HEX);
}

String apName() {
  return "MSB-Node-" + macSuffix();
}

// Lowercase, alphanumerics and hyphens only — what mDNS will accept. Falls
// back to the MAC suffix so an unnamed node is still reachable.
String mdnsHost() {
  String h;
  String src = nodeName.length() ? nodeName : ("msb-" + macSuffix());
  for (size_t i = 0; i < src.length() && h.length() < 24; i++) {
    char c = src[i];
    if (c >= 'A' && c <= 'Z') c = c - 'A' + 'a';
    if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9')) h += c;
    // Any other character separates. Treating only space/-/_ as separators
    // welded "Ubud/Pejeng" into "ubudpejeng"; a slash is a word break to a
    // reader and must be one here too.
    else if (h.length() && h[h.length()-1] != '-') h += '-';
  }
  while (h.length() && h[h.length()-1] == '-') h.remove(h.length() - 1);
  if (h.length() == 0) h = "msb-" + macSuffix();
  return h;
}

String sanitizeToken(String t) {
  t.trim();
  return t;
}

// Never print a whole token to a page anyone on the LAN can load.
String maskedToken() {
  if (scToken.length() == 0) return "NOT SET";
  if (scToken.length() <= 2) return "**";
  return scToken.substring(0, 2) + String("****");
}

String uptimeStr() {
  uint32_t s = millis() / 1000;
  char buf[32];
  snprintf(buf, sizeof(buf), "%lud %02lu:%02lu:%02lu",
           (unsigned long)(s / 86400), (unsigned long)((s % 86400) / 3600),
           (unsigned long)((s % 3600) / 60), (unsigned long)(s % 60));
  return String(buf);
}

// ============================================================================
// LOOK — the setup portal and the status page share one theme
//
// The PLANETAI layer, cut down to what a captive portal can carry: paper
// #F9F5F2 / ink #171717, square corners, numbers and ids in mono, blue only for
// identity (the node's id chip), green only for an act taken (a publish that
// left), red only as an edge on a failure notice — never a fill, never text.
// State is carried by weight, opacity and a dashed edge, not by hue.
// No web fonts: a phone joined to the node's access point has no internet, so
// Figtree/JetBrains Mono are named first and the system stack takes over.
// Logos are inline SVG data URIs (Fab Lab Bali wordmark converted to paths, so
// it does not depend on Figtree being installed; ~8 kB together).
// ============================================================================

const char THEME_CSS[] PROGMEM =
  "<style>:root{--p:#F9F5F2;--i:#171717;--m:#5f5b57;--h:#d8d2cc;--b:#20388D;--g:#00A057;--r:#E62038}html,body{mar"
  "gin:0;background:var(--p);color:var(--i)}body,h1,h3,.c,div,input,select,button{font-family:Figtree,system-ui,-"
  "apple-system,'Segoe UI',Roboto,sans-serif;text-align:left}.wrap{display:block;max-width:520px;min-width:0;marg"
  "in:0 auto;padding:0 16px 40px}.top{background:var(--i);margin:0 -16px 18px;padding:12px 16px;display:flex;alig"
  "n-items:center}.top img{display:block;width:auto}.top .flb{height:40px}.top .fc{height:36px;margin-left:auto}."
  "id{display:inline-block;font:12px/1 ui-monospace,'JetBrains Mono',SFMono-Regular,Menlo,Consolas,monospace;lett"
  "er-spacing:.06em;border:1px solid var(--b);padding:6px 8px;margin:0 0 6px}h1{font-size:22px;font-weight:700;ma"
  "rgin:6px 0 2px;line-height:1.2}h3{font-size:13px;font-weight:400;color:var(--m);margin:0 0 16px}input,button,s"
  "elect,.msg{border-radius:0}input:not([type=checkbox]){background:#fff;border:1px solid var(--i);font-size:16px"
  ";padding:10px;color:var(--i)}input:focus{outline:2px solid var(--b);outline-offset:0}input[type=checkbox]{acce"
  "nt-color:var(--i);width:18px;height:18px;vertical-align:middle;margin-right:6px}button,input[type=submit]{back"
  "ground:var(--i);color:var(--p);border:0;font-size:16px;font-weight:600;line-height:2.8rem}button.D{background:"
  "transparent;color:var(--i);border:1px dashed var(--i)}a{color:var(--i);font-weight:600}a:hover{color:var(--b)}"
  "label{font-size:14px}hr{border:0;border-top:1px solid var(--i);margin:20px 0 4px}.msg{border:1px solid var(--i"
  ");border-left-width:6px;background:transparent}.msg.S{border-left-color:var(--g)}.msg.D{border-left-color:var("
  "--r)}.msg.P{border-left-color:var(--b)}.q{font:12px ui-monospace,'JetBrains Mono',SFMono-Regular,Menlo,Consola"
  "s,monospace}.sec{font:600 11px/1.2 ui-monospace,'JetBrains Mono',SFMono-Regular,Menlo,Consolas,monospace;lette"
  "r-spacing:.14em;text-transform:uppercase;margin:22px 0 4px}.hint{font-size:13px;color:var(--m);margin:0 0 8px;"
  "line-height:1.45}.foot{margin-top:30px;padding-top:10px;border-top:1px solid var(--h);font:11px/1.5 ui-monospa"
  "ce,'JetBrains Mono',SFMono-Regular,Menlo,Consolas,monospace;color:var(--m)}table{width:100%;border-collapse:co"
  "llapse;margin:0 0 20px}th{text-align:left;font-weight:400;color:var(--m);padding:7px 10px 7px 0;width:46%;font"
  "-size:14px;vertical-align:top}td{padding:7px 0;font-size:14px;border-bottom:1px solid var(--h)}.n{font-family:"
  "ui-monospace,'JetBrains Mono',SFMono-Regular,Menlo,Consolas,monospace}.on{font-weight:600}.off{opacity:.45}.st"
  "op{font-weight:700;border:1px dashed var(--i);padding:1px 5px}.mk{display:inline-block;width:9px;height:9px;ba"
  "ckground:var(--g);margin-right:6px}.note{color:var(--m);font-size:13px;line-height:1.5;border-top:1px solid va"
  "r(--h);padding-top:14px}</style>";

const char LOGO_FLB[] PROGMEM =
  "data:image/svg+xml,%3Csvg version='1.1' viewBox='0 0 1759 755.9' xmlns='http://www.w3.org/2000/svg'%3E%3Cdefs%"
  "3E%3CclipPath id='d'%3E%3Cpath transform='translate(-744.2 -448)' d='m0 1992h1708v-1992h-1708z'/%3E%3C/clipPat"
  "h%3E%3CclipPath id='c'%3E%3Cpath transform='translate(-241.6 -566.4)' d='m0 1992h1708v-1992h-1708z'/%3E%3C/cli"
  "pPath%3E%3CclipPath id='b'%3E%3Cpath transform='translate(-467.6 -198.7)' d='m0 1992h1708v-1992h-1708z'/%3E%3C"
  "/clipPath%3E%3CclipPath id='a'%3E%3Cpath transform='translate(-673.1 -578.3)' d='m0 1992h1708v-1992h-1708z'/%3"
  "E%3C/clipPath%3E%3C/defs%3E%3Cg transform='translate(-236.4 -1681)'%3E%3Cg%3E%3Cpath transform='matrix(1.333 0"
  " 0 -1.333 992.3 2059)' d='m0 0c0 156.6-126.9 283.5-283.5 283.5-156.6 0-283.5-126.9-283.5-283.5s126.9-283.5 283"
  ".5-283.5c156.6 0 283.5 126.9 283.5 283.5' clip-path='url(%23d)' fill='%23f9f0d1'/%3E%3Cpath transform='matrix("
  "1.333 0 0 -1.333 322.1 1901)' d='m0 0c-2.807 1.621-6.387 0.548-7.868-2.336-61.72-120.2-18.84-268.9 99.45-337.2"
  " 36.24-20.92 75.48-31.94 114.6-33.9 3.233-0.162 5.945 2.411 5.946 5.647l1e-3 16.97c0 2.07-1.132 3.975-2.951 4."
  "965l-50.52 27.5c-5.516 3.003-8.921 8.808-8.849 15.09l0.302 26.44c0.052 4.591 2.619 8.795 6.697 10.9 3.239 1.67"
  "5 5.959 3.245 7.239 3.984 28.94 17.14 28.32 69.28 3.083 112.1-25.23 42.77-68.95 58.31-94.47 43.25-28.99-17.06-"
  "35.58-58.19-12.04-101.9 6.54-12.09 15.11-22.58 20.69-29.09 2.055-2.401 3.115-5.493 2.974-8.65l-0.841-18.73c-0."
  "191-4.248-4.828-6.773-8.499-4.627l-43.62 25.49c-8.698 5.082-14.03 14.41-14 24.48l0.591 206.1c6e-3 2.025-1.072 "
  "3.899-2.826 4.912z' clip-path='url(%23c)' fill='%23faa51c'/%3E%3Cpath transform='matrix(1.333 0 0 -1.333 623.4"
  " 2391)' d='m0 0c0-3.241 2.719-5.805 5.957-5.646 134.9 6.634 242.3 118.1 242.3 254.7 0 41.84-10.08 81.34-27.94 "
  "116.2-1.476 2.88-5.06 3.943-7.863 2.325l-14.7-8.482c-1.793-1.036-2.877-2.968-2.825-5.038l1.446-57.5c0.158-6.27"
  "9-3.167-12.13-8.642-15.21l-23.05-12.96c-4.002-2.25-8.926-2.128-12.79 0.349-3.069 1.968-5.79 3.538-7.069 4.277-"
  "29.31 16.49-74.16-10.12-98.58-53.36s-16.02-88.87 9.778-103.4c29.27-16.58 68.19-1.713 94.31 40.55 7.201 11.71 1"
  "1.99 24.38 14.85 32.46 1.052 2.979 3.2 5.444 6.005 6.9l16.64 8.636c3.775 1.959 8.279-0.794 8.257-5.047l-0.263-"
  "50.52c-0.053-10.07-5.463-19.36-14.2-24.37l-178.8-102.5c-1.757-1.007-2.84-2.878-2.841-4.903z' clip-path='url(%2"
  "3b)' fill='%234b8e86'/%3E%3Cpath transform='matrix(1.333 0 0 -1.333 897.5 1885)' d='m0 0c2.807 1.62 3.668 5.25"
  "8 1.911 7.982-73.22 113.5-223.5 150.8-341.8 82.48-36.24-20.92-65.4-49.4-86.65-82.28-1.757-2.719-0.885-6.354 1."
  "918-7.972l14.69-8.485c1.793-1.035 4.009-1.008 5.775 0.072l49.08 30c5.358 3.276 12.09 3.322 17.49 0.119l22.75-1"
  "3.48c3.95-2.34 6.307-6.665 6.094-11.25-0.169-3.642-0.169-6.783-0.169-8.261 0.372-33.63 45.84-59.16 95.5-58.7 4"
  "9.66 0.465 84.97 30.56 84.69 60.19-0.28 33.63-32.61 59.91-82.27 61.4-13.74 0.382-27.11-1.801-35.54-3.371-3.107"
  "-0.579-6.315 0.049-8.978 1.751l-15.8 10.09c-3.583 2.29-3.451 7.567 0.242 9.674l43.89 25.03c8.75 4.991 19.5 4.9"
  "48 28.21-0.114l178.2-103.6c1.751-1.018 3.912-1.021 5.666-9e-3z' clip-path='url(%23a)' fill='%23972f1f'/%3E%3C/"
  "g%3E%3Cg fill='%23f9f0d1' stroke-width='4.297' aria-label='FAB LAB'%3E%3Cpath d='m1105 1933v-120.3h71.5v13.23h"
  "-56.89v41.08h50.19v13.23h-50.19v52.76z'/%3E%3Cpath d='m1184 1933 48.98-120.3h15.12l48.98 120.3h-15.3l-13.92-34"
  ".2h-54.48l-13.92 34.2zm34.37-47.26h44.34l-22.17-54.83z'/%3E%3Cpath d='m1315 1933v-120.3h37.98q12.37 0 21.14 3."
  "781 8.765 3.781 13.58 11.17 4.812 7.218 4.812 17.7 0 8.765-3.953 15.47-3.953 6.531-11.17 10.66 8.937 4.297 13."
  "75 11.52 4.984 7.218 4.984 17.19 0 10.48-4.64 17.87-4.64 7.218-13.23 11.17-8.422 3.781-20.28 3.781zm14.44-13.0"
  "6h27.84q11.34 0 17.7-5.328 6.531-5.5 6.531-14.95 0-10.14-7.39-15.81-7.39-5.844-20.62-5.844h-24.06zm0-54.48h27."
  "16q9.968 0 15.64-5.328 5.672-5.328 5.672-14.78 0-9.796-6.703-14.95-6.531-5.328-18.56-5.328h-23.2z'/%3E%3Cpath "
  "d='m1463 1933v-120.3h14.61v107.1h56.72v13.23z'/%3E%3Cpath d='m1538 1933 48.98-120.3h15.12l48.98 120.3h-15.3l-1"
  "3.92-34.2h-54.48l-13.92 34.2zm34.37-47.26h44.34l-22.17-54.83z'/%3E%3Cpath d='m1668 1933v-120.3h37.98q12.37 0 2"
  "1.14 3.781 8.765 3.781 13.58 11.17 4.812 7.218 4.812 17.7 0 8.765-3.953 15.47-3.953 6.531-11.17 10.66 8.937 4."
  "297 13.75 11.52 4.984 7.218 4.984 17.19 0 10.48-4.64 17.87-4.64 7.218-13.23 11.17-8.422 3.781-20.28 3.781zm14."
  "44-13.06h27.84q11.34 0 17.7-5.328 6.531-5.5 6.531-14.95 0-10.14-7.39-15.81-7.39-5.844-20.62-5.844h-24.06zm0-54"
  ".48h27.16q9.968 0 15.64-5.328 5.672-5.328 5.672-14.78 0-9.796-6.703-14.95-6.531-5.328-18.56-5.328h-23.2z'/%3E%"
  "3C/g%3E%3Cg fill='%23f7a41f' stroke-width='11.12' aria-label='BALI'%3E%3Cpath d='m1106 2293v-311.4h105.4q32.03"
  " 0 56.06 9.788 24.02 9.788 37.37 29.81 13.35 19.58 13.35 48.94 0 18.24-9.343 33.81-8.898 15.13-25.36 26.25 21."
  "8 11.12 33.37 29.81 12.01 18.24 12.01 44.04 0 28.47-12.9 48.49-12.9 20.02-36.04 30.25t-54.28 10.23zm59.62-53.8"
  "3h54.28q21.8 0 34.26-10.68 12.46-11.12 12.46-29.36 0-19.13-13.79-29.81-13.79-11.12-37.82-11.12h-49.38zm0-130.8"
  "h47.16q20.02 0 31.59-10.23 11.57-10.23 11.57-28.92t-12.9-28.92-35.15-10.23h-42.27z'/%3E%3Cpath d='m1348 2293 1"
  "22.8-311.4h64.95l122.8 311.4h-64.51l-26.69-68.51h-128.1l-26.69 68.51zm111.2-122.3h88.09l-44.04-113z'/%3E%3Cpat"
  "h d='m1696 2293v-311.4h60.95v255.8h137v55.61z'/%3E%3Cpath d='m1935 2293v-311.4h60.95v311.4z'/%3E%3C/g%3E%3C/g%"
  "3E%3C/svg%3E";

const char LOGO_FC[] PROGMEM =
  "data:image/svg+xml,%3Csvg version='1.1' viewBox='0 0 320 321.7' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d"
  "='m240.2 137.7v-89.18c0-1.85-0.99-3.57-2.6-4.5l-74.98-43.29c-1.61-0.93-3.58-0.93-5.19 0l-74.98 43.29c-1.61 0.9"
  "3-2.6 2.64-2.6 4.5v89.18l77.57-44.79c1.61-0.93 3.58-0.93 5.19 0l77.57 44.79z' fill='%23f9f5f2'/%3E%3Cpath d='m"
  "160 276.4 77.24 44.59c1.61 0.93 3.58 0.93 5.19 0l74.98-43.29c1.61-0.93 2.6-2.64 2.6-4.5v-86.58c0-1.86-0.99-3.5"
  "7-2.6-4.5l-77.23-44.49v89.47c0 1.85-0.99 3.57-2.6 4.5l-77.57 44.79z' fill='%23f9f5f2'/%3E%3Cpath d='m160 276.4"
  "-77.24 44.59c-1.61 0.93-3.58 0.93-5.19 0l-74.98-43.29c-1.61-0.93-2.6-2.64-2.6-4.5v-86.58c0-1.86 0.99-3.57 2.6-"
  "4.5l77.23-44.49v89.47c0 1.85 0.99 3.57 2.6 4.5l77.57 44.79z' fill='%23f9f5f2'/%3E%3Cpolygon transform='transla"
  "te(-95.85 -95)' points='224.2 249.2 239.6 249.2 239.6 241.2 215.3 241.2 215.3 277 224.2 277 224.2 262.9 237.3 "
  "262.9 237.3 254.9 224.2 254.9' fill='%23f9f5f2'/%3E%3Cpath d='m155 146.2-11.81 35.85h9.02l2.47-8.21h10.54l2.47"
  " 8.21h9.22l-11.66-35.85h-10.26zm8 19.93h-6.15l3.05-10.51 3.09 10.51z' fill='%23f9f5f2'/%3E%3Cpath d='m207.9 16"
  "7.5c-0.55-1.1-1.25-2.01-2.07-2.71-0.82-0.69-1.73-1.21-2.7-1.53 0.83-0.31 1.56-0.8 2.18-1.44 0.64-0.66 1.15-1.5"
  " 1.53-2.5 0.37-0.99 0.56-2.2 0.56-3.6 0-2.84-0.87-5.16-2.59-6.9s-4.14-2.62-7.17-2.62h-17.43v35.85h18.96c1.38 0"
  " 2.67-0.28 3.84-0.83 1.16-0.55 2.18-1.31 3.03-2.26 0.84-0.95 1.51-2.08 1.98-3.35s0.71-2.64 0.71-4.06c0-1.58-0."
  "28-2.95-0.84-4.06zm-18.85 0.31h7.99c0.82 0 1.44 0.21 1.9 0.64 0.44 0.42 0.66 1.01 0.66 1.82v1.68c0 0.81-0.22 1"
  ".4-0.66 1.82-0.45 0.43-1.07 0.64-1.9 0.64h-7.99v-6.59zm9.31-9.96c0 0.81-0.21 1.42-0.65 1.86s-1.04 0.65-1.86 0."
  "65h-6.81v-6.49h6.81c0.81 0 1.42 0.21 1.86 0.65s0.65 1.04 0.65 1.86v1.48z' fill='%23f9f5f2'/%3E%3Cpath d='m126."
  "8 222.3c-4.16 0-7.41-1.4-9.78-4.21-2.37-2.8-3.55-6.88-3.55-12.21 0-2.67 0.3-5.02 0.91-7.05s1.49-3.75 2.64-5.14"
  " 2.55-2.45 4.21-3.16c1.65-0.71 3.51-1.07 5.57-1.07 2.76 0 5.07 0.6 6.94 1.8s3.33 2.98 4.39 5.34l-4.32 2.37c-0."
  "55-1.52-1.39-2.72-2.52-3.62-1.14-0.89-2.63-1.34-4.48-1.34-2.46 0-4.38 0.84-5.78 2.51s-2.09 3.99-2.09 6.94v4.84"
  "c0 2.95 0.7 5.27 2.09 6.94s3.32 2.51 5.78 2.51c1.91 0 3.46-0.49 4.66-1.48s2.08-2.25 2.66-3.8l4.14 2.5c-1.06 2."
  "3-2.55 4.1-4.46 5.39s-4.25 1.94-7.01 1.94z' fill='%23f9f5f2'/%3E%3Cpath d='m141.2 221.8v-4.18h4.32v-23.38h-4.3"
  "2v-4.19h13.83v4.19h-4.37v23.38h4.37v4.18z' fill='%23f9f5f2'/%3E%3Cpath d='m172 194.6v27.2h-5.14v-27.2h-9.46v-4"
  ".55h24.06v4.55z' fill='%23f9f5f2'/%3E%3Cpath d='m194.2 221.8v-12.51l-10.92-19.24h5.87l7.73 14.15h0.14l7.69-14."
  "15h5.64l-11.01 19.15v12.6z' fill='%23f9f5f2'/%3E%3C/svg%3E";

// The ink band with both marks. Same markup on the portal and the status page.
String headerBand() {
  String h = "<div class='top'><img class='flb' alt='Fab Lab Bali' src=\"";
  h += FPSTR(LOGO_FLB);
  h += "\"><img class='fc' alt='Fab City' src=\"";
  h += FPSTR(LOGO_FC);
  h += "\"></div>";
  return h;
}

// Portal header: band + the node's id chip (the AP name the phone just joined).
String portalHeader() {
  return headerBand() + "<span class='id'>" + apName() + "</span>";
}

String footerLine() {
  return String("<div class='foot'>Making Sense Bali · makingsense.fablabbali.com · firmware ") + FW_VERSION + "</div>";
}

// ============================================================================
// CONFIG PORTAL (WiFiManager + NVS)
// ============================================================================

// Pure read — prefs is opened once in setup().
void loadIdentity() {
  scToken    = sanitizeToken(prefs.getString("token", ""));
  nodeName   = prefs.getString("name", "");
  nodeSite   = prefs.getString("site", "");
  nodeHeight = prefs.getString("height", "");
  nodeIndoor = prefs.getBool("indoor", false);
  brokerHost = prefs.getString("mhost", DEFAULT_MQTT_HOST);
  brokerHost.trim();
  if (brokerHost.length() == 0) brokerHost = DEFAULT_MQTT_HOST;
  brokerPort = (uint16_t)prefs.getUShort("mport", DEFAULT_MQTT_PORT);
  if (brokerPort == 0) brokerPort = DEFAULT_MQTT_PORT;
  brokerUser = prefs.getString("muser", "");
  brokerPass = prefs.getString("mpass", "");
  scFallback = prefs.getBool("scfb", true);
  otaEnabled = prefs.getBool("ota", true);
}

// Smart Citizen's broker, or somebody's own (a PLANETAI node, typically)?
bool localBrokerHost(const String &host) {
  return !host.equalsIgnoreCase(DEFAULT_MQTT_HOST);
}

bool localBroker() {
  return localBrokerHost(brokerHost);
}

String smartCitizenLabel() {
  return String(DEFAULT_MQTT_HOST) + ":" + String(DEFAULT_MQTT_PORT) + " (Smart Citizen)";
}

// What is configured, in the order it is tried.
String brokerLabel() {
  if (!localBroker()) return smartCitizenLabel();
  String s = brokerHost + ":" + String(brokerPort) + " (PLANETAI node)";
  if (scFallback) s += ", then " + smartCitizenLabel();
  return s;
}

// Where the readings go right now.
String destinationNow() {
  if (!localBroker()) return smartCitizenLabel();
  if (fallbackSince) return smartCitizenLabel() + ", the PLANETAI node is not answering";
  return brokerHost + ":" + String(brokerPort) + " (PLANETAI node)";
}

void setupConfig(bool forcePortal) {
  loadIdentity();

  WiFiManager wm;
  wm.setTitle("Node setup");
  // WiFiManager keeps the pointers, so the strings must outlive this call.
  static String head = FPSTR(THEME_CSS);
  static String header;  header = portalHeader();
  static String footer;  footer = footerLine();
  wm.setCustomHeadElement(head.c_str());
  wm.setCustomBodyHeader(header.c_str());
  wm.setCustomBodyFooter(footer.c_str());
  // A participant needs one thing here. Info / erase / update stay reachable
  // by URL for whoever knows them, but are not offered as buttons.
  std::vector<const char*> menu = {"wifi"};
  wm.setMenu(menu);
  wm.setConfigPortalTimeout(PORTAL_TIMEOUT_S);
  wm.setConnectTimeout(20);

  WiFiManagerParameter hdrToken(
      "<p class='sec'>Device token</p>"
      "<p class='hint'>The token your platform gives this device — on Smart "
      "Citizen it is on the device page. It identifies the node on the wire; "
      "nothing publishes without it. If you scanned the QR from "
      "makingsense.fablabbali.com/setup.html it is already filled in. For a node "
      "that only talks to a PLANETAI node on your own network, any six "
      "characters will do.</p>");
  WiFiManagerParameter tokenParam("sctoken", "Token", scToken.c_str(), TOKEN_FIELD_LEN);

  WiFiManagerParameter hdrBroker(
      "<p class='sec'>Where it publishes</p>"
      "<p class='hint'><b>First, a PLANETAI node:</b> on the machine running the "
      "node, open a terminal and run <b>planetai broker</b>. It prints the four "
      "values below: the host (its name ending in .local, or its address), port "
      "1883, user <b>planetai</b> and a password. Type them in. The node keeps "
      "every reading and can pass it on to Smart Citizen for you.</p>"
      "<p class='hint'><b>Then Smart Citizen:</b> with the box below ticked, if the "
      "PLANETAI node stops answering this sensor publishes to Smart Citizen "
      "directly, and goes back to the node when it answers again. Leave the host "
      "blank and it publishes to Smart Citizen only.</p>");
  // The fields describe the PLANETAI node; Smart Citizen needs none of them.
  String hostStr = localBroker() ? brokerHost : String("");
  String portStr = String(localBroker() ? brokerPort : 1883);
  String userStr = localBroker() ? brokerUser : String("planetai");
  WiFiManagerParameter hostParam("mhost", "PLANETAI node host (blank = Smart Citizen only)", hostStr.c_str(), HOST_FIELD_LEN);
  WiFiManagerParameter portParam("mport", "Port", portStr.c_str(), 6);
  WiFiManagerParameter userParam("muser", "User", userStr.c_str(), USER_FIELD_LEN);
  WiFiManagerParameter passParam("mpass", "Password", brokerPass.c_str(), PASS_FIELD_LEN, "type='password'");
  WiFiManagerParameter fallbackParam("scfb", "If the PLANETAI node stops answering, publish to Smart Citizen", "T", 2,
                                     scFallback ? "type='checkbox' checked" : "type='checkbox'", WFM_LABEL_AFTER);

  WiFiManagerParameter hdrLocal(
      "<p class='sec'>This node</p>"
      "<p class='hint'>For finding and "
      "checking the node on your own network. <b>These are never published to "
      "an online platform</b>: a PLANETAI node on your network receives them so "
      "it knows where the sensor hangs. Set the public name and location on your "
      "platform's device page.</p>");
  WiFiManagerParameter nameParam("nodename", "Name (e.g. Balai Banjar Serangan)", nodeName.c_str(), NAME_FIELD_LEN);
  WiFiManagerParameter siteParam("nodesite", "Where it hangs (desa, landmark)", nodeSite.c_str(), SITE_FIELD_LEN);
  WiFiManagerParameter heightParam("nodehgt", "Height above ground, metres", nodeHeight.c_str(), 6);
  // A checkbox: the browser sends "T" when ticked and nothing at all when not, so getValue() is "" for off.
  WiFiManagerParameter indoorParam("indoor", "This node hangs indoors (a room, not the street)", "T", 2,
                                   nodeIndoor ? "type='checkbox' checked" : "type='checkbox'", WFM_LABEL_AFTER);

  WiFiManagerParameter hdrUpdates(
      "<p class='sec'>Updates</p>"
      "<p class='hint'>Once a day the sensor checks for a newer Making Sense Bali "
      "firmware and installs it. If a new firmware cannot get back online, the "
      "sensor goes back to the one it had.</p>");
  WiFiManagerParameter otaParam("ota", "Keep the firmware up to date", "T", 2,
                                otaEnabled ? "type='checkbox' checked" : "type='checkbox'", WFM_LABEL_AFTER);

  wm.addParameter(&hdrToken);
  wm.addParameter(&tokenParam);
  wm.addParameter(&hdrBroker);
  wm.addParameter(&hostParam);
  wm.addParameter(&portParam);
  wm.addParameter(&userParam);
  wm.addParameter(&passParam);
  wm.addParameter(&fallbackParam);
  wm.addParameter(&hdrLocal);
  wm.addParameter(&nameParam);
  wm.addParameter(&siteParam);
  wm.addParameter(&heightParam);
  wm.addParameter(&indoorParam);
  wm.addParameter(&hdrUpdates);
  wm.addParameter(&otaParam);

  // Persist as soon as Save is pressed — even if the WiFi join then fails,
  // the values survive for the next attempt.
  wm.setSaveParamsCallback([&]() {
    String t = sanitizeToken(tokenParam.getValue());
    if (t.length() > 0) { prefs.putString("token", t); scToken = t; }

    String n = String(nameParam.getValue());   n.trim();
    String s = String(siteParam.getValue());   s.trim();
    String h = String(heightParam.getValue()); h.trim();
    prefs.putString("name", n);   nodeName   = n;
    prefs.putString("site", s);   nodeSite   = s;
    prefs.putString("height", h); nodeHeight = h;
    bool indoor = String(indoorParam.getValue()).length() > 0;
    prefs.putBool("indoor", indoor); nodeIndoor = indoor;

    String host = String(hostParam.getValue()); host.trim();
    if (host.length() == 0) host = DEFAULT_MQTT_HOST;
    int port = String(portParam.getValue()).toInt();
    if (port <= 0 || port > 65535) port = localBrokerHost(host) ? 1883 : DEFAULT_MQTT_PORT;
    String user = String(userParam.getValue()); user.trim();
    String pass = String(passParam.getValue());
    prefs.putString("mhost", host);           brokerHost = host;
    prefs.putUShort("mport", (uint16_t)port); brokerPort = (uint16_t)port;
    prefs.putString("muser", user);           brokerUser = user;
    prefs.putString("mpass", pass);           brokerPass = pass;
    bool fb = String(fallbackParam.getValue()).length() > 0;
    bool ota = String(otaParam.getValue()).length() > 0;
    prefs.putBool("scfb", fb);  scFallback = fb;
    prefs.putBool("ota", ota);  otaEnabled = ota;

    Serial.printf("[config] saved — token %s · name '%s' · site '%s' · height '%s' · %s · broker %s:%d user '%s'"
                  " · Smart Citizen fallback %s · updates %s\n",
                  t.length() ? "yes" : "NO", n.c_str(), s.c_str(), h.c_str(), indoor ? "indoor" : "outdoor",
                  host.c_str(), port, user.c_str(), fb ? "on" : "off", ota ? "on" : "off");
  });

  // QR hand-off. makingsense.fablabbali.com/setup.html registers the device on
  // Smart Citizen and shows a QR for http://192.168.4.1/t?token=xxxxxx. A phone
  // joined to this AP scans it: the token is saved and prefilled, and the phone
  // goes on to the WiFi page, so nobody copies six characters by hand.
  // Registered through setWebServerCallback because WiFiManager creates its
  // WebServer only when the portal starts; wm.server is public.
  wm.setWebServerCallback([&]() {
    wm.server->on("/t", [&]() {
      String t = sanitizeToken(wm.server->arg("token"));
      if (t.length() == 0 || t.length() > TOKEN_FIELD_LEN) {
        wm.server->send(400, "text/plain", "missing or malformed token");
        return;
      }
      prefs.putString("token", t);
      scToken = t;
      tokenParam.setValue(t.c_str(), TOKEN_FIELD_LEN);   // prefill the portal field
      Serial.printf("[config] token saved via /t (%s)\n", maskedToken().c_str());
      // A PLANETAI node's QR also carries its broker: host, and optionally port, user, pass.
      String nodeLine;
      String host = wm.server->arg("host"); host.trim();
      if (host.length() && host.length() <= (unsigned)HOST_FIELD_LEN) {
        int port = wm.server->arg("port").toInt();
        if (port <= 0 || port > 65535) port = 1883;
        String user = wm.server->arg("user"); user.trim();
        String pass = wm.server->arg("pass");
        if (user.length() > (unsigned)USER_FIELD_LEN) user = "";
        if (pass.length() > (unsigned)PASS_FIELD_LEN) pass = "";
        prefs.putString("mhost", host);           brokerHost = host;
        prefs.putUShort("mport", (uint16_t)port); brokerPort = (uint16_t)port;
        prefs.putString("muser", user);           brokerUser = user;
        prefs.putString("mpass", pass);           brokerPass = pass;
        String portStr = String(port);
        hostParam.setValue(host.c_str(), HOST_FIELD_LEN);
        portParam.setValue(portStr.c_str(), 6);
        userParam.setValue(user.c_str(), USER_FIELD_LEN);
        passParam.setValue(pass.c_str(), PASS_FIELD_LEN);
        Serial.printf("[config] PLANETAI node saved via /t: %s:%d user '%s'\n", host.c_str(), port, user.c_str());
        nodeLine = " to the PLANETAI node <span class='n'>" + htmlEscape(host) + "</span>";
      }
      wm.server->send(200, "text/html; charset=utf-8",
        "<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>" +
        String(FPSTR(THEME_CSS)) + "<body><div class='wrap'>" + headerBand() +
        "<h1>Token saved</h1><p class='hint'>This node will publish as <span class='n'>" + maskedToken() +
        "</span>" + nodeLine + ". Now give it your WiFi.</p><form action='/wifi' method='get'><button>Choose WiFi &rarr;</button></form>" +
        footerLine() + "</div></body>");
    });
  });

  bool ok;
  if (forcePortal) {
    Serial.println("[config] portal opened on demand");
    ok = wm.startConfigPortal(apName().c_str(), PORTAL_PASSWORD);
  } else {
    ok = wm.autoConnect(apName().c_str(), PORTAL_PASSWORD);
  }

  if (!ok) {
    Serial.println("[config] portal timed out / join failed — rebooting to retry saved WiFi");
    delay(1000);
    ESP.restart();
  }

  loadIdentity();
  Serial.printf("[wifi] connected — IP %s · RSSI %d dBm\n",
                WiFi.localIP().toString().c_str(), WiFi.RSSI());
  if (scToken.length() == 0) {
    Serial.println("[config] *** NO TOKEN SAVED — node will read sensors but");
    Serial.println("[config] *** publish NOTHING. Reopen setup to add one.");
  } else {
    Serial.printf("[config] token: %s · name: %s\n", scToken.c_str(),
                  nodeName.length() ? nodeName.c_str() : "(unnamed)");
  }
  Serial.printf("[config] publishes to %s\n", brokerLabel().c_str());
}

bool bootButtonHeld() {
  pinMode(BOOT_BTN_PIN, INPUT_PULLUP);
  delay(50);
  if (digitalRead(BOOT_BTN_PIN) != LOW) return false;
  uint32_t start = millis();
  while (millis() - start < 1500) {
    if (digitalRead(BOOT_BTN_PIN) != LOW) return false;
    delay(10);
  }
  return true;
}

// ============================================================================
// LOCAL STATUS PAGE
// ============================================================================
// Served on the node's LAN address, and at http://<mdnsHost()>.local.
// Exists so a node can be checked in the field with a phone, which is the
// difference between a workshop that needs one laptop per table and one that
// doesn't. Read-only except for the reconfigure button, and the token is
// masked because anyone on the same WiFi can load this.

String htmlEscape(const String &in) {
  String o;
  for (size_t i = 0; i < in.length(); i++) {
    char c = in[i];
    if      (c == '&')  o += "&amp;";
    else if (c == '<')  o += "&lt;";
    else if (c == '>')  o += "&gt;";
    else if (c == '"')  o += "&quot;";
    else if (c == '\'') o += "&#39;";
    else o += c;
  }
  return o;
}

String row(const String &k, const String &v, const char* cls = "") {
  return "<tr><th>" + htmlEscape(k) + "</th><td class='" + String(cls) + "'>" + v + "</td></tr>";
}

String fmt(float v, int dp, const char* unit) {
  if (isnan(v)) return "<span class='off'>—</span>";
  char b[24];
  snprintf(b, sizeof(b), "%.*f", dp, v);
  return "<span class='n'>" + String(b) + "</span> " + unit;
}

// State by weight, not hue: online is set in weight, "not fitted" is faded
// (a normal state), and only a sensor that was there and stopped answering
// gets the dashed edge.
String sensorStateHtml(bool online, bool lost) {
  if (online) return "<span class='on'>online</span>";
  if (lost)   return "<span class='stop'>stopped answering — check the cable</span>";
  return "<span class='off'>not fitted</span>";
}

void handleStatus() {
  String title = nodeName.length() ? nodeName : apName();
  String h;
  h.reserve(16384);
  h += "<!doctype html><html lang='en'><head><meta charset='utf-8'>";
  h += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
  h += "<title>" + htmlEscape(title) + " — Making Sense Bali</title>";
  h += FPSTR(THEME_CSS);
  h += "</head><body><div class='wrap'>";
  h += headerBand();
  h += "<span class='id'>" + htmlEscape(mdnsHost()) + ".local</span>";
  h += "<h1>" + htmlEscape(title) + "</h1>";
  h += "<h3>" + htmlEscape(nodeSite.length() ? nodeSite : "site not set");
  if (nodeHeight.length()) h += " · " + htmlEscape(nodeHeight) + " m above ground";
  h += nodeIndoor ? " · indoors" : " · outdoors";
  h += "</h3>";

  // Only sensors that are fitted get rows. A node without a BME680 shows no
  // empty temperature row; a node with two PM sensors labels which is which.
  const char* UG = "&micro;g/m&sup3;";
  String senLabel = sen5xModel[0] ? String(sen5xModel) : String("SEN5x");
  // Every figure carries its time and how we know it: these are live, from
  // the last read cycle, at the node's local clock.
  h += "<p class='sec'>Latest reading · live · <span class='n'>" + htmlEscape(lastPublishAt) + "</span></p><table>";
  if (g_hmOnline || g_hmLost) {
    String tag = (g_senOnline || g_senLost) ? " (HM3301)" : "";
    h += row("PM1"   + tag, lastHmOk ? "<span class='n'>" + String(lastPM1)  + "</span> " + UG : "<span class='off'>—</span>");
    h += row("PM2.5" + tag, lastHmOk ? "<span class='n'>" + String(lastPM25) + "</span> " + UG : "<span class='off'>—</span>");
    h += row("PM10"  + tag, lastHmOk ? "<span class='n'>" + String(lastPM10) + "</span> " + UG : "<span class='off'>—</span>");
  }
  if (g_senOnline || g_senLost) {
    String tag = (g_hmOnline || g_hmLost) ? " (" + senLabel + ")" : "";
    h += row("PM1"   + tag, fmt(lastSenOk ? lastSen.pm1  : NAN, 1, UG));
    h += row("PM2.5" + tag, fmt(lastSenOk ? lastSen.pm25 : NAN, 1, UG));
    h += row("PM4"   + tag, fmt(lastSenOk ? lastSen.pm4  : NAN, 1, UG));
    h += row("PM10"  + tag, fmt(lastSenOk ? lastSen.pm10 : NAN, 1, UG));
    if (!isnan(lastSen.tempC)) h += row("Temperature (" + senLabel + ")", fmt(lastSen.tempC, 2, "&deg;C"));
    if (!isnan(lastSen.rh))    h += row("Humidity (" + senLabel + ")",    fmt(lastSen.rh, 2, "%"));
    if (!isnan(lastSen.voc))   h += row("VOC index", fmt(lastSen.voc, 0, ""));
    if (!isnan(lastSen.nox))   h += row("NOx index", fmt(lastSen.nox, 0, ""));
  }
  if (g_pmsOnline || g_pmsLost) {
    const char* pmsName = pmsIsT ? "PMS5003T" : "PMS5003";
    String tag = (g_hmOnline || g_hmLost || g_senOnline || g_senLost) ? " (" + String(pmsName) + ")" : "";
    if (g_pmsOnline && millis() - pmsSince < 30000) tag += " · warming up, not published yet";
    h += row("PM1"   + tag, fmt(lastPmsOk ? lastPms.pm1  : NAN, 0, UG));
    h += row("PM2.5" + tag, fmt(lastPmsOk ? lastPms.pm25 : NAN, 0, UG));
    h += row("PM10"  + tag, fmt(lastPmsOk ? lastPms.pm10 : NAN, 0, UG));
    if (pmsIsT) {
      h += row("Temperature (" + String(pmsName) + ")", fmt(lastPmsOk ? lastPms.tempC : NAN, 1, "&deg;C"));
      h += row("Humidity (" + String(pmsName) + ")",    fmt(lastPmsOk ? lastPms.rh : NAN, 1, "%"));
    }
  }
  if (g_scdOnline || g_scdLost) {
    h += row("CO&#8322;", fmt(lastScdOk ? lastScd.co2 : NAN, 0, "ppm"));
    h += row("Temperature (SCD4x)", fmt(lastScdOk ? lastScd.tempC : NAN, 2, "&deg;C"));
    h += row("Humidity (SCD4x)",    fmt(lastScdOk ? lastScd.rh : NAN, 2, "%"));
  }
  if (g_shtOnline || g_shtLost) {
    h += row("Temperature (SHT4x)", fmt(lastShtOk ? lastShtT : NAN, 2, "&deg;C"));
    h += row("Humidity (SHT4x)",    fmt(lastShtOk ? lastShtRH : NAN, 2, "%"));
  }
  if (g_bmeOnline || g_bmeLost) {
    String tag = (g_senOnline || g_senLost || g_shtOnline || g_scdOnline) ? " (BME680)" : "";
    h += row("Temperature" + tag, fmt(lastT, 2, "&deg;C"));
    h += row("Humidity" + tag,    fmt(lastRH, 2, "%"));
    h += row("Pressure",    fmt(lastP, 3, "kPa"));
    h += row("Gas",         fmt(lastGas, 0, "&Omega;"));
    h += row("IAQ (approx)", fmt(lastIAQ, 0, ""));
  }
  h += "</table>";

  h += "<p class='sec'>Health</p><table>";
  h += row("HM3301", sensorStateHtml(g_hmOnline,  g_hmLost));
  h += row(senLabel, sensorStateHtml(g_senOnline, g_senLost));
  h += row("BME680", sensorStateHtml(g_bmeOnline, g_bmeLost));
  h += row(pmsIsT ? "PMS5003T" : "PMS5003", sensorStateHtml(g_pmsOnline, g_pmsLost));
  h += row("SHT4x",  sensorStateHtml(g_shtOnline, g_shtLost));
  h += row("SCD4x",  sensorStateHtml(g_scdOnline, g_scdLost));
  h += row("Smart Citizen token", scToken.length() ? "<span class='n on'>" + maskedToken() + "</span>"
                                                   : "<span class='stop'>NOT SET — nothing is published</span>");
  h += row("Publishes to", "<span class='n'>" + htmlEscape(brokerLabel()) + "</span>");
  if (localBroker()) h += row("Right now", "<span class='n'>" + htmlEscape(destinationNow()) + "</span>");
  h += row("MQTT", mqtt.connected() ? "<span class='on'>connected</span>" : "<span class='stop'>disconnected</span>");
  h += row("Last publish", String(lastPublishOk ? "<span class='mk'></span><span class='on'>left the node</span> at "
                                                 : "<span class='stop'>failed</span> at ") + "<span class='n'>" + htmlEscape(lastPublishAt) + "</span>");
  h += row("Published / failed", "<span class='n'>" + String(publishCount) + " / " + String(publishFailCount) + "</span>");
  h += "</table>";

  h += "<p class='sec'>Connection</p><table>";
  h += row("WiFi", htmlEscape(WiFi.SSID()));
  h += row("Signal", "<span class='n'>" + String(WiFi.RSSI()) + "</span> dBm");
  h += row("IP", "<span class='n'>" + WiFi.localIP().toString() + "</span>");
  h += row("Also reachable at", "<span class='n'>http://" + mdnsHost() + ".local</span>");
  h += row("I2C pins", "<span class='n'>SDA " + String(I2C_SDA_PIN) + " · SCL " + String(I2C_SCL_PIN) + "</span>");
  h += row("Uptime", "<span class='n'>" + uptimeStr() + "</span>");
  h += row("Firmware", "<span class='n'>" + htmlEscape(FW_BUILD[0] ? String(FW_BUILD) : String(FW_VERSION) + " (built by hand)") + "</span>");
  h += row("Updates", htmlEscape(otaEnabled ? otaStatus : String("off")));
  h += "</table>";

  h += "<form method='POST' action='/setup' onsubmit=\"return confirm('Reboot into the setup portal? The node stops measuring until setup finishes.')\">";
  h += "<button type='submit'>Reopen setup</button></form>";

  if (onNode) {
    h += "<p class='note'>Name, site, height and indoors are sent to the local node "
         "with every connection, so it knows what this sensor is and where it hangs. "
         "Whether the node also passes readings on to smartcitizen.me is set on the node. "
         "Temperature and humidity are published raw — they have not been checked "
         "against a reference station, so expect them to read high in an enclosure.</p>";
  } else {
    h += "<p class='note'>Name and site are stored on this node only. The display "
         "name and location on smartcitizen.me are set there, on the device page. "
         "Temperature and humidity are published raw — they have not been checked "
         "against a reference station, so expect them to read high in an enclosure.</p>";
  }
  h += footerLine();
  h += "</div></body></html>";

  status.send(200, "text/html; charset=utf-8", h);
}

void handleSetupRequest() {
  status.send(200, "text/html; charset=utf-8",
    "<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>" +
    String(FPSTR(THEME_CSS)) + "<body><div class='wrap'>" + headerBand() +
    "<h1>Rebooting into setup</h1><p class='hint'>Join the WiFi network <span class='id'>" + apName() +
    "</span> (password <span class='n'>" + String(PORTAL_PASSWORD) + "</span>) in about 15 seconds.</p></div></body>");
  reopenPortalRequested = true;
}

void startStatusServer() {
  String host = mdnsHost();
  if (MDNS.begin(host.c_str())) {
    MDNS.addService("http", "tcp", 80);
    Serial.printf("[mdns] http://%s.local\n", host.c_str());
  } else {
    Serial.println("[mdns] failed to start — use the IP address");
  }
  status.on("/", HTTP_GET, handleStatus);
  status.on("/setup", HTTP_POST, handleSetupRequest);
  status.onNotFound([]() { status.sendHeader("Location", "/"); status.send(302, "text/plain", ""); });
  status.begin();
  Serial.printf("[http] status page on http://%s/\n", WiFi.localIP().toString().c_str());
}

// ============================================================================
// WIFI (runtime) + NTP
// ============================================================================

void ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  uint32_t now = millis();
  if (now - lastWifiRetry < WIFI_RETRY_INTERVAL_MS) return;
  lastWifiRetry = now;
  Serial.println("[wifi] disconnected — reconnecting");
  WiFi.reconnect();
}

void syncTime() {
  configTime(8 * 3600, 0, "pool.ntp.org", "time.google.com");
  Serial.print("[ntp] syncing");
  time_t now = time(nullptr);
  uint32_t start = millis();
  while (now < 1700000000 && (millis() - start) < 15000) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println();
  if (now < 1700000000) {
    Serial.println("[ntp] failed — recorded_at will be wrong, the platform may drop readings");
  } else {
    Serial.printf("[ntp] synced — unix %ld\n", (long)now);
  }
}

String iso8601UTC() {
  time_t now = time(nullptr);
  struct tm tm_utc;
  gmtime_r(&now, &tm_utc);
  char buf[32];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &tm_utc);
  return String(buf);
}

String localClock() {
  time_t now = time(nullptr);
  struct tm tm_loc;
  localtime_r(&now, &tm_loc);
  char buf[32];
  strftime(buf, sizeof(buf), "%H:%M:%S", &tm_loc);
  return String(buf);
}

// ============================================================================
// MQTT
// ============================================================================

// Once per connection to a local node: who this device is and where it hangs. Retained, so the node reads it
// the moment it subscribes, even after a restart on its side. Never sent to Smart Citizen: the point of v4 is
// that the Smart Citizen path stays exactly what v3 sent.
bool publishMeta() {
  if (!onNode || !mqtt.connected()) return false;
  JsonDocument doc;
  doc["name"]     = nodeName;
  doc["site"]     = nodeSite;
  if (nodeHeight.length()) doc["height_m"] = nodeHeight.toFloat();
  doc["indoor"]   = nodeIndoor;
  // `hardware` keeps v4's two values for the combinations v4 could build, so
  // a PLANETAI node keyed on them sees no change; `sensors` lists what is fitted.
  if (g_senOnline) doc["hardware"] = g_hmOnline ? "msb-diy-node-hm3301-sen5x" : "msb-diy-node-sen5x";
  else             doc["hardware"] = g_hmOnline ? "msb-diy-node-plus" : "msb-diy-node-basic";
  JsonArray fitted = doc["sensors"].to<JsonArray>();
  if (g_hmOnline)  fitted.add("hm3301");
  if (g_senOnline) fitted.add(sen5xModel[0] ? sen5xModel : "sen5x");
  if (g_bmeOnline) fitted.add("bme680");
  if (g_pmsOnline) fitted.add(pmsIsT ? "pms5003t" : "pms5003");
  if (g_shtOnline) fitted.add("sht4x");
  if (g_scdOnline) fitted.add("scd4x");
  doc["fw"]       = FW_VERSION;
  String json;
  serializeJson(doc, json);
  String topic = String("device/sck/") + scToken + "/meta";
  bool ok = mqtt.publish(topic.c_str(), json.c_str(), true);
  Serial.printf("[mqtt] meta %s: %s\n", ok ? "published" : "FAILED", json.c_str());
  return ok;
}

// Where the next connection goes: the PLANETAI node while it answers; Smart
// Citizen when no node is set, or when the node has missed
// NODE_FAILS_BEFORE_FALLBACK connections in a row and the fallback is on. From
// Smart Citizen the node is tried again every NODE_RETRY_MS (see loop()).
// The topic and the bytes are the same on both, so a reading published during
// a fallback is a reading Smart Citizen would have had from the node anyway.
void connectMQTT() {
  if (mqtt.connected()) return;
  if (WiFi.status() != WL_CONNECTED) return;
  if (scToken.length() == 0) return;
  uint32_t now = millis();
  if (lastMqttTry && now - lastMqttTry < MQTT_RETRY_MS) return;
  lastMqttTry = now;

  bool toNode = localBroker() && (!fallbackSince || now - fallbackSince >= NODE_RETRY_MS);
  const char* host = toNode ? brokerHost.c_str() : DEFAULT_MQTT_HOST;
  uint16_t    port = toNode ? brokerPort : DEFAULT_MQTT_PORT;

  // 8883 is TLS (Smart Citizen, or a node that terminates TLS itself); anything else is plain MQTT on the LAN.
  if (port == 8883) {
    tlsNet.setInsecure();   // see v2 notes — fine for a workshop kit, not for policy data. A PLANETAI node
                            // forwarding to Smart Citizen verifies the platform's certificate on this device's behalf.
    mqtt.setClient(tlsNet);
  } else {
    mqtt.setClient(plainNet);
  }
  mqtt.setServer(host, port);
  mqtt.setBufferSize(1024);   // HM3301 + SEN55 + BME680 + PMS5003T + SHT4x + SCD4x is ~27 channels

  Serial.printf("[mqtt] connecting to %s:%u%s ", host, port, toNode ? " (PLANETAI node)" : " (Smart Citizen)");
  // Smart Citizen's way is token as username and no password; a node's broker has its own user and password.
  // The client id stays the token on both, so a node can tell devices apart in its broker log.
  bool withUser = toNode && brokerUser.length();
  bool ok = withUser
      ? mqtt.connect(scToken.c_str(), brokerUser.c_str(), brokerPass.c_str())
      : mqtt.connect(scToken.c_str(), scToken.c_str(), "");
  onNode = ok && toNode;
  if (ok) {
    Serial.println("ok");
    if (toNode) {
      if (fallbackSince) Serial.println("[mqtt] the PLANETAI node answers again, publishing there");
      nodeFails = 0;
      fallbackSince = 0;
      publishMeta();
    }
    return;
  }
  Serial.printf("failed (rc=%d) — will retry. rc=5 means %s\n", mqtt.state(),
                withUser ? "the broker refused the user/password" : "BAD TOKEN");
  if (!toNode) return;
  if (fallbackSince) { fallbackSince = now; return; }   // still down: another NODE_RETRY_MS on Smart Citizen
  if (++nodeFails >= NODE_FAILS_BEFORE_FALLBACK && scFallback) {
    Serial.printf("[mqtt] the PLANETAI node missed %u connections, publishing to Smart Citizen until it answers\n",
                  (unsigned)nodeFails);
    nodeFails = 0;
    fallbackSince = now;
    lastMqttTry = 0;   // straight on to Smart Citizen
  }
}

bool publishReadings(bool bmeOk, float tempC, float humRH, float pressureKPa,
                     float gasOhm, float iaq,
                     bool hmOk, uint16_t pm1, uint16_t pm25, uint16_t pm10,
                     bool senOk, const Sen5xReading &sen,
                     bool pmsOk, const PmsReading &pms,
                     bool shtOk, float shtT, float shtRH,
                     bool scdOk, const Scd4xReading &scd) {
  if (!mqtt.connected()) return false;

  JsonDocument doc;
  JsonArray data = doc["data"].to<JsonArray>();
  JsonObject reading = data.add<JsonObject>();
  reading["recorded_at"] = iso8601UTC();
  JsonArray sensors = reading["sensors"].to<JsonArray>();

  auto addSensor = [&](int id, float value) {
    if (id == 0) return;
    if (isnan(value) || isinf(value)) return;
    JsonObject s = sensors.add<JsonObject>();
    s["id"] = id;
    s["value"] = value;
  };

  if (bmeOk) {
    addSensor(SC_ID_TEMP,     tempC);
    addSensor(SC_ID_HUM,      humRH);
    addSensor(SC_ID_PRESSURE, pressureKPa);
    addSensor(SC_ID_GAS,      gasOhm);
    addSensor(SC_ID_IAQ,      iaq);
  }
  if (hmOk) {
    addSensor(SC_ID_PM1,  (float)pm1);
    addSensor(SC_ID_PM25, (float)pm25);
    addSensor(SC_ID_PM10, (float)pm10);
  }
  if (senOk) {
    // NAN channels (absent on this model, or not valid yet) are skipped by addSensor.
    addSensor(SC_ID_SEN_PM1,  sen.pm1);
    addSensor(SC_ID_SEN_PM25, sen.pm25);
    addSensor(SC_ID_SEN_PM4,  sen.pm4);
    addSensor(SC_ID_SEN_PM10, sen.pm10);
    addSensor(SC_ID_SEN_HUM,  sen.rh);
    addSensor(SC_ID_SEN_TEMP, sen.tempC);
    addSensor(SC_ID_SEN_VOC,  sen.voc);
    addSensor(SC_ID_SEN_NOX,  sen.nox);
  }
  if (pmsOk) {
    addSensor(SC_ID_PMS_PM1,  pms.pm1);
    addSensor(SC_ID_PMS_PM25, pms.pm25);
    addSensor(SC_ID_PMS_PM10, pms.pm10);
    addSensor(SC_ID_PMS_TEMP, pms.tempC);   // NAN unless it is a PMS5003T
    addSensor(SC_ID_PMS_HUM,  pms.rh);
  }
  if (shtOk) {
    addSensor(SC_ID_SHT_TEMP, shtT);
    addSensor(SC_ID_SHT_HUM,  shtRH);
  }
  if (scdOk) {
    addSensor(SC_ID_SCD_CO2,  scd.co2);     // NAN between the SCD4x's 5 s measurements
    addSensor(SC_ID_SCD_TEMP, scd.tempC);
    addSensor(SC_ID_SCD_HUM,  scd.rh);
  }

  if (sensors.size() == 0) {
    Serial.println("[mqtt] no valid readings this cycle — nothing published");
    return false;
  }

  String json;
  serializeJson(doc, json);
  String topic = String("device/sck/") + scToken + "/readings";

  bool ok = mqtt.publish(topic.c_str(), json.c_str(), false);
  if (ok) {
    Serial.printf("[mqtt] published (%u bytes): %s\n", json.length(), json.c_str());
  } else {
    Serial.println("[mqtt] publish failed");
  }
  return ok;
}

// ============================================================================
// SENSORS (unchanged from v1/v2)
// ============================================================================

float computeIAQ(float gasOhm, float humRH) {
  if (isnan(gasOhm) || isnan(humRH) || gasOhm <= 0.0f) return NAN;
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

  float goodness = gasScore + humScore;
  float iaq = (100.0f - goodness) * 5.0f;
  if (iaq < 0.0f)   iaq = 0.0f;
  if (iaq > 500.0f) iaq = 500.0f;
  return iaq;
}

bool readBME680(float &tempC, float &humRH, float &pressureKPa, float &gasOhm) {
  if (!bme.performReading()) return false;
  tempC       = bme.temperature;
  humRH       = bme.humidity;
  pressureKPa = bme.pressure / 1000.0f;
  gasOhm      = bme.gas_resistance;
  return !(isnan(tempC) || isnan(humRH));
}

bool hm3301_init() {
  Wire.beginTransmission(HM3301_I2C_ADDR);
  Wire.write(HM3301_SELECT_I2C_CMD);
  return Wire.endTransmission() == 0;
}

bool readHM3301(uint16_t &pm1, uint16_t &pm25, uint16_t &pm10) {
  uint8_t buf[29];
  size_t got = Wire.requestFrom(HM3301_I2C_ADDR, (uint8_t)29);
  if (got != 29) return false;
  for (int i = 0; i < 29; i++) {
    if (!Wire.available()) return false;
    buf[i] = Wire.read();
  }
  uint8_t sum = 0;
  for (int i = 0; i < 28; i++) sum += buf[i];
  if (sum != buf[28]) return false;
  pm1  = ((uint16_t)buf[10] << 8) | buf[11];
  pm25 = ((uint16_t)buf[12] << 8) | buf[13];
  pm10 = ((uint16_t)buf[14] << 8) | buf[15];
  return true;
}

// ============================================================================
// SEN5x — direct I2C
//
// Command words and delays from Sensirion's embedded-i2c-sen5x. Every 2 data
// bytes on the wire are followed by a CRC-8 (poly 0x31, init 0xFF), so an
// N-word read is 3N bytes. A frame with any bad CRC is discarded whole: a
// corrupted PM word looks exactly like a real spike.
// ============================================================================

constexpr uint16_t SEN5X_CMD_START_MEASUREMENT    = 0x0021;
constexpr uint16_t SEN5X_CMD_READ_MEASURED_VALUES = 0x03C4;  // 8 words
constexpr uint16_t SEN5X_CMD_GET_PRODUCT_NAME     = 0xD014;  // 16 words (32 chars)
constexpr uint16_t SEN5X_CMD_DEVICE_RESET         = 0xD304;

bool sensirionCmd(uint8_t addr, uint16_t cmd, uint16_t delayMs) {
  Wire.beginTransmission(addr);
  Wire.write((uint8_t)(cmd >> 8));
  Wire.write((uint8_t)(cmd & 0xFF));
  if (Wire.endTransmission() != 0) return false;
  if (delayMs) delay(delayMs);
  return true;
}

// Read `count` words, 3 bytes each on the wire. Any bad CRC discards the lot.
bool sensirionReadReply(uint8_t addr, uint16_t* out, size_t count) {
  const size_t wireBytes = count * 3;
  size_t got = Wire.requestFrom(addr, (uint8_t)wireBytes);
  if (got != wireBytes) return false;
  for (size_t i = 0; i < count; i++) {
    uint8_t buf[3];
    for (uint8_t b = 0; b < 3; b++) {
      if (!Wire.available()) return false;
      buf[b] = Wire.read();
    }
    if (sensirionCrc(buf, 2) != buf[2]) return false;
    out[i] = ((uint16_t)buf[0] << 8) | buf[1];
  }
  return true;
}

bool sensirionReadWords(uint8_t addr, uint16_t cmd, uint16_t* out, size_t count, uint16_t delayMs) {
  return sensirionCmd(addr, cmd, delayMs) && sensirionReadReply(addr, out, count);
}

// Sensirion's "no value" sentinels: 0xFFFF unsigned, 0x7FFF signed.
inline float sen5xScaleU(uint16_t raw, float div) { return raw == 0xFFFF ? NAN : (float)raw / div; }
inline float sen5xScaleS(uint16_t raw, float div) {
  int16_t s = (int16_t)raw;
  return s == 0x7FFF ? NAN : (float)s / div;
}

// Decode the 8 words of READ_MEASURED_VALUES. Split out so it can be tested
// off the board.
void sen5xDecode(const uint16_t v[8], Sen5xReading &r) {
  r.pm1   = sen5xScaleU(v[0], 10.0f);
  r.pm25  = sen5xScaleU(v[1], 10.0f);
  r.pm4   = sen5xScaleU(v[2], 10.0f);
  r.pm10  = sen5xScaleU(v[3], 10.0f);
  r.rh    = sen5xScaleS(v[4], 100.0f);
  r.tempC = sen5xScaleS(v[5], 200.0f);
  r.voc   = sen5xScaleS(v[6], 10.0f);
  r.nox   = sen5xScaleS(v[7], 10.0f);
}

bool sen5xReadModel() {
  uint16_t w[16];
  if (!sensirionReadWords(SEN5X_ADDR, SEN5X_CMD_GET_PRODUCT_NAME, w, 16, 50)) return false;
  size_t n = 0;
  for (size_t i = 0; i < 16 && n < sizeof(sen5xModel) - 2; i++) {
    char hi = (char)(w[i] >> 8), lo = (char)(w[i] & 0xFF);
    if (!hi) break;
    sen5xModel[n++] = hi;
    if (!lo) break;
    sen5xModel[n++] = lo;
  }
  sen5xModel[n] = '\0';
  return n > 0;
}

// Reset first: if only the ESP32 rebooted, the SEN5x is still in measurement
// mode and would refuse START. Reset puts it in idle whatever state it was in.
bool sen5xBegin() {
  sensirionCmd(SEN5X_ADDR, SEN5X_CMD_DEVICE_RESET, 120);   // result ignored on purpose
  if (!sen5xReadModel()) return false;
  return sensirionCmd(SEN5X_ADDR, SEN5X_CMD_START_MEASUREMENT, 50);
}

bool readSEN5x(Sen5xReading &r) {
  uint16_t v[8];
  if (!sensirionReadWords(SEN5X_ADDR, SEN5X_CMD_READ_MEASURED_VALUES, v, 8, 20)) return false;
  sen5xDecode(v, r);
  // Right after START the PM words are 0xFFFF for about a second. That is
  // "not ready", not a failure — return true with NANs, publish nothing for it.
  return true;
}

// ============================================================================
// SHT4x — direct I2C. One-byte commands, two CRC'd words back (Sensirion SHT4x
// datasheet). 0x89 reads the serial number: an SHT3x on the same address does
// not answer a one-byte command, so this is also how an SHT4x is told apart.
// ============================================================================

constexpr uint8_t SHT4X_CMD_MEASURE_HIGH = 0xFD;   // high repeatability, 10 ms
constexpr uint8_t SHT4X_CMD_READ_SERIAL  = 0x89;

bool sht4xCommand(uint8_t cmd, uint16_t delayMs, uint16_t out[2]) {
  Wire.beginTransmission(SHT4X_ADDR);
  Wire.write(cmd);
  if (Wire.endTransmission() != 0) return false;
  delay(delayMs);
  return sensirionReadReply(SHT4X_ADDR, out, 2);
}

bool sht4xBegin() {
  uint16_t serial[2];
  return sht4xCommand(SHT4X_CMD_READ_SERIAL, 2, serial);
}

bool readSHT4x(float &tempC, float &rh) {
  uint16_t w[2];
  if (!sht4xCommand(SHT4X_CMD_MEASURE_HIGH, 10, w)) return false;
  sht4xDecode(w, tempC, rh);
  return true;
}

// ============================================================================
// SCD4x — direct I2C (Sensirion SCD4x datasheet). Periodic mode: a new CO2, T
// and RH every 5 s. Self-calibration stays on, as shipped: it assumes the
// sensor sees outdoor air (~400 ppm) at least once a week. A room that never
// airs out will drift; that is the sensor's limit, not something to hide here.
// ============================================================================

constexpr uint16_t SCD4X_CMD_START_PERIODIC   = 0x21B1;
constexpr uint16_t SCD4X_CMD_STOP_PERIODIC    = 0x3F86;   // 500 ms
constexpr uint16_t SCD4X_CMD_GET_SERIAL       = 0x3682;   // 3 words
constexpr uint16_t SCD4X_CMD_DATA_READY       = 0xE4B8;   // 1 word
constexpr uint16_t SCD4X_CMD_READ_MEASUREMENT = 0xEC05;   // 3 words

// Stop first: if only the ESP32 rebooted, the SCD4x is still measuring and
// would ignore every command but stop.
bool scd4xBegin() {
  sensirionCmd(SCD4X_ADDR, SCD4X_CMD_STOP_PERIODIC, 500);   // result ignored on purpose
  uint16_t serial[3];
  if (!sensirionReadWords(SCD4X_ADDR, SCD4X_CMD_GET_SERIAL, serial, 3, 1)) return false;
  return sensirionCmd(SCD4X_ADDR, SCD4X_CMD_START_PERIODIC, 0);
}

bool readSCD4x(Scd4xReading &r) {
  uint16_t ready;
  if (!sensirionReadWords(SCD4X_ADDR, SCD4X_CMD_DATA_READY, &ready, 1, 1)) return false;
  if ((ready & 0x07FF) == 0) return true;   // between measurements: NANs, not a failure
  uint16_t w[3];
  if (!sensirionReadWords(SCD4X_ADDR, SCD4X_CMD_READ_MEASUREMENT, w, 3, 1)) return false;
  scd4xDecode(w, r);
  return true;
}

// ============================================================================
// PLANTOWER PMS5003 / PMS5003T — UART, listen only
//
// The sensor streams a 32-byte frame about once a second at 9600 8N1 from the
// moment it has power: 0x42 0x4D, frame length 28, 13 big-endian words, then
// the 16-bit sum of bytes 0..29. Nothing has to be sent to it, so the node
// opens RX on PMS_RX_PIN and attaches no TX: a board with something else on
// that pin is never driven. A Plantower is fitted once a valid frame arrives.
//
// PMS5003 or PMS5003T: same frame; the T puts its temperature and humidity
// (x10) in the words that carry the 5 um and 10 um counts on the plain one.
// Those counts are cumulative ("particles beyond X um"), so on a PMS5003 they
// never grow with size. A frame where they do is a PMS5003T, and that is
// sticky. Until such a frame shows up nothing is published from those two
// words, so a T taken for a plain PMS5003 loses a few minutes of T/RH and
// never publishes a count as a temperature.
// ============================================================================

constexpr uint32_t PMS_WAIT_MS   = 3000;    // a frame every ~1 s, every ~2.3 s in clean air
constexpr uint32_t PMS_WARMUP_MS = 30000;   // Plantower: readings settle 30 s after the fan starts

// Drain what arrived since last time and keep the newest valid frame. With no
// valid frame buffered, wait up to waitMs for one.
bool pmsReadFrame(uint8_t out[PMS_FRAME_LEN], uint32_t waitMs) {
  uint8_t f[PMS_FRAME_LEN];
  uint8_t idx = 0;
  bool got = false;
  uint32_t start = millis();
  while (true) {
    if (!Serial1.available()) {
      if (got || millis() - start >= waitMs) break;
      delay(5);
      continue;
    }
    uint8_t b = Serial1.read();
    if (idx == 0 && b != 0x42) continue;
    if (idx == 1 && b != 0x4D) { idx = (b == 0x42) ? 1 : 0; continue; }
    f[idx++] = b;
    if (idx < PMS_FRAME_LEN) continue;
    idx = 0;
    if (pmsFrameValid(f)) { memcpy(out, f, PMS_FRAME_LEN); got = true; }
  }
  return got;
}

bool readPMS(PmsReading &r) {
  uint8_t f[PMS_FRAME_LEN];
  if (!pmsReadFrame(f, PMS_WAIT_MS)) return false;
  if (!pmsIsT && pmsLooksLikeT(f)) {
    pmsIsT = true;
    Serial.println("[sensors] the Plantower is a PMS5003T: its temperature and humidity are published too");
  }
  pmsDecode(f, pmsIsT, r);
  return true;
}

// ============================================================================
// SENSOR DETECTION
//
// What is fitted is decided by who answers on the bus. Absence is normal and
// silent; only a sensor that was online and then stops answering is a fault.
// ============================================================================

const uint8_t KNOWN_ADDRS[] = {HM3301_I2C_ADDR, SEN5X_ADDR, BME680_ADDR_A, BME680_ADDR_B, SHT4X_ADDR, SCD4X_ADDR};
const int KNOWN_ADDR_COUNT = sizeof(KNOWN_ADDRS) / sizeof(KNOWN_ADDRS[0]);

bool i2cAnswers(uint8_t addr) {
  Wire.beginTransmission(addr);
  return Wire.endTransmission() == 0;
}

void configureBME680() {
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);
}

bool startBME680() {
  uint8_t addr = i2cAnswers(BME680_ADDR_A) ? BME680_ADDR_A : BME680_ADDR_B;
  bool ok = bme.begin(addr);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000);   // Adafruit_BusIO can reset the pins
  if (!ok) { ok = bme.begin(addr); Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000); }
  if (ok) configureBME680();
  return ok;
}

// Bring up whatever answers and is not already online. Returns true if
// anything new came up. `announce` = print the inventory line.
bool startAnswering(bool announce) {
  bool any = false;
  if (!g_hmOnline && i2cAnswers(HM3301_I2C_ADDR) && hm3301_init()) {
    g_hmOnline = true; g_hmLost = false; hmFails = 0; any = true;
  }
  if (!g_senOnline && i2cAnswers(SEN5X_ADDR) && sen5xBegin()) {
    g_senOnline = true; g_senLost = false; senFails = 0; any = true;
  }
  if (!g_bmeOnline && (i2cAnswers(BME680_ADDR_A) || i2cAnswers(BME680_ADDR_B)) && startBME680()) {
    g_bmeOnline = true; g_bmeLost = false; bmeFails = 0; any = true;
  }
  if (!g_shtOnline && i2cAnswers(SHT4X_ADDR) && sht4xBegin()) {
    g_shtOnline = true; g_shtLost = false; shtFails = 0; any = true;
  }
  if (!g_scdOnline && i2cAnswers(SCD4X_ADDR) && scd4xBegin()) {
    g_scdOnline = true; g_scdLost = false; scdFails = 0; any = true;
  }
  // The Plantower is not on the bus. Bytes in the UART buffer mean something is
  // talking on PMS_RX_PIN; a full scan (announce) also waits for a first frame.
  uint8_t frame[PMS_FRAME_LEN];
  if (!g_pmsOnline && PMS_RX_PIN >= 0 && (announce || Serial1.available())
      && pmsReadFrame(frame, PMS_WAIT_MS)) {
    g_pmsOnline = true; g_pmsLost = false; pmsFails = 0; any = true;
    pmsSince = millis();
    if (pmsLooksLikeT(frame)) pmsIsT = true;
  }
  if (announce || any) {
    String fitted, absent;
    auto add = [](String &s, const String &x) { if (s.length()) s += ", "; s += x; };
    String sen = sen5xModel[0] ? String(sen5xModel) + " (0x69)" : String("SEN5x (0x69)");
    if (g_hmOnline) add(fitted, "HM3301 (0x40)");  else add(absent, "HM3301");
    if (g_senOnline) add(fitted, sen);             else add(absent, "SEN5x");
    if (g_bmeOnline) add(fitted, "BME680");        else add(absent, "BME680");
    if (g_shtOnline) add(fitted, "SHT4x (0x44)");  else add(absent, "SHT4x");
    if (g_scdOnline) add(fitted, "SCD4x (0x62)");  else add(absent, "SCD4x");
    if (g_pmsOnline) add(fitted, String(pmsIsT ? "PMS5003T" : "PMS5003") + " (UART RX " + String(PMS_RX_PIN) + ")");
    else             add(absent, "PMS5003");
    Serial.printf("[sensors] fitted: %s%s%s\n", fitted.length() ? fitted.c_str() : "none",
                  absent.length() ? "  ·  not fitted: " : "", absent.c_str());
  }
  return any;
}

// A fitted sensor that keeps failing is a real fault — say so once.
void noteRead(bool ok, bool &online, bool &lost, uint8_t &fails, const char* name) {
  if (ok) { fails = 0; return; }
  if (++fails >= SENSOR_LOST_AFTER) {
    online = false; lost = true; fails = 0;
    Serial.printf("[sensors] %s stopped answering — check its cable; looking for it every %lu min\n",
                  name, (unsigned long)(SENSOR_RESCAN_MS / 60000UL));
  }
}

// ============================================================================
// SENSOR BRING-UP — pin auto-detect (v4), now counting the SEN5x too
// ============================================================================

int probePins(int sda, int scl) {
  Wire.end();
  delay(5);
  if (!Wire.begin(sda, scl, 100000)) return 0;
  delay(20);
  int hits = 0;
  for (int i = 0; i < KNOWN_ADDR_COUNT; i++) {
    if (i2cAnswers(KNOWN_ADDRS[i])) hits++;
  }
  return hits;
}

void bringUpSensors(const char* reason) {
  Serial.printf("[sensors] scanning the bus (%s)\n", reason);
  int bestSda = -1, bestScl = -1, bestHits = 0;
  for (int i = 0; i < I2C_CANDIDATE_COUNT; i++) {
    int hits = probePins(I2C_CANDIDATES[i].sda, I2C_CANDIDATES[i].scl);
    if (hits > bestHits) {
      bestHits = hits;
      bestSda  = I2C_CANDIDATES[i].sda;
      bestScl  = I2C_CANDIDATES[i].scl;
    }
  }

  // Nothing at all is the one case worth a hint — a node with no sensors
  // publishes nothing. Said once per scan, not per reading.
  if (bestHits == 0) {
    I2C_SDA_PIN = I2C_CANDIDATES[0].sda;
    I2C_SCL_PIN = I2C_CANDIDATES[0].scl;
    Wire.end();
    delay(5);
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000);
    Serial.println("[sensors] no I2C sensor answered. On the XIAO Grove shield only the two sockets");
    Serial.println("[sensors] marked I2C carry the bus. HM3301 and SEN5x need 5 V. Retrying every 5 min.");
    startAnswering(true);   // a Plantower-only node has nothing on the bus
    return;
  }

  I2C_SDA_PIN = bestSda;
  I2C_SCL_PIN = bestScl;
  Wire.end();
  delay(5);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000);
  Serial.printf("[i2c] SDA=%d SCL=%d\n", I2C_SDA_PIN, I2C_SCL_PIN);
  startAnswering(true);
}

// ============================================================================
// SELF-UPDATE from the flash page
//
// The manifest the flash page serves (ESP Web Tools format, written by
// .github/workflows/firmware-build.yml) names the build and, per chip, the
// app image at 0x10000. That image is all an update needs: bootloader and
// partition table stay. Everything is fetched over HTTPS against the core's
// CA bundle, and the image itself carries a SHA-256 the updater checks.
//
// The bootloader's rollback is the safety net. A build that arrived this way
// boots on probation; it confirms itself only once it has read the manifest
// again, which proves WiFi, DNS, TLS and the update path all still work, so
// the fleet can always be reached with the next fix. A build that crashes, or
// cannot get that far in OTA_VERIFY_DEADLINE_MS, is rolled back on reboot,
// and the old build remembers not to fetch it again.
// ============================================================================

// Tells the core not to confirm an OTA build at boot; otaCheck() does it.
// C linkage: the weak default lives in the core's esp32-hal-misc.c.
extern "C" bool verifyRollbackLater() { return true; }

void otaBootCheck() {
  esp_ota_img_states_t st;
  if (esp_ota_get_state_partition(esp_ota_get_running_partition(), &st) == ESP_OK &&
      st == ESP_OTA_IMG_PENDING_VERIFY) {
    otaPendingVerify = true;
  }
  if (otaPendingVerify && !FW_BUILD[0]) {   // a hand build cannot check itself against the manifest
    esp_ota_mark_app_valid_cancel_rollback();
    otaPendingVerify = false;
  }
  String tried = prefs.getString("otatry", "");
  if (tried.length()) {
    prefs.remove("otatry");
    if (tried != FW_BUILD) {
      prefs.putString("otabad", tried);
      otaStatus = tried + " did not stay up and was rolled back; it will not be tried again";
      Serial.printf("[ota] %s\n", otaStatus.c_str());
    }
  }
  if (otaPendingVerify)
    Serial.printf("[ota] %s is new on this node: on probation until it reads the manifest\n", FW_BUILD);
}

void otaCheck() {
  lastOtaCheck = millis();
  if (!otaEnabled && !otaPendingVerify) return;
  if (WiFi.status() != WL_CONNECTED) return;
  if (!FW_BUILD[0]) { otaStatus = "built by hand, does not update itself"; return; }

  NetworkClientSecure tls;
  tls.useBuiltinCACertBundle();
  HTTPClient http;
  http.setTimeout(10000);
  if (!http.begin(tls, OTA_MANIFEST_URL)) { otaStatus = "could not open the flash page"; return; }
  int code = http.GET();
  if (code != 200) {
    otaStatus = "the flash page answered " + String(code) + " at " + localClock();
    http.end();
    return;
  }
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, http.getString());
  http.end();
  if (err) { otaStatus = String("the manifest did not parse: ") + err.c_str(); return; }

  if (otaPendingVerify) {
    esp_ota_mark_app_valid_cancel_rollback();
    otaPendingVerify = false;
    Serial.printf("[ota] %s read the manifest: it stays\n", FW_BUILD);
  }

  String version = doc["version"] | "";
  String app;
  for (JsonObject b : doc["builds"].as<JsonArray>()) {
    if (String(b["chipFamily"] | "") != OTA_CHIP) continue;
    for (JsonObject part : b["parts"].as<JsonArray>())
      if ((part["offset"] | 0) == 0x10000) app = String(part["path"] | "");
  }
  if (!version.length() || !app.length()) { otaStatus = "the manifest has no build for " + String(OTA_CHIP); return; }
  if (version == FW_BUILD) { otaStatus = "up to date, checked at " + localClock(); return; }
  if (!otaEnabled) return;
  if (version == prefs.getString("otabad", "")) {
    otaStatus = version + " was rolled back here before; staying on " + String(FW_BUILD);
    return;
  }

  String url = String(OTA_MANIFEST_URL);
  url = url.substring(0, url.lastIndexOf('/') + 1) + app;
  Serial.printf("[ota] %s -> %s: downloading %s\n", FW_BUILD, version.c_str(), url.c_str());
  prefs.putString("otatry", version);
  mqtt.disconnect();   // one TLS session at a time; it reconnects after the reboot, or below
  NetworkClientSecure dl;
  dl.useBuiltinCACertBundle();
  httpUpdate.rebootOnUpdate(true);
  httpUpdate.update(dl, url);
  // Only a failed update gets here; a good one has already rebooted into the new build.
  prefs.remove("otatry");
  otaStatus = "update to " + version + " failed: " + httpUpdate.getLastErrorString();
  Serial.printf("[ota] %s\n", otaStatus.c_str());
}

// ============================================================================
// SETUP / LOOP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n=== Making Sense Bali — DIY Node v5 (HM3301 / SEN5x / BME680 / PMS5003 / SHT4x / SCD4x, auto-detected) ===");
  Serial.printf("[boot] firmware %s\n", FW_BUILD[0] ? FW_BUILD : "built by hand");
  Serial.printf("[boot] AP name if portal opens: %s  (password: %s)\n",
                apName().c_str(), PORTAL_PASSWORD);

  prefs.begin("msb", false);
  otaBootCheck();

  // The status page's "Reopen setup" button sets this flag and reboots. Consume
  // it here so the portal opens exactly once, then clear it — otherwise a node
  // that loses power mid-setup comes back into the portal forever.
  bool flagged = prefs.getBool("forceportal", false);
  if (flagged) {
    prefs.remove("forceportal");
    Serial.println("[boot] reopen-setup flag was set — opening portal");
  }

  bool forcePortal = flagged || bootButtonHeld();
  if (PMS_RX_PIN >= 0) {
    Serial1.setRxBufferSize(2048);   // a minute of Plantower frames, so the newest is always in there
    Serial1.begin(9600, SERIAL_8N1, PMS_RX_PIN, -1);   // RX only: no TX pin is attached or driven
  }
  bringUpSensors("boot");
  lastSensorScan = millis();
  setupConfig(forcePortal);
  syncTime();
  startStatusServer();
}

void loop() {
  ensureWiFi();
  connectMQTT();
  mqtt.loop();
  status.handleClient();

  // On Smart Citizen because the node stopped answering: give the node another go.
  if (mqtt.connected() && !onNode && localBroker() && fallbackSince &&
      millis() - fallbackSince >= NODE_RETRY_MS) {
    Serial.println("[mqtt] trying the PLANETAI node again");
    mqtt.disconnect();
    lastMqttTry = 0;
  }

  // Self-update: a build on probation checks every minute until it confirms
  // itself, and gives up into a rollback at the deadline.
  if (otaPendingVerify && millis() >= OTA_VERIFY_DEADLINE_MS) {
    Serial.println("[ota] this build never reached the manifest: rebooting into the previous one");
    delay(200);
    ESP.restart();
  }
  uint32_t otaDue = otaPendingVerify ? OTA_VERIFY_RETRY_MS : (lastOtaCheck ? OTA_INTERVAL_MS : OTA_FIRST_CHECK_MS);
  if ((otaEnabled || otaPendingVerify) && WiFi.status() == WL_CONNECTED && millis() - lastOtaCheck >= otaDue) {
    otaCheck();
  }

  if (reopenPortalRequested) {
    delay(400);                       // let the browser get the response first
    Serial.println("[http] reopen-setup requested — restarting into portal");
    prefs.putBool("forceportal", true);
    delay(200);
    ESP.restart();
  }

  uint32_t now = millis();
  if (now - lastPublish >= PUBLISH_INTERVAL_MS || lastPublish == 0) {
    lastPublish = now;

    // Quiet check for sensors that weren't there (plugged in later, or came
    // back after a fault). With nothing fitted at all, redo the full pin scan.
    if (now - lastSensorScan >= SENSOR_RESCAN_MS) {
      lastSensorScan = now;
      bool anyFitted = g_hmOnline || g_senOnline || g_bmeOnline || g_shtOnline || g_scdOnline || g_pmsOnline;
      bool anyLost   = g_hmLost || g_senLost || g_bmeLost || g_shtLost || g_scdLost || g_pmsLost;
      if (!anyFitted && I2C_SDA_PIN >= 0 && !anyLost) {
        bringUpSensors("nothing fitted yet");
      } else if (!(g_hmOnline && g_senOnline && g_bmeOnline && g_shtOnline && g_scdOnline && g_pmsOnline)) {
        startAnswering(false);   // prints only if something new came up
      }
    }

    float tempC = NAN, humRH = NAN, pressureKPa = NAN, gasOhm = NAN;
    uint16_t pm1 = 0, pm25 = 0, pm10 = 0;
    Sen5xReading sen;
    PmsReading pms;
    Scd4xReading scd;
    float shtT = NAN, shtRH = NAN;

    bool bmeOk = g_bmeOnline && readBME680(tempC, humRH, pressureKPa, gasOhm);
    bool hmOk  = g_hmOnline  && readHM3301(pm1, pm25, pm10);
    bool senOk = g_senOnline && readSEN5x(sen);
    bool shtOk = g_shtOnline && readSHT4x(shtT, shtRH);
    bool scdOk = g_scdOnline && readSCD4x(scd);
    bool pmsOk = g_pmsOnline && readPMS(pms);
    if (g_bmeOnline) noteRead(bmeOk, g_bmeOnline, g_bmeLost, bmeFails, "BME680");
    if (g_hmOnline)  noteRead(hmOk,  g_hmOnline,  g_hmLost,  hmFails,  "HM3301");
    if (g_senOnline) noteRead(senOk, g_senOnline, g_senLost, senFails, sen5xModel[0] ? sen5xModel : "SEN5x");
    if (g_shtOnline) noteRead(shtOk, g_shtOnline, g_shtLost, shtFails, "SHT4x");
    if (g_scdOnline) noteRead(scdOk, g_scdOnline, g_scdLost, scdFails, "SCD4x");
    if (g_pmsOnline) noteRead(pmsOk, g_pmsOnline, g_pmsLost, pmsFails, pmsIsT ? "PMS5003T" : "PMS5003");
    bool pmsWarm = pmsOk && millis() - pmsSince >= PMS_WARMUP_MS;
    float iaq  = bmeOk ? computeIAQ(gasOhm, humRH) : NAN;

    // One line, only the sensors that are fitted.
    String line = "[read]";
    char b[96];
    if (hmOk)  { snprintf(b, sizeof(b), "  HM3301 PM1=%u PM2.5=%u PM10=%u", pm1, pm25, pm10); line += b; }
    if (senOk) { snprintf(b, sizeof(b), "  %s PM2.5=%.1f PM10=%.1f T=%.2f RH=%.1f VOC=%.0f NOx=%.0f",
                          sen5xModel[0] ? sen5xModel : "SEN5x", sen.pm25, sen.pm10, sen.tempC, sen.rh, sen.voc, sen.nox);
                 line += b; }
    if (bmeOk) { snprintf(b, sizeof(b), "  BME680 T=%.2f RH=%.2f P=%.3f Gas=%.0f IAQ~%.0f",
                          tempC, humRH, pressureKPa, gasOhm, iaq); line += b; }
    if (pmsOk) { snprintf(b, sizeof(b), "  %s PM1=%.0f PM2.5=%.0f PM10=%.0f%s", pmsIsT ? "PMS5003T" : "PMS5003",
                          pms.pm1, pms.pm25, pms.pm10, pmsWarm ? "" : " (warming up)"); line += b;
                 if (pmsIsT) { snprintf(b, sizeof(b), " T=%.1f RH=%.1f", pms.tempC, pms.rh); line += b; } }
    if (shtOk) { snprintf(b, sizeof(b), "  SHT4x T=%.2f RH=%.2f", shtT, shtRH); line += b; }
    if (scdOk) { snprintf(b, sizeof(b), "  SCD4x CO2=%.0f T=%.2f RH=%.2f", scd.co2, scd.tempC, scd.rh); line += b; }
    if (line.length() == 6) line += " no sensor read this cycle";
    Serial.println(line);

    bool ok = publishReadings(bmeOk, tempC, humRH, pressureKPa, gasOhm, iaq,
                              hmOk, pm1, pm25, pm10, senOk, sen,
                              pmsWarm, pms, shtOk, shtT, shtRH, scdOk, scd);

    // Snapshot for the status page.
    lastT = tempC; lastRH = humRH; lastP = pressureKPa; lastGas = gasOhm; lastIAQ = iaq;
    lastPM1 = pm1; lastPM25 = pm25; lastPM10 = pm10;
    lastBmeOk = bmeOk; lastHmOk = hmOk; lastSenOk = senOk;
    if (senOk) lastSen = sen;
    lastShtOk = shtOk; lastShtT = shtT; lastShtRH = shtRH;
    lastPmsOk = pmsOk; if (pmsOk) lastPms = pms;
    lastScdOk = scdOk; if (scdOk && !isnan(scd.co2)) lastScd = scd;
    lastPublishOk = ok;
    lastPublishAt = localClock();
    if (ok) publishCount++; else publishFailCount++;
  }

  delay(20);   // shorter than v2 so the status page stays responsive
}
