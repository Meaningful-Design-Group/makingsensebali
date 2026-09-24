// Making Sense Bali — DIY Node firmware
// v2 (WiFiManager, zero secrets in source) — ESP32-C3 SuperMini AND XIAO ESP32-S3
//
// Boards:  MakerGO ESP32-C3 SuperMini  |  Seeed XIAO ESP32-S3
//          Tools -> USB CDC On Boot: Enabled (BOTH boards, or Serial is silent)
// Sensors: BME680 (I2C 0x76/0x77) + Seeed Grove HM3301 (I2C 0x40)
// Platform: publishes to mqtt.smartcitizen.me over TLS
//
// Repo: https://github.com/Meaningful-Design-Group/makingsensebali
// License: MIT
//
// ---------------------------------------------------------------------------
// WHAT CHANGED vs v1 (plain, hardcoded)
// ---------------------------------------------------------------------------
//  * NO SECRETS IN THIS FILE. WiFi credentials and the Smart Citizen device
//    token are entered through a captive portal on a phone and stored in the
//    ESP32's NVS flash. One firmware image serves the whole fleet; nobody
//    needs the Arduino IDE after the batch flash.
//
//  * FIRST BOOT (or no saved WiFi): the node opens an access point named
//    MSB-Node-xxxxxx (xxxxxx = last 3 bytes of its MAC). Join it from a
//    phone (password below), the portal opens — or browse to 192.168.4.1.
//    Pick the real WiFi, type its password, paste the Smart Citizen token
//    from the device page, Save. The node reboots and starts publishing.
//
//  * CONFIGURED BOOT: connects in seconds, no portal.
//
//  * SAVED WIFI UNREACHABLE: portal opens for 3 minutes, then the node
//    reboots and tries the saved network again. This loop is deliberate —
//    a router power blip must NOT strand the node in AP mode forever.
//
//  * RECONFIGURE A WORKING NODE (new house, new token): hold the BOOT
//    button while the node starts, keep holding ~2 s after plugging in.
//    The portal opens with the saved token prefilled. Or simply power the
//    node up out of range of its saved WiFi and wait for the portal.
//
// Everything else — I2C pin auto-detect, no-fake-zeros, no-NaN, the IAQ
// approximation and its honest limitations — is carried over from v1
// unchanged. See those header notes in the repo history.
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

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WiFiManager.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <ArduinoJson.h>
#include <time.h>

// HM3301 is read directly over I2C without the Seeed_HM330X library — the
// Seeed library's u8/u16 typedefs don't compile against the modern
// arduino-esp32 core. The protocol is simple; see readHM3301().

// ============================================================================
// CONFIGURATION — fleet-wide constants only. Nothing device-specific here.
// ============================================================================

// Captive portal
const char* PORTAL_PASSWORD = "makingsense";   // AP join password; keeps a
                                               // neighbour from hijacking the
                                               // node during its config window
const uint16_t PORTAL_TIMEOUT_S = 180;         // portal lifetime before reboot

// BOOT button, for forcing the portal on a configured node.
//   XIAO ESP32-S3: BOOT = GPIO0.   ESP32-C3 SuperMini: BOOT = GPIO9.
// Detected at compile time from the selected board's target.
#if defined(CONFIG_IDF_TARGET_ESP32S3)
  const int BOOT_BTN_PIN = 0;
#elif defined(CONFIG_IDF_TARGET_ESP32C3)
  const int BOOT_BTN_PIN = 9;
#else
  const int BOOT_BTN_PIN = 0;   // sane default for other ESP32 variants
#endif

// Smart Citizen sensor IDs — SC global-catalog IDs for Bosch BME68X and
// Seeed HM-3301. Same for every node. For a Basic kit (no HM-3301), set the
// three PM IDs to 0 to skip publishing them.
const int SC_ID_PM1      = 233;  // µg/m³  — Seeed HM-3301 - PM1.0
const int SC_ID_PM25     = 234;  // µg/m³  — Seeed HM-3301 - PM2.5
const int SC_ID_PM10     = 235;  // µg/m³  — Seeed HM-3301 - PM10.0
const int SC_ID_TEMP     = 237;  // °C     — Bosch BME68X - Temperature (RAW — see limitation)
const int SC_ID_HUM      = 238;  // %RH    — Bosch BME68X - Humidity   (RAW — see limitation)
const int SC_ID_PRESSURE = 239;  // kPa    — Bosch BME68X - Pressure
const int SC_ID_GAS      = 240;  // Ohm    — Bosch BME68X - Gas Resistance (RAW ohms)
const int SC_ID_IAQ      = 241;  // index  — Bosch BME68X - IAQ (open approximation)

