#include "DHT.h"
#include "HX711.h"

//Pins
// Front lift cell
const int DOUT1 = 2;
const int SCK1 = 3;

// Front grad cell
const int DOUT2 = 4;
const int SCK2 = 5;

// Back lift cell
const int DOUT3 = 6;
const int SCK3 =  7;

// Back drag cell
const int DOUT4 = 8;
const int SCK4 =  9;

const int PT = A2; // Pitot tube
const int DS = 12; // Density sensor

// Constants
const float Vcc = 5.0; // voltage supplied to the pitot tube
const float ADC_RES = 1023.0; // 10-bit ADC
const float P_max = 2.0; // kPa (sensor range)
const float V_offset = 0.5; // NEED TO CALIBRATE LATER. Voltage at 0 differential pressure
const float sensitivity = 1.0; // kPa per 1V (from datasheet)
const float atm_pressure = 101325; // Assume standard atmospheric pressure in Pascals
float pressure0;

// HX711 instances
HX711 scale1;
HX711 scale2;
HX711 scale3;
HX711 scale4;

DHT dht(DS, DHT11); // DHT11 air density sensor

void setup() {
  Serial.begin(9600);

  // Initialize each scale with unique DOUT and SCK
  scale1.begin(DOUT1, SCK1);
  scale2.begin(DOUT2, SCK2);
  scale3.begin(DOUT3, SCK3);
  scale4.begin(DOUT4, SCK4);

  // Initialize sensors
  dht.begin();

  delay(1000);

  // Collibrations
  scale1.tare();
  scale2.tare();
  scale3.tare();
  scale4.tare();
}

void loop() {

  // Collect data from the load cells
  long f1 = 0, f2 = 0, f3 = 0, f4 = 0;

  if (scale1.is_ready()) f1 = scale1.get_units();
  if (scale2.is_ready()) f2 = scale2.get_units();
  if (scale3.is_ready()) f3 = scale3.get_units();
  if (scale4.is_ready()) f4 = scale4.get_units();
  
  // Collect data from the sensors
  int adcValue = analogRead(PT);
  float voltage = (adcValue / ADC_RES) * Vcc;
  float pressure_Pa = (voltage - V_offset) * (P_max / (Vcc - 2 * V_offset)) * 1000.0; // Convert voltage to pressure in kPa
  if (pressure0) {pressure_Pa -= pressure0;}
  else {pressure0 = pressure_Pa;}
  float dynamicPressure = max(pressure_Pa, 0.0);

  float temperature = dht.readTemperature(); // Celsius
  float temperatureK = temperature + 273.15;
  float density = (atm_pressure - dynamicPressure) / (287.05 * temperatureK);

  float windSpeed = sqrt((2.0 * dynamicPressure) / density); // Calculate wind speed (Bernoulli)

  // String output = wind_velocity + " " + density + " " + f1 + " " + f2 + " " + f3 + " " + f4;
  Serial.print(windSpeed); Serial.print("\t");
  Serial.print(density); Serial.print("\t");
  Serial.print(f1); Serial.print("\t");
  Serial.print(f2); Serial.print("\t");
  Serial.print(f3); Serial.print("\t");
  Serial.println(f4);

  delay(50);
}
