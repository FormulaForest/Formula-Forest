#include "DHT.h"
#include "HX711.h"

// ----------------- Pins -----------------
// Front lift cell
const int DOUT1 = 2;
const int SCK1 = 3;

// Front drag cell
const int DOUT2 = 4;
const int SCK2 = 5;

// Back lift cell
const int DOUT3 = 6;
const int SCK3 = 7;

// Back drag cell
const int DOUT4 = 8;
const int SCK4 = 9;

const int PT = A2; // Pitot tube analog pin
const int DS = 12; // DHT11 pin

// ----------------- Constants -----------------
const float Vcc = 5.0;        // Voltage supplied to pitot tube
const float ADC_RES = 1023.0; // 10-bit ADC
const float P_max = 2.0;      // kPa sensor range
const float V_offset = 0.5;   // Voltage at 0 pressure (calibrate later)
const float atm_pressure = 101325; // Pa
float pressure0 = 0;          // Baseline offset

// ----------------- HX711 instances -----------------
HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;

// ----------------- DHT11 instance -----------------
DHT dht(DS, DHT11);

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("✅ Arduino setup started...");

  // Initialize load cells
  scale1.begin(DOUT1, SCK1);
  scale2.begin(DOUT2, SCK2);
  scale3.begin(DOUT3, SCK3);
  scale4.begin(DOUT4, SCK4);

  // Initialize DHT11
  dht.begin();
  delay(1000);

  // Tare (zero) load cells
  scale1.tare();
  scale2.tare();
  scale3.tare();
  scale4.tare();

  Serial.println("✅ Sensors initialized");
  Serial.println("WindSpeed(m/s),Density(kg/m^3),Load1,Load2,Load3,Load4,Temperature(C)");
}

void loop() {
  // -------- Load cells --------
  float f1 = 0, f2 = 0, f3 = 0, f4 = 0;
  if (scale1.is_ready()) f1 = scale1.get_units();
  if (scale2.is_ready()) f2 = scale2.get_units();
  if (scale3.is_ready()) f3 = scale3.get_units();
  if (scale4.is_ready()) f4 = scale4.get_units();

  // -------- Pitot tube --------
  int adcValue = analogRead(PT);
  float voltage = (adcValue / ADC_RES) * Vcc;

  // Convert to pressure (Pa)
  float pressure_Pa = (voltage - V_offset) * (P_max / (Vcc - 2 * V_offset)) * 1000.0;
  if (pressure0) {
    pressure_Pa -= pressure0; // zero offset
  } else {
    pressure0 = pressure_Pa;
  }
  float dynamicPressure = max(pressure_Pa, 0.0);

  // -------- DHT11 --------
  float temperature = dht.readTemperature(); // °C
  if (isnan(temperature)) {
    temperature = -99; // fallback value
    Serial.println("⚠️ DHT11 read failed!");
  }

  float temperatureK = temperature + 273.15;
  float density = (atm_pressure - dynamicPressure) / (287.05 * temperatureK);

  // -------- Wind speed --------
  float windSpeed = sqrt((2.0 * dynamicPressure) / density);

  // -------- Print as CSV --------
  Serial.print(windSpeed, 2); Serial.print(",");
  Serial.print(density, 3);   Serial.print(",");
  Serial.print(f1, 2);        Serial.print(",");
  Serial.print(f2, 2);        Serial.print(",");
  Serial.print(f3, 2);        Serial.print(",");
  Serial.print(f4, 2);        Serial.print(",");
  Serial.println(temperature, 1);

  delay(500); // update rate
}
