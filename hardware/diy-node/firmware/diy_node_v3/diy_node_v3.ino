// Making Sense Bali — DIY Node firmware
// v3 (WiFiManager + node identity + local status page)
//    ESP32-C3 SuperMini AND XIAO ESP32-S3
//
// Boards:  MakerGO ESP32-C3 SuperMini  |  Seeed XIAO ESP32-S3
//          Tools -> USB CDC On Boot: Enabled (BOTH boards, or Serial is silent)
// Sensors: BME680 (I2C 0x76/0x77) + Seeed Grove HM3301 (I2C 0x40)
// Platform: publishes to mqtt.smartcitizen.me over TLS
//
// Repo: https://github.com/mdg-bali/makingsensebali
// License: MIT
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
#include <time.h>

// HM3301 is read directly over I2C without the Seeed_HM330X library — the
// Seeed library's u8/u16 typedefs don't compile against the modern
// arduino-esp32 core. The protocol is simple; see readHM3301().

// ============================================================================
// CONFIGURATION — fleet-wide constants only. Nothing device-specific here.
// ============================================================================

const char* PORTAL_PASSWORD = "makingsense";   // AP join password
const uint16_t PORTAL_TIMEOUT_S = 180;         // portal lifetime before reboot

#if defined(CONFIG_IDF_TARGET_ESP32S3)
  const int BOOT_BTN_PIN = 0;
#elif defined(CONFIG_IDF_TARGET_ESP32C3)
  const int BOOT_BTN_PIN = 9;
#else
  const int BOOT_BTN_PIN = 0;
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

const char* MQTT_HOST = "mqtt.smartcitizen.me";
const uint16_t MQTT_PORT = 8883;

const uint32_t PUBLISH_INTERVAL_MS     = 60UL * 1000UL;
const uint32_t WIFI_RETRY_INTERVAL_MS  = 15UL * 1000UL;

// A Smart Citizen device token is six characters — verified against the SCK
// firmware, lib/Shared/Config.h: `struct Token { ... char token[7]="null"; }`.
// The field is sized larger so a paste with stray characters is visible and
// correctable rather than silently truncated.
const int TOKEN_FIELD_LEN = 16;
const int NAME_FIELD_LEN  = 32;
const int SITE_FIELD_LEN  = 64;

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

WiFiClientSecure net;
PubSubClient mqtt(net);
Preferences prefs;
WebServer status(80);

// --- identity, from NVS ---
String scToken;      // Smart Citizen device token — the publishing identity
String nodeName;     // human name, local only
String nodeSite;     // where it hangs, local only
String nodeHeight;   // metres above ground, local only

uint32_t lastPublish   = 0;
uint32_t lastWifiRetry = 0;

bool g_bmeOnline = false;
bool g_hmOnline  = false;

// Last cycle, for the status page.
float  lastT = NAN, lastRH = NAN, lastP = NAN, lastGas = NAN, lastIAQ = NAN;
uint16_t lastPM1 = 0, lastPM25 = 0, lastPM10 = 0;
bool   lastBmeOk = false, lastHmOk = false;
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
// CONFIG PORTAL (WiFiManager + NVS)
// ============================================================================

// Pure read — prefs is opened once in setup().
void loadIdentity() {
  scToken    = sanitizeToken(prefs.getString("token", ""));
  nodeName   = prefs.getString("name", "");
  nodeSite   = prefs.getString("site", "");
  nodeHeight = prefs.getString("height", "");
}

