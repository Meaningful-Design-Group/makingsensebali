// Pure decoders for the DIY node: bytes in, numbers out. No Arduino calls, so
// test/decoders_test.cpp compiles this same file on a laptop and checks it
// against the datasheets' own examples.
#pragma once
#include <math.h>
#include <stdint.h>
#include <stddef.h>

struct Scd4xReading { float co2 = NAN, tempC = NAN, rh = NAN; };   // ppm, °C, %RH
constexpr uint8_t PMS_FRAME_LEN = 32;   // one Plantower frame, header to checksum
struct PmsReading {
  float pm1 = NAN, pm25 = NAN, pm10 = NAN;   // µg/m³, atmospheric environment
  float tempC = NAN, rh = NAN;               // PMS5003T only
};

// Shared by every Sensirion part here (SEN5x, SHT4x, SCD4x): 16-bit words, each
// followed by this CRC-8 on the wire.
uint8_t sensirionCrc(const uint8_t* data, size_t len) {
  uint8_t crc = 0xFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (uint8_t b = 0; b < 8; b++) {
      crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x31) : (uint8_t)(crc << 1);
    }
  }
  return crc;
}

void sht4xDecode(const uint16_t w[2], float &tempC, float &rh) {
  tempC = -45.0f + 175.0f * (float)w[0] / 65535.0f;
  rh    =  -6.0f + 125.0f * (float)w[1] / 65535.0f;
  if (rh < 0.0f)   rh = 0.0f;     // the datasheet's own advice: the RH line overshoots at both ends
  if (rh > 100.0f) rh = 100.0f;
}

void scd4xDecode(const uint16_t w[3], Scd4xReading &r) {
  r.co2   = w[0] ? (float)w[0] : NAN;   // 0 ppm is not a reading
  r.tempC = -45.0f + 175.0f * (float)w[1] / 65535.0f;
  r.rh    = 100.0f * (float)w[2] / 65535.0f;
}

inline uint16_t be16(const uint8_t* d, int i) { return ((uint16_t)d[i] << 8) | d[i + 1]; }

bool pmsFrameValid(const uint8_t f[PMS_FRAME_LEN]) {
  if (f[0] != 0x42 || f[1] != 0x4D || be16(f, 2) != PMS_FRAME_LEN - 4) return false;
  uint16_t sum = 0;
  for (int i = 0; i < PMS_FRAME_LEN - 2; i++) sum += f[i];
  return sum == be16(f, PMS_FRAME_LEN - 2);
}

bool pmsLooksLikeT(const uint8_t f[PMS_FRAME_LEN]) {
  return be16(f, 24) > be16(f, 22) || be16(f, 26) > be16(f, 24);
}

// Atmospheric-environment PM (words at 10..15), the same choice as the HM3301 here.
void pmsDecode(const uint8_t f[PMS_FRAME_LEN], bool isT, PmsReading &r) {
  r.pm1  = be16(f, 10);
  r.pm25 = be16(f, 12);
  r.pm10 = be16(f, 14);
  if (isT) {
    r.tempC = (int16_t)be16(f, 24) / 10.0f;
    r.rh    = be16(f, 26) / 10.0f;
  }
}

