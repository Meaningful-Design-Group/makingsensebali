// Pure alarm logic for Bayu v6: numbers in, state out. No Arduino calls, so
// test/alarms_test.cpp compiles this same file on a laptop. The thresholds
// themselves are constants at the top of diy_node_v6.ino.
#pragma once
#include <math.h>
#include <stdint.h>

// ISPU category of a PM2.5 value against the four upper breakpoints
// {Baik, Sedang, Tidak Sehat, Sangat Tidak Sehat}: 0 Baik .. 4 Berbahaya,
// -1 when there is no value.
inline int8_t ispuCategory(float pm25, const float upper[4]) {
  if (isnan(pm25)) return -1;
  for (int8_t i = 0; i < 4; i++)
    if (pm25 <= upper[i]) return i;
  return 4;
}

// An alarm that switches on at once and off only after `clearable` has held
// for holdMs without a break (hysteresis in level and in time).
struct Alarm { bool active = false; uint32_t clearSince = 0; };

// Returns true when the alarm changed state. `now` is millis().
inline bool stepAlarm(Alarm &a, bool above, bool clearable, uint32_t now, uint32_t holdMs) {
  if (above) {
    a.clearSince = 0;
    if (a.active) return false;
    a.active = true;
    return true;
  }
  if (!a.active) return false;
  if (!clearable) { a.clearSince = 0; return false; }
  if (!a.clearSince) { a.clearSince = now ? now : 1; return false; }
  if (now - a.clearSince < holdMs) return false;
  a.active = false;
  a.clearSince = 0;
  return true;
}

// Mean of the values in a ring that are not NAN; NAN with fewer than minN.
inline float ringMean(const float* ring, uint8_t len, uint8_t minN) {
  float sum = 0;
  uint8_t n = 0;
  for (uint8_t i = 0; i < len; i++)
    if (!isnan(ring[i])) { sum += ring[i]; n++; }
  return n >= minN ? sum / n : NAN;
}
