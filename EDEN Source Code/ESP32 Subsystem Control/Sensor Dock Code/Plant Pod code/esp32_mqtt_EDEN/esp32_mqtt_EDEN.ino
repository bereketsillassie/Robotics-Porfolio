#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_AM2320.h>
#include <LiquidCrystal_I2C.h>
#include <hp_BH1750.h>
#include "Adafruit_seesaw.h"


// WiFi credentials
const char* ssid = "Linksys08736";         
const char* password = "kbygr7ycna";       

// MQTT server details
const char* mqtt_server = "192.168.1.126";  
const int mqtt_port = 1883;                 

WiFiClient espClient;
PubSubClient client(espClient);

// Define MQTT topic
const char* topic = "plantPod1/data"; // Change for diff pods

// Initialize sensors
Adafruit_AM2320 am2320 = Adafruit_AM2320();
hp_BH1750 lightMeter;
LiquidCrystal_I2C lcd(0x27, 16, 2); 
const int moistureSensorPin = 32;  // Pin 32 for the esp
int moisturePercent;


unsigned long lastUpdate = 0; // Tracks the last time the display was updated
int currentScreen = 0; // Tracks the current screen (0 = Temp/Humidity, 1 = Lux)


unsigned long lastPublishTime = 0;
const int publishInterval = 5000; // Publish every 5 seconds

const int minMoisture = 3531;  // Need to calibrate between sensors
const int maxMoisture = 1753;  // Same here


// Function prototypes
void setupWiFi();
void reconnect();
void publishSensorData();

void setup() {
  Serial.begin(115200);
  
  // Initialize WiFi
  setupWiFi();
  
  // Initialize MQTT
  client.setServer(mqtt_server, mqtt_port);
  pinMode(moistureSensorPin, INPUT);



  Serial.println("Scanning I2C...");
  Wire.begin();
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      Serial.println(address, HEX);
    }
  }
  Serial.println("I2C scan complete.");


  // Initialize AM2320
  if (!am2320.begin()) {
    Serial.println("Failed to initialize AM2320!");
     
  }

  // Initialize BH1750
  if (!lightMeter.begin(0x23, &Wire)) { 
    Serial.println("Failed to initialize BH1750!");
    
  }

  pinMode(moistureSensorPin, INPUT);


  // Initialize LCD
  lcd.init();      // Initialize LCD
  lcd.clear();     // Clear LCD screen
  lcd.backlight(); // Turn on the LCD backlight
  lcd.setCursor(0, 0);
  lcd.print("Initializing...");
  delay(1500);
}

void loop() {
  // Reconnect if needed
  if (!client.connected()) {
    reconnect();
  }
  
  lightMeter.start();

  // Read data from AM2320
  float temperature = am2320.readTemperature();
  float humidity = am2320.readHumidity();
  

  // Read data from BH1750
  float lightLevel = lightMeter.getLux();

  // Read data from Soil Sensor
  int rawMoisture = analogRead(moistureSensorPin);
  moisturePercent = map(rawMoisture, minMoisture, maxMoisture, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);

  // Check if it's time to update the screen
  if (millis() - lastUpdate >= 3000) { // Update every 3 seconds
    lastUpdate = millis(); // Reset the timer
    currentScreen = (currentScreen + 1) % 2; // Toggle between 0 and 1 fro different screens

    lcd.clear(); // Clear the screen for new content

    if (currentScreen == 0) {
      // Display temperature and humidity
      if (isnan(temperature) || isnan(humidity)) {
        lcd.setCursor(0, 0);
        lcd.print("AM2320 Error!");
      } else {
        lcd.setCursor(0, 0);
        lcd.print("Temp: ");
        lcd.print(temperature);
        lcd.print(" C");

        lcd.setCursor(0, 1);
        lcd.print("Hum: ");
        lcd.print(humidity);
        lcd.print("%");
      }
    } else if (currentScreen == 1) {
      // Display lux
      if (lightLevel < 0) {
        lcd.setCursor(0, 0);
        lcd.print("BH1750 Error!");
      } else {
        lcd.setCursor(0, 0);
        lcd.print("Light: ");
        lcd.print(lightLevel);
        lcd.print(" lux");

        lcd.setCursor(0, 1);
        lcd.print("Moist: ");
        lcd.print(moisturePercent);
        //Serial.println(rawMoisture);
        lcd.print(" %");
      }
    }
  }
  


  // Handle MQTT
  client.loop();

  // Publish sensor data every 5 seconds
  if (millis() - lastPublishTime >= publishInterval) {
    lastPublishTime = millis();
    publishSensorData();
  }
  
}

void setupWiFi() {
  Serial.print("Connecting to ");
  Serial.print(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("ESP32ClientPP1")) {  // Change for diff pods
      Serial.println("Connected to MQTT Broker");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Trying again in 5 seconds...");
      delay(5000);
    }
  }

  client.loop(); 
}

void publishSensorData() {
  // Create a JSON document for pi interface
  StaticJsonDocument<256> doc;

  float lux = lightMeter.getLux();
  float roundedLux = roundToDecimalPlaces(lux, 1);
  
  // Use actual sensor readings
  doc["light"] = roundedLux;
  doc["temperature"] = am2320.readTemperature();
  doc["humidity"] = am2320.readHumidity();
  doc["moisture"] = moisturePercent;

  // Convert JSON to string
  char buffer[256];
  serializeJson(doc, buffer);

  // Publish to MQTT topic
  if (client.publish(topic, buffer)) {
    Serial.print("Published: ");
    Serial.println(buffer);
  } else {
    Serial.println("Failed to publish message");
  }
}


float roundToDecimalPlaces(float value, int decimalPlaces) {
  float factor = pow(10, decimalPlaces);
  return round(value * factor) / factor;
}


