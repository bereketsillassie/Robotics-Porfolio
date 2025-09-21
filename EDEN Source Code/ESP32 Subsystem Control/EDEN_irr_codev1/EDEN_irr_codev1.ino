#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi and MQTT Broker settings
const char* ssid = "Linksys08736";
const char* password = "kbygr7ycna";

// MQTT server details
const char* mqttServer = "192.168.1.126";
const int mqttPort = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// Define MQTT topic
const char* MQTT_PUMP_CMD = "pump/ctl";
const char* MQTT_SOL_CMD = "sol/ctl";
const char* MQTT_GANTRY_CMD = "gantry/ctl";

// pump pin
#define pump_pin 23
//Solenoid pins
#define T_sol_pin 22
#define B_sol_pin 21
// Gantry control pins
#define T_ganDIR_pin 33
#define T_ganPUL_pin 32
#define B_ganDIR_pin 25
#define B_ganPUL_pin 26

#define TR_LS_pin 19
#define TL_LS_pin 18
#define BR_LS_pin 17
#define BL_LS_pin 16

const int stepDelay = 800; 
bool direction = HIGH;     

String T_gant = "";
String B_gant = "";
bool curr_TR_state;
bool curr_TL_state;
bool curr_BR_state;
bool curr_BL_state;


void callback(char* topic, byte* payload, unsigned int length) {

  Serial.println("Message here");
  Serial.println(topic);
  if (strcmp(topic, MQTT_PUMP_CMD) == 0){
    String pump_message = "";
    for (int i = 0; i < length; i++) {
      pump_message += (char)payload[i];
    }
    Serial.println("Received pump message: " + pump_message);


    if(pump_message == "True")
      digitalWrite(pump_pin, HIGH);
    else{
      digitalWrite(pump_pin, LOW);
    }
  }

  if (strcmp(topic, MQTT_SOL_CMD) == 0){
    String sol_message = "";
    for (int i = 0; i < length; i++) {
      sol_message += (char)payload[i];
    }
    Serial.println("Received solenoid message: " + sol_message);


    // Split the sol_message string into two values
    int spaceIndex = sol_message.indexOf(' '); // Find space between values
    if (spaceIndex == -1) {
      Serial.println("Error: Invalid solenoid message format");
      return;
    }
    String T_sol = sol_message.substring(0, spaceIndex);
    String B_sol = sol_message.substring(spaceIndex + 1);


    Serial.println(T_sol + " ");

    if(T_sol == "True")
      digitalWrite(T_sol_pin, HIGH);
    else{
      digitalWrite(T_sol_pin, LOW);
    }

    if(B_sol == "True")
      digitalWrite(B_sol_pin, HIGH);
    else{
      digitalWrite(B_sol_pin, LOW);
    }

  }



  if (strcmp(topic, MQTT_GANTRY_CMD) == 0){
    String gant_message = "";
    for (int i = 0; i < length; i++) {
      gant_message += (char)payload[i];
    }
    Serial.println("Received gantry message: " + gant_message);

    
    
    int spaceIndex = gant_message.indexOf(' '); // Find space between values
    if (spaceIndex == -1) {
      Serial.println("Error: Invalid gantry message format");
      return;
    }
    T_gant = gant_message.substring(0, spaceIndex);
    B_gant = gant_message.substring(spaceIndex + 1);

    
  }

}

void setGantry(){

}


void reconnectWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Reconnecting to WiFi...");
    WiFi.disconnect();
    WiFi.reconnect();
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\nWiFi reconnected!");
    } else {
      Serial.println("\nFailed to reconnect to WiFi");
    }
  }
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.println("Reconnecting to MQTT...");
    if (client.connect("ESP32_Client2")) {
      Serial.println("Connected to MQTT");
      client.subscribe(MQTT_PUMP_CMD);
      client.subscribe(MQTT_SOL_CMD);
      client.subscribe(MQTT_GANTRY_CMD);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}


