#include "BluetoothSerial.h"
#include "esp_bt_device.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif
int Gas_analog = 4;    // used for ESP32
int Gas_digital = 2;   // used for ESP32
int vib_pin = 0; //used for ESP32
BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  Serial.println("\n---Start---");
  pinMode(Gas_digital, INPUT);
  pinMode(vib_pin,INPUT);
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
  int vibrationSensor = digitalRead(vib_pin);
  Serial.print("Gas Sensor: ");
  SerialBT.print("Gas Sensor: ");
  SerialBT.print(gassensorAnalog);
  Serial.print(gassensorAnalog);
  Serial.print("\n");
  SerialBT.print("\n");
  delay(1000);
  Serial.print("Gas Class: ");
  SerialBT.print("Gas Class: ");
  Serial.print(gassensorDigital);
  SerialBT.print(gassensorDigital);
  Serial.print("\n");
  SerialBT.print("\n");
  delay(1000);
  Serial.print("Vib Sensor: ");
  SerialBT.print("Vib Sensor: ");
  Serial.print(vibrationSensor);
  SerialBT.print(vibrationSensor);
  Serial.print("\n");
  SerialBT.print("\n");
  
    if (vibrationSensor > 0){
  Serial.println("vibration detected");
  Serial.println("/n");
  SerialBT.print("vibration detected");
  SerialBT.print("/n");
  Serial.println("LatLog");
  SerialBT.print("LatLog");
  delay(1000);
 }
else {
    Serial.println("No Vibration");
    Serial.println("/n");
    SerialBT.print("No vibration");
    SerialBT.print("/n");
      delay(100);
  }
  if (gassensorAnalog > 1000) {
    Serial.println("Gas");
    Serial.println("/n");
    SerialBT.print("Gas leakage");
    SerialBT.print("/n");
    Serial.println("LatLog");
    SerialBT.print("LatLog");
    delay(1000);
  }
  else {
    Serial.println("No Gas");
    Serial.println("/n");
    SerialBT.print("No Gas");
    SerialBT.print("/n");
    delay(100);
  }
}  