void setupConfig(bool forcePortal) {
  loadIdentity();

  WiFiManager wm;
  wm.setTitle("Making Sense Bali — node setup");
  wm.setConfigPortalTimeout(PORTAL_TIMEOUT_S);
  wm.setConnectTimeout(20);

  WiFiManagerParameter hdrToken(
      "<p style='margin:14px 0 4px;font-weight:600'>Smart Citizen</p>"
      "<p style='margin:0 0 8px;font-size:13px;color:#555'>The six-character "
      "device token from your device page. This is what identifies the node to "
      "the platform — nothing publishes without it.</p>");
  WiFiManagerParameter tokenParam("sctoken", "Device token", scToken.c_str(), TOKEN_FIELD_LEN);

  WiFiManagerParameter hdrLocal(
      "<p style='margin:18px 0 4px;font-weight:600'>This node</p>"
      "<p style='margin:0 0 8px;font-size:13px;color:#555'>For finding and "
      "checking the node on your own network. <b>These are not sent to Smart "
      "Citizen</b> — set the display name and location on the device page there.</p>");
  WiFiManagerParameter nameParam("nodename", "Name (e.g. Balai Banjar Serangan)", nodeName.c_str(), NAME_FIELD_LEN);
  WiFiManagerParameter siteParam("nodesite", "Where it hangs (desa, landmark)", nodeSite.c_str(), SITE_FIELD_LEN);
  WiFiManagerParameter heightParam("nodehgt", "Height above ground, metres", nodeHeight.c_str(), 6);

  wm.addParameter(&hdrToken);
  wm.addParameter(&tokenParam);
  wm.addParameter(&hdrLocal);
  wm.addParameter(&nameParam);
  wm.addParameter(&siteParam);
  wm.addParameter(&heightParam);

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

    Serial.printf("[config] saved — token %s · name '%s' · site '%s' · height '%s'\n",
                  t.length() ? "yes" : "NO", n.c_str(), s.c_str(), h.c_str());
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
  if (isnan(v)) return "<span class='bad'>—</span>";
  char b[24];
  snprintf(b, sizeof(b), "%.*f", dp, v);
  return String(b) + " " + unit;
}

void handleStatus() {
  String title = nodeName.length() ? nodeName : apName();
  String h;
  h.reserve(4096);
  h += "<!doctype html><html><head><meta charset='utf-8'>";
  h += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
  h += "<title>" + htmlEscape(title) + " — Making Sense Bali</title><style>";
  h += "body{font-family:system-ui,-apple-system,sans-serif;margin:0;padding:18px;";
  h += "background:#16181b;color:#e8e4da;line-height:1.5}";
  h += "h1{font-size:21px;margin:0 0 2px}.sub{color:#8b8578;font-size:13px;margin:0 0 18px}";
  h += "table{width:100%;max-width:560px;border-collapse:collapse;margin-bottom:22px}";
  h += "th{text-align:left;font-weight:400;color:#8b8578;padding:6px 10px 6px 0;width:46%;";
  h += "vertical-align:top;font-size:14px}td{padding:6px 0;font-size:14px}";
  h += "h2{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#7f8b86;";
  h += "margin:0 0 6px;font-weight:400}.ok{color:#7bb893}.bad{color:#e07a5f}";
  h += ".note{max-width:560px;color:#8b8578;font-size:13px;border-top:1px solid #2c2f34;padding-top:14px}";
  h += "button{font:inherit;background:#24262b;color:#e8e4da;border:1px solid #3a3d43;";
  h += "border-radius:7px;padding:9px 15px;cursor:pointer}</style></head><body>";

  h += "<h1>" + htmlEscape(title) + "</h1>";
  h += "<p class='sub'>" + htmlEscape(nodeSite.length() ? nodeSite : "site not set");
  if (nodeHeight.length()) h += " · " + htmlEscape(nodeHeight) + " m above ground";
  h += "</p>";

  h += "<h2>Latest reading</h2><table>";
  h += row("Temperature", fmt(lastT, 2, "&deg;C"));
  h += row("Humidity",    fmt(lastRH, 2, "%"));
  h += row("Pressure",    fmt(lastP, 3, "kPa"));
  h += row("Gas",         fmt(lastGas, 0, "&Omega;"));
  h += row("IAQ (approx)", fmt(lastIAQ, 0, ""));
  h += row("PM1",   lastHmOk ? String(lastPM1)  + " &micro;g/m&sup3;" : "<span class='bad'>—</span>");
  h += row("PM2.5", lastHmOk ? String(lastPM25) + " &micro;g/m&sup3;" : "<span class='bad'>—</span>");
  h += row("PM10",  lastHmOk ? String(lastPM10) + " &micro;g/m&sup3;" : "<span class='bad'>—</span>");
  h += "</table>";

  h += "<h2>Health</h2><table>";
  h += row("BME680", g_bmeOnline ? "<span class='ok'>online</span>" : "<span class='bad'>not found</span>");
  h += row("HM3301", g_hmOnline  ? "<span class='ok'>online</span>" : "<span class='bad'>not found</span>");
  h += row("Smart Citizen token", scToken.length() ? "<span class='ok'>" + maskedToken() + "</span>"
                                                   : "<span class='bad'>NOT SET — nothing is published</span>");
  h += row("MQTT", mqtt.connected() ? "<span class='ok'>connected</span>" : "<span class='bad'>disconnected</span>");
  h += row("Last publish", (lastPublishOk ? "<span class='ok'>ok</span> at " : "<span class='bad'>failed</span> at ") + htmlEscape(lastPublishAt));
  h += row("Published / failed", String(publishCount) + " / " + String(publishFailCount));
  h += "</table>";

  h += "<h2>Connection</h2><table>";
  h += row("WiFi", htmlEscape(WiFi.SSID()));
  h += row("Signal", String(WiFi.RSSI()) + " dBm");
  h += row("IP", WiFi.localIP().toString());
  h += row("Also reachable at", "http://" + mdnsHost() + ".local");
  h += row("I2C pins", "SDA " + String(I2C_SDA_PIN) + " · SCL " + String(I2C_SCL_PIN));
  h += row("Uptime", uptimeStr());
  h += "</table>";

  h += "<form method='POST' action='/setup' onsubmit=\"return confirm('Reboot into the setup portal? The node stops measuring until setup finishes.')\">";
  h += "<button type='submit'>Reopen setup</button></form>";

  h += "<p class='note'>Name and site are stored on this node only. The display "
       "name and location on smartcitizen.me are set there, on the device page. "
       "Temperature and humidity are published raw — they have not been checked "
       "against a reference station, so expect them to read high in an enclosure.</p>";
  h += "</body></html>";

  status.send(200, "text/html; charset=utf-8", h);
}