// MQTT broker (do not change unless testing locally)
const char* MQTT_HOST = "mqtt.smartcitizen.me";
const uint16_t MQTT_PORT = 8883;

// Timing
const uint32_t PUBLISH_INTERVAL_MS     = 60UL * 1000UL;  // one reading/minute
const uint32_t WIFI_RETRY_INTERVAL_MS  = 15UL * 1000UL;  // reconnect attempt spacing

// --- I2C pin auto-detect (unchanged from v1) ---
// Both target boards are covered: {5,6} is the XIAO ESP32-S3 Grove connector
// (the shield's two I2C sockets both land there), {8,9} is the C3 SuperMini
// default, {6,7} the XIAO C3 Grove. Each pair listed in both orientations,
// because swapped SDA/SCL presents as "sensor not found".
//
// Note on GPIO8/GPIO9 (C3): both are strapping pins (GPIO9 is BOOT). Fine in
// normal operation — idle I2C is pulled HIGH, which is what the chip wants
// at boot. If a node intermittently fails to boot, rewire to GPIO4/GPIO5 and
// move {4,5} first.
struct I2CPins { int sda; int scl; };
const I2CPins I2C_CANDIDATES[] = {
  {5, 6},  {6, 5},     // Seeed XIAO ESP32-S3 Grove (D4/D5)  — the fleet standard
  {8, 9},  {9, 8},     // C3 SuperMini default
  {6, 7},  {7, 6},     // Seeed XIAO ESP32-C3 Grove (D4/D5)
  {10, 9}, {9, 10},    // seen on a hand-wired Bali unit
  {10, 8}, {8, 10},    // also seen in a bench scan of that unit
  {4, 5},  {5, 4}      // safe spares, off the strapping pins
};
const int I2C_CANDIDATE_COUNT = sizeof(I2C_CANDIDATES) / sizeof(I2C_CANDIDATES[0]);

int I2C_SDA_PIN = -1;   // filled in by bringUpSensors(). -1 = not yet.
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

String scToken;                 // Smart Citizen device token, from NVS
uint32_t lastPublish   = 0;
uint32_t lastWifiRetry = 0;

bool g_bmeOnline = false;
bool g_hmOnline  = false;

// Clean-air gas-resistance reference for the IAQ approximation, learned at
// runtime (see computeIAQ). 0 = not yet initialised.
float gasBaselineOhm = 0.0f;

// ============================================================================
// CONFIG PORTAL (WiFiManager + NVS)
// ============================================================================

String apName() {
  return "MSB-Node-" + String((uint32_t)(ESP.getEfuseMac() & 0xFFFFFF), HEX);
}

// Basic sanity on the token: trim whitespace (the #1 paste error), reject
// empties. The platform doesn't offer a way to verify a token before use, so
// the real confirmation is the MQTT connect result — watch the serial line.
String sanitizeToken(String t) {
  t.trim();
  return t;
}

// Runs the WiFiManager flow. Blocks until WiFi is up, or reboots on portal
// timeout so a router power blip can't strand the node in AP mode.
void setupConfig(bool forcePortal) {
  prefs.begin("msb", false);
  scToken = prefs.getString("token", "");

  WiFiManager wm;
  wm.setTitle("Making Sense Bali — node setup");
  wm.setConfigPortalTimeout(PORTAL_TIMEOUT_S);
  wm.setConnectTimeout(20);

  WiFiManagerParameter tokenParam(
      "sctoken", "Smart Citizen device token (from your device page)",
      scToken.c_str(), 16);
  wm.addParameter(&tokenParam);

  // Persist the token as soon as Save is pressed — even if the WiFi join
  // then fails, the token survives for the next attempt.
  wm.setSaveParamsCallback([&tokenParam]() {
    String t = sanitizeToken(tokenParam.getValue());
    if (t.length() > 0) {
      prefs.putString("token", t);
      Serial.printf("[config] token saved (%d chars)\n", t.length());
    }
  });

  bool ok;
  if (forcePortal) {
    Serial.println("[config] BOOT held — opening portal on demand");
    ok = wm.startConfigPortal(apName().c_str(), PORTAL_PASSWORD);
  } else {
    // Connects with saved credentials if any; opens the portal otherwise.
    ok = wm.autoConnect(apName().c_str(), PORTAL_PASSWORD);
  }

  if (!ok) {
    Serial.println("[config] portal timed out / join failed — rebooting to retry saved WiFi");
    delay(1000);
    ESP.restart();
  }

  scToken = sanitizeToken(prefs.getString("token", ""));
  Serial.printf("[wifi] connected — IP %s · RSSI %d dBm\n",
                WiFi.localIP().toString().c_str(), WiFi.RSSI());
  if (scToken.length() == 0) {
    Serial.println("[config] *** NO TOKEN SAVED — node will read sensors but");
    Serial.println("[config] *** publish NOTHING. Hold BOOT at power-up to set one.");
  } else {
    Serial.printf("[config] token: %s\n", scToken.c_str());
  }
}