void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP32_Client2")) {
      Serial.println("Connected to MQTT");
      client.subscribe(MQTT_PUMP_CMD);
      client.subscribe(MQTT_SOL_CMD);
      client.subscribe(MQTT_GANTRY_CMD);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds");
      delay(5000);
    }
  }
  

  /*
     const int pump_pin = 23;
    //Solenoid pins
    const int T_sol_pin = 22; 
    const int B_sol_pin = 21;
    // Gantry control pins
    const int T_ganDIR_pin = 33;
    const int T_ganPUL_pin = 32;
    const int B_ganDIR_pin = 34;
    const int B_ganPUL_pin = 35;

    const int TR_LS_pin = 19;
    const int TL_LS_pin = 18;
    const int TR_LS_pin = 17;
    const int TL_LS_pin = 16;
  */

  pinMode(pump_pin, OUTPUT);
  pinMode(T_sol_pin, OUTPUT);
  pinMode(B_sol_pin, OUTPUT);
  pinMode(T_ganDIR_pin, OUTPUT);
  pinMode(T_ganPUL_pin, OUTPUT);
  pinMode(B_ganDIR_pin, OUTPUT);
  pinMode(B_ganPUL_pin, OUTPUT);
  pinMode(TR_LS_pin, INPUT_PULLUP);
  pinMode(TL_LS_pin, INPUT_PULLUP);
  pinMode(BR_LS_pin, INPUT_PULLUP);
  pinMode(BL_LS_pin, INPUT_PULLUP);


  digitalWrite(B_ganPUL_pin, LOW);
  digitalWrite(B_ganPUL_pin, LOW);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();  // Process incoming messages



  curr_TR_state = digitalRead(TR_LS_pin);
  curr_TL_state = digitalRead(TL_LS_pin);
  curr_BR_state = digitalRead(BR_LS_pin);
  curr_BL_state = digitalRead(BL_LS_pin);




  if (T_gant == "STOP" && B_gant == "STOP"){
    digitalWrite(T_ganPUL_pin, LOW);
    digitalWrite(B_ganPUL_pin, LOW);
    delayMicroseconds(stepDelay);
  } 
  else{
    // TOP GANTRY CONTROL (Left = True  |  Right = False)
    if (T_gant == "True"){
      digitalWrite(T_ganDIR_pin, HIGH);
      if(curr_TR_state != LOW){
        digitalWrite(T_ganPUL_pin, HIGH);
        delayMicroseconds(stepDelay);
        digitalWrite(T_ganPUL_pin, LOW);
        delayMicroseconds(stepDelay);
        curr_TR_state = digitalRead(TR_LS_pin);
      }
    }


    if (T_gant == "False"){
      digitalWrite(T_ganDIR_pin, LOW);
      if(curr_TL_state != LOW){
        digitalWrite(T_ganPUL_pin, HIGH);
        delayMicroseconds(stepDelay);
        digitalWrite(T_ganPUL_pin, LOW);
        delayMicroseconds(stepDelay);
        curr_TL_state = digitalRead(TL_LS_pin);
      }
    }


    // BOTTOM Gantry Control
    if (B_gant == "True"){
      digitalWrite(B_ganDIR_pin, HIGH);
      if(curr_BR_state != LOW){
        digitalWrite(B_ganPUL_pin, HIGH);
        delayMicroseconds(stepDelay);
        digitalWrite(B_ganPUL_pin, LOW);
        delayMicroseconds(stepDelay);
        curr_BR_state = digitalRead(BR_LS_pin);
      }
    }


    if (B_gant == "False"){
      digitalWrite(B_ganDIR_pin, LOW);
      if(curr_BL_state != LOW){
        digitalWrite(B_ganPUL_pin, HIGH);
        delayMicroseconds(stepDelay);
        digitalWrite(B_ganPUL_pin, LOW);
        delayMicroseconds(stepDelay);
        curr_BL_state = digitalRead(BL_LS_pin);
      }
    }


    digitalWrite(T_ganPUL_pin, LOW);
    digitalWrite(B_ganPUL_pin, LOW);
  }

}






