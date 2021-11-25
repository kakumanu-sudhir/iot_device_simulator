#include "BluetoothSerial.h"
#include "esp_bt_device.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif
int Gas_analog = 4;    // used for ESP32
int Gas_digital = 2;   // used for ESP32
BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  Serial.println("\n---Start---");
  pinMode(Gas_digital, INPUT);
  SerialBT.begin("ESP32test"); //Bluetooth device name
  
  Serial.println("The device started, now you can pair it with bluetooth!");
  Serial.println("Device Name: ESP32test");
  Serial.print("BT MAC: ");
  //printDeviceAddress();
  Serial.println("hai");
}

void loop() {
  int gassensorAnalog = analogRead(Gas_analog);
  int gassensorDigital = digitalRead(Gas_digital);

  Serial.print("Gas Sensor: ");
  SerialBT.print("Gas Sensor: ");
   SerialBT.print(gassensorAnalog);
  Serial.print(gassensorAnalog);
  Serial.print("\t");
  SerialBT.print("\t");
  Serial.print("Gas Class: ");
  SerialBT.print("Gas Class: ");
  Serial.print(gassensorDigital);
  SerialBT.print(gassensorDigital);
  Serial.print("\t");
  SerialBT.print("\t");
  Serial.print("\t");
  SerialBT.print("\t");
  
  if (gassensorAnalog > 1000) {
    Serial.println("Gas");
    SerialBT.print("Gas leakage");
    SerialBT.print("/n");
    SerialBT.print("LatLog");
    delay(1000);
  }
  else {
    Serial.println("No Gas");
    SerialBT.print("No Gas");
  }
  delay(100);
}