// Was BOOT held during the first moments after power-up? Read before any
// I2C activity (on the C3, BOOT shares GPIO9 with an I2C candidate pair).
bool bootButtonHeld() {
  pinMode(BOOT_BTN_PIN, INPUT_PULLUP);
  delay(50);
  if (digitalRead(BOOT_BTN_PIN) != LOW) return false;
  // Debounce: must stay held for ~1.5 s to count, so a bouncy line or a
  // fumbled plug-in doesn't wipe a deployed node's config flow.
  uint32_t start = millis();
  while (millis() - start < 1500) {
    if (digitalRead(BOOT_BTN_PIN) != LOW) return false;
    delay(10);
  }
  return true;
}

// ============================================================================
// WIFI (runtime) + NTP
// ============================================================================

// After boot, the ESP32 auto-reconnects on its own; this just nudges it and
// logs, spaced out so the loop isn't spammed. The portal is NOT reopened at
// runtime — a deployed node that loses WiFi should rejoin when the router
// returns, not sit in AP mode. (Power-cycling it out of range opens the
// portal via the boot path, which is the documented way to reconfigure.)
void ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  uint32_t now = millis();
  if (now - lastWifiRetry < WIFI_RETRY_INTERVAL_MS) return;
  lastWifiRetry = now;
  Serial.println("[wifi] disconnected — reconnecting");
  WiFi.reconnect();
}

