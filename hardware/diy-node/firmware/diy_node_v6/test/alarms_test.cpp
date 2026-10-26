// c++ -std=c++17 -Wall -Wextra -o /tmp/alarms_test alarms_test.cpp && /tmp/alarms_test
// Checks the v6 alarm logic against the ISPU breakpoints (Permen LHK P.14/2020).
// Lives in test/, which the Arduino build does not compile.
#include <assert.h>
#include <stdio.h>
#include "../alarms.h"

int main() {
  const float bp[4] = {15.5f, 55.4f, 150.4f, 250.4f};
  assert(ispuCategory(NAN, bp) == -1);
  assert(ispuCategory(0, bp) == 0);
  assert(ispuCategory(15.5f, bp) == 0);
  assert(ispuCategory(15.6f, bp) == 1);
  assert(ispuCategory(55.4f, bp) == 1);
  assert(ispuCategory(55.5f, bp) == 2);
  assert(ispuCategory(250.4f, bp) == 3);
  assert(ispuCategory(250.5f, bp) == 4);

  const uint32_t hold = 5 * 60 * 1000;
  Alarm a;
  assert(!stepAlarm(a, false, true, 1000, hold) && !a.active);   // nothing to clear
  assert(stepAlarm(a, true, false, 2000, hold) && a.active);     // on at once
  assert(!stepAlarm(a, false, false, 3000, hold) && a.active);   // in the band: stays on
  assert(!stepAlarm(a, false, true, 4000, hold) && a.active);    // below: clock starts
  assert(!stepAlarm(a, false, true, 4000 + hold - 1, hold) && a.active);
  assert(!stepAlarm(a, false, false, 4000 + hold, hold) && a.active);   // back in the band: clock resets
  assert(!stepAlarm(a, false, true, 10000000, hold) && a.active);
  assert(stepAlarm(a, false, true, 10000000 + hold, hold) && !a.active); // 5 min below: off

  float ring[4] = {NAN, NAN, NAN, NAN};
  assert(isnan(ringMean(ring, 4, 2)));
  ring[0] = 10; assert(isnan(ringMean(ring, 4, 2)));
  ring[2] = 20; assert(ringMean(ring, 4, 2) == 15);
  puts("alarms_test: ok");
  return 0;
}
