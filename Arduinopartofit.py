
git clone https://github.com/BlackBrix/Arduino-Frequency-Counter-Library

#include <FreqCount.h>

void setup() {
  Serial.begin(115200);
  while (!Serial);  // wait for Serial (Micro/Leonardo)

  // Start counting pulses, gate time = 1 second
  FreqCount.begin(1000);
}

void loop() {
  if (FreqCount.available()) {
    unsigned long count = FreqCount.read(); // number of pulses in last 1 second
    Serial.println(count);                  // send frequency over Serial to Raspberry Pi
  }
}