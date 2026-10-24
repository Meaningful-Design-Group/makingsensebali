// Checks diy_node_v5/decoders.h on a laptop, against the datasheets' own
// examples and hand-built Plantower frames. CI runs it before compiling:
//   c++ -std=c++17 -Wall -o /tmp/decoders_test test/decoders_test.cpp && /tmp/decoders_test
#include "../diy_node_v5/decoders.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static bool near(float a, float b, float tol) { return fabsf(a - b) <= tol; }

// A frame with these 13 data words, length 28 and a correct checksum.
static void frame(uint8_t f[PMS_FRAME_LEN], const uint16_t words[13]) {
  f[0] = 0x42; f[1] = 0x4D; f[2] = 0; f[3] = 28;
  for (int i = 0; i < 13; i++) { f[4 + 2 * i] = words[i] >> 8; f[5 + 2 * i] = words[i] & 0xFF; }
  uint16_t sum = 0;
  for (int i = 0; i < PMS_FRAME_LEN - 2; i++) sum += f[i];
  f[30] = sum >> 8; f[31] = sum & 0xFF;
}

int main() {
  // Sensirion CRC-8: the example every Sensirion datasheet gives, 0xBEEF -> 0x92.
  const uint8_t beef[2] = {0xBE, 0xEF};
  assert(sensirionCrc(beef, 2) == 0x92);

  // SCD4x datasheet, read_measurement example: 500 ppm, 25 °C, 37 %RH.
  const uint16_t scdWords[3] = {0x01F4, 0x6667, 0x5EB9};
  Scd4xReading scd;
  scd4xDecode(scdWords, scd);
  assert(scd.co2 == 500.0f && near(scd.tempC, 25.0f, 0.01f) && near(scd.rh, 37.0f, 0.01f));
  const uint16_t scdZero[3] = {0, 0x6667, 0x5EB9};
  scd4xDecode(scdZero, scd);
  assert(isnan(scd.co2));   // 0 ppm is not a reading

  // SHT4x conversion; RH clamps to 0..100 at the ends.
  float t, rh;
  const uint16_t sht[2] = {0x6666, 0x8000};
  sht4xDecode(sht, t, rh);
  assert(near(t, 25.0f, 0.01f) && near(rh, 56.5f, 0.01f));
  const uint16_t shtEnds[2] = {0, 0xFFFF};
  sht4xDecode(shtEnds, t, rh);
  assert(near(t, -45.0f, 0.01f) && rh == 100.0f);
  const uint16_t shtLow[2] = {0x6666, 0};
  sht4xDecode(shtLow, t, rh);
  assert(rh == 0.0f);

  // PMS5003: std PM 1/2.5/10, atm PM 1/2.5/10, counts >0.3 .. >10 um, reserved.
  uint8_t f[PMS_FRAME_LEN];
  const uint16_t plain[13] = {11, 18, 22, 9, 15, 20, 2100, 640, 120, 14, 3, 1, 0};
  frame(f, plain);
  assert(pmsFrameValid(f));
  assert(!pmsLooksLikeT(f));
  PmsReading pms;
  pmsDecode(f, false, pms);
  assert(pms.pm1 == 9 && pms.pm25 == 15 && pms.pm10 == 20);   // atmospheric, not CF=1
  assert(isnan(pms.tempC) && isnan(pms.rh));

  // Clean air: every count above 2.5 um at zero is still a plain PMS5003.
  const uint16_t clean[13] = {0, 0, 0, 0, 0, 0, 90, 20, 0, 0, 0, 0, 0};
  frame(f, clean);
  assert(pmsFrameValid(f) && !pmsLooksLikeT(f));

  // PMS5003T: 28.5 °C and 75.0 %RH where the 5 and 10 um counts would be.
  const uint16_t tee[13] = {11, 18, 22, 9, 15, 20, 2100, 640, 120, 14, 285, 750, 0};
  frame(f, tee);
  assert(pmsFrameValid(f) && pmsLooksLikeT(f));
  pmsDecode(f, true, pms);
  assert(pms.pm25 == 15 && near(pms.tempC, 28.5f, 0.001f) && near(pms.rh, 75.0f, 0.001f));

  // A T below zero is a negative int16.
  const uint16_t cold[13] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xFFF6, 300, 0};
  frame(f, cold);
  pmsDecode(f, true, pms);
  assert(near(pms.tempC, -1.0f, 0.001f));

  // Corruption: one flipped byte, or a frame length that is not 28 (a PMS5003ST is 36).
  frame(f, plain);
  f[13] ^= 0x01;
  assert(!pmsFrameValid(f));
  frame(f, plain);
  f[3] = 36;
  assert(!pmsFrameValid(f));

  puts("decoders: all checks passed");
  return 0;
}