void handleSetupRequest() {
  status.send(200, "text/html; charset=utf-8",
    "<!doctype html><meta charset='utf-8'>"
    "<body style='font-family:system-ui;background:#16181b;color:#e8e4da;padding:22px'>"
    "<p>Rebooting into setup. Join the WiFi network <b>" + apName() +
    "</b> (password <b>" + String(PORTAL_PASSWORD) + "</b>) in about 15 seconds.</p></body>");
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

void connectMQTT() {
  if (mqtt.connected()) return;
  if (WiFi.status() != WL_CONNECTED) return;
  if (scToken.length() == 0) return;

  net.setInsecure();   // see v2 notes — fine for a workshop kit, not for policy data
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(512);

  Serial.printf("[mqtt] connecting to %s:%u ", MQTT_HOST, MQTT_PORT);
  if (mqtt.connect(scToken.c_str(), scToken.c_str(), "")) {
    Serial.println("ok");
  } else {
    Serial.printf("failed (rc=%d) — will retry. rc=5 usually means BAD TOKEN\n", mqtt.state());
  }
}

bool publishReadings(bool bmeOk, float tempC, float humRH, float pressureKPa,
                     float gasOhm, float iaq,
                     bool hmOk, uint16_t pm1, uint16_t pm25, uint16_t pm10) {
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
// SENSOR BRING-UP (unchanged)
// ============================================================================

int probePins(int sda, int scl) {
  Wire.end();
  delay(5);
  if (!Wire.begin(sda, scl, 100000)) return 0;
  delay(20);
  const uint8_t wanted[] = {0x40, 0x76, 0x77};
  int hits = 0;
  for (int i = 0; i < 3; i++) {
    Wire.beginTransmission(wanted[i]);
    if (Wire.endTransmission() == 0) {
      Serial.printf("      SDA=%2d SCL=%2d -> 0x%02X responding\n", sda, scl, wanted[i]);
      hits++;
    }
  }
  return hits;
}

void bringUpSensors(const char* reason) {
  Serial.printf("\n[sensors] bring-up (%s)\n", reason);
  Serial.println("[i2c] probing candidate pin pairs:");
  int bestSda = -1, bestScl = -1, bestHits = 0;
  for (int i = 0; i < I2C_CANDIDATE_COUNT; i++) {
    int hits = probePins(I2C_CANDIDATES[i].sda, I2C_CANDIDATES[i].scl);
    if (hits > bestHits) {
      bestHits = hits;
      bestSda  = I2C_CANDIDATES[i].sda;
      bestScl  = I2C_CANDIDATES[i].scl;
    }
  }

  if (bestHits == 0) {
    Serial.println("      NO devices found on ANY candidate pair.");
    Serial.println("      -> Not a pin problem. Check power and cabling:");
    Serial.println("         HM3301 needs 5V; most BME680 breakouts want 3V3.");
    Serial.println("         On the XIAO Grove shield, ONLY the two sockets");
    Serial.println("         marked I2C carry the bus — the other six are GPIO.");
    I2C_SDA_PIN = I2C_CANDIDATES[0].sda;
    I2C_SCL_PIN = I2C_CANDIDATES[0].scl;
    Wire.end();
    delay(5);
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000);
    g_bmeOnline = false;
    g_hmOnline  = false;
    Serial.println();
    return;
  }

  I2C_SDA_PIN = bestSda;
  I2C_SCL_PIN = bestScl;
  Serial.printf("[i2c] USING SDA=%d SCL=%d (%d device(s) found)\n",
                I2C_SDA_PIN, I2C_SCL_PIN, bestHits);

  Wire.end();
  delay(5);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000);

  g_bmeOnline = bme.begin(0x76);
  if (!g_bmeOnline) g_bmeOnline = bme.begin(0x77);

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  if (!g_bmeOnline) {
    Serial.println("[bme680] retrying with pins re-asserted");
    g_bmeOnline = bme.begin(0x76);
    if (!g_bmeOnline) g_bmeOnline = bme.begin(0x77);
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  }

  if (g_bmeOnline) {
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150);
    Serial.println("[bme680] ONLINE — heater + filter configured");
  } else {
    Serial.println("[bme680] not found (is it in an I2C-marked socket?)");
  }

  g_hmOnline = hm3301_init();
  Serial.println(g_hmOnline ? "[hm3301] ONLINE at 0x40"
                            : "[hm3301] not found (needs 5V — check Grove cable)");
  Serial.println();
}

