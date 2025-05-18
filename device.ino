#include <math.h>
#include <time>

float calculatePressure(float resistance_kOhm) {
  float numerator = 1652.067;
  float exponent = 1.0 / 0.647;
  float pressure = pow(numerator / (resistance_kOhm + 0.611), exponent);
  return pressure;
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  // 模擬輸入電阻值，例如 10 kΩ
  float inputResistance = 10.0;
  float pressure = calculatePressure(inputResistance);

  Serial.print("輸入電阻：");
  Serial.print(inputResistance);
  Serial.print(" kΩ，估算壓力：約 ");
  Serial.print(pressure);
  Serial.println(" g");

  delay(3000);
}