void syncTime() {
  // Bali is UTC+8 (WITA). We publish in UTC anyway, so the offset only
  // affects local logging.
  configTime(8 * 3600, 0, "pool.ntp.org", "time.google.com");

  Serial.print("[ntp] syncing");
  time_t now = time(nullptr);
  uint32_t start = millis();
  while (now < 1700000000 && (millis() - start) < 15000) {  // ~2023-11
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

// ============================================================================
// MQTT
// ============================================================================

void connectMQTT() {
  if (mqtt.connected()) return;
  if (WiFi.status() != WL_CONNECTED) return;
  if (scToken.length() == 0) return;   // no token, no identity, no connect

  // v2 still skips CA validation. For production, replace with
  // net.setCACert(<ISRG Root X1>) — the SC broker uses Let's Encrypt.
  // Skipping validation = vulnerable to MITM on the LAN. Acceptable for a
  // workshop kit, not for a sensor cited in policy work.
  net.setInsecure();

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(512);   // default 256 is too small for our payload

  // SC convention: token is both client_id and username; password empty.
  Serial.printf("[mqtt] connecting to %s:%u ", MQTT_HOST, MQTT_PORT);
  if (mqtt.connect(scToken.c_str(), scToken.c_str(), "")) {
    Serial.println("ok");
  } else {
    // rc=5 (not authorised) with everything else working is the signature
    // of a mistyped token. Hold BOOT at power-up to re-enter it.
    Serial.printf("failed (rc=%d) — will retry. rc=5 usually means BAD TOKEN\n",
                  mqtt.state());
  }
}

// bmeOk / hmOk gate which channels enter the payload. A failed sensor
// contributes NOTHING — no zeros, no NaN (serialised null) stored as data.
bool publishReadings(bool bmeOk, float tempC, float humRH, float pressureKPa,
                     float gasOhm, float iaq,
                     bool hmOk, uint16_t pm1, uint16_t pm25, uint16_t pm10) {
  if (!mqtt.connected()) return false;

  JsonDocument doc;
  JsonArray data = doc["data"].to<JsonArray>();
  JsonObject reading = data.add<JsonObject>();
  reading["recorded_at"] = iso8601UTC();
  JsonArray sensors = reading["sensors"].to<JsonArray>();

  // Skips unconfigured IDs (0) AND non-finite values (NaN/inf).
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

  // Nothing valid this cycle — say so and send nothing.
  if (sensors.size() == 0) {
    Serial.println("[mqtt] no valid readings this cycle — nothing published");
    return false;
  }

  String json;
  serializeJson(doc, json);

  String topic = String("device/sck/") + scToken + "/readings";

  // PubSubClient publishes at QoS 0. `true` means the bytes reached the
  // socket — NOT that the broker acknowledged or the platform ingested.
  bool ok = mqtt.publish(topic.c_str(), json.c_str(), false);
  if (ok) {
    Serial.printf("[mqtt] published (%u bytes): %s\n", json.length(), json.c_str());
  } else {
    Serial.println("[mqtt] publish failed");
  }
  return ok;
}

// ============================================================================
// SENSORS (unchanged from v1)
// ============================================================================

// computeIAQ — OPEN air-quality index, 0 (clean) … 500 (polluted).
// NOT Bosch's BSEC. See v1 header notes for the honest limitations: the
// baseline seeds from the first post-boot reading, early IAQ trends clean,
// it is uncalibrated and not comparable unit-to-unit. For defensible policy
// numbers: BSEC2 firmware or co-location correction in the pipeline.
float computeIAQ(float gasOhm, float humRH) {
  if (isnan(gasOhm) || isnan(humRH) || gasOhm <= 0.0f) return NAN;

  if (gasBaselineOhm <= 0.0f) {
    gasBaselineOhm = gasOhm;  // first reading seeds the baseline
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
  if (!bme.performReading()) {
    return false;
  }
  tempC       = bme.temperature;        // °C  — RAW, self-heated (see header)
  humRH       = bme.humidity;           // %RH — RAW, self-heated (see header)
  pressureKPa = bme.pressure / 1000.0f; // Pa → kPa (SC platform uses kPa)
  gasOhm      = bme.gas_resistance;     // Ω — RAW ohms, channel 240 wants this
  return !(isnan(tempC) || isnan(humRH));
}

// HM3301 — direct I2C. Init: write 0x88 to 0x40 (select I2C mode; the sensor
// boots in UART mode). Read: 29-byte frame; bytes 10-15 are atmospheric
// PM1/PM2.5/PM10; byte 28 is a checksum over bytes 0-27.
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
// SENSOR BRING-UP (unchanged from v1)
// ============================================================================

int probePins(int sda, int scl) {
  Wire.end();
  delay(5);
  if (!Wire.begin(sda, scl, 100000)) return 0;   // 100 kHz, forgiving
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

  // Re-assert pins in case Adafruit_BusIO reset them, then retry once.
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
  Serial.println("\n=== Making Sense Bali — DIY Node v2 (WiFiManager) ===");
  Serial.printf("[boot] AP name if portal opens: %s  (password: %s)\n",
                apName().c_str(), PORTAL_PASSWORD);

  // Read the BOOT button BEFORE any I2C traffic — on the C3 it shares
  // GPIO9 with an I2C candidate pair.
  bool forcePortal = bootButtonHeld();

  bringUpSensors("boot");

  setupConfig(forcePortal);   // blocks until WiFi is up, or reboots
  syncTime();
}

void loop() {
  ensureWiFi();
  connectMQTT();
  mqtt.loop();

  uint32_t now = millis();
  if (now - lastPublish >= PUBLISH_INTERVAL_MS || lastPublish == 0) {
    lastPublish = now;

    // Retry bring-up while anything is missing (also makes boot diagnostics
    // visible on native-USB boards, where the CDC port enumerates late).
    if (!g_bmeOnline || !g_hmOnline) {
      bringUpSensors("retry — sensor missing");
    }

    float tempC = NAN, humRH = NAN, pressureKPa = NAN, gasOhm = NAN;
    uint16_t pm1 = 0, pm25 = 0, pm10 = 0;

    bool bmeOk = g_bmeOnline && readBME680(tempC, humRH, pressureKPa, gasOhm);
    bool hmOk  = g_hmOnline  && readHM3301(pm1, pm25, pm10);

    // IAQ only when the BME read succeeded. '~' = approximation, not BSEC.
    float iaq = bmeOk ? computeIAQ(gasOhm, humRH) : NAN;

    Serial.printf("[read] T=%.2f°C  RH=%.2f%%  P=%.3fkPa  Gas=%.0fΩ  IAQ~%.0f  "
                  "PM1=%u  PM2.5=%u  PM10=%u  (bme=%d hm=%d)\n",
                  tempC, humRH, pressureKPa, gasOhm, iaq,
                  pm1, pm25, pm10, bmeOk, hmOk);

    publishReadings(bmeOk, tempC, humRH, pressureKPa, gasOhm, iaq,
                    hmOk, pm1, pm25, pm10);
  }

  delay(100);
}