// ============================================================================
// SETUP / LOOP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\n=== Making Sense Bali — DIY Node v3 (WiFiManager + status page) ===");
  Serial.printf("[boot] AP name if portal opens: %s  (password: %s)\n",
                apName().c_str(), PORTAL_PASSWORD);

  prefs.begin("msb", false);

  // The status page's "Reopen setup" button sets this flag and reboots. Consume
  // it here so the portal opens exactly once, then clear it — otherwise a node
  // that loses power mid-setup comes back into the portal forever.
  bool flagged = prefs.getBool("forceportal", false);
  if (flagged) {
    prefs.remove("forceportal");
    Serial.println("[boot] reopen-setup flag was set — opening portal");
  }

  bool forcePortal = flagged || bootButtonHeld();
  bringUpSensors("boot");
  setupConfig(forcePortal);
  syncTime();
  startStatusServer();
}

void loop() {
  ensureWiFi();
  connectMQTT();
  mqtt.loop();
  status.handleClient();

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

    if (!g_bmeOnline || !g_hmOnline) {
      bringUpSensors("retry — sensor missing");
    }

    float tempC = NAN, humRH = NAN, pressureKPa = NAN, gasOhm = NAN;
    uint16_t pm1 = 0, pm25 = 0, pm10 = 0;

    bool bmeOk = g_bmeOnline && readBME680(tempC, humRH, pressureKPa, gasOhm);
    bool hmOk  = g_hmOnline  && readHM3301(pm1, pm25, pm10);
    float iaq  = bmeOk ? computeIAQ(gasOhm, humRH) : NAN;

    Serial.printf("[read] T=%.2f°C  RH=%.2f%%  P=%.3fkPa  Gas=%.0fΩ  IAQ~%.0f  "
                  "PM1=%u  PM2.5=%u  PM10=%u  (bme=%d hm=%d)\n",
                  tempC, humRH, pressureKPa, gasOhm, iaq,
                  pm1, pm25, pm10, bmeOk, hmOk);

    bool ok = publishReadings(bmeOk, tempC, humRH, pressureKPa, gasOhm, iaq,
                              hmOk, pm1, pm25, pm10);

    // Snapshot for the status page.
    lastT = tempC; lastRH = humRH; lastP = pressureKPa; lastGas = gasOhm; lastIAQ = iaq;
    lastPM1 = pm1; lastPM25 = pm25; lastPM10 = pm10;
    lastBmeOk = bmeOk; lastHmOk = hmOk;
    lastPublishOk = ok;
    lastPublishAt = localClock();
    if (ok) publishCount++; else publishFailCount++;
  }

  delay(20);   // shorter than v2 so the status page stays responsive
}
