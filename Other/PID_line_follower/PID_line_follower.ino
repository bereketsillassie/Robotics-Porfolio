#include <QTRSensors.h>


// Sensor and motor configuration
#define NUM_SENSORS 5
#define TIMEOUT 2500
#define EMITTER_PIN 2


QTRSensorsRC qtrrc((unsigned char[]){ 3, 4, 5, 6, 7 }, NUM_SENSORS, TIMEOUT);
unsigned int sensorValues[NUM_SENSORS];


// PID constants
float Kp = 4;
float Ki = 0.0;
float Kd = 2.0;

// PID variables
float error = 0, lastError = 0, integral = 0;

// Motor pins
#define ENA 11
#define IN1 12
#define IN2 13
#define ENB 10
#define IN3 8
#define IN4 9

// Base motor speed
int baseSpeed = 150;

void setup() {
  // Initialize motors
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Initialize serial monitor
  Serial.begin(9600);

  // Calibrate the sensors
  Serial.println("Calibrating...");
  for (int i = 0; i < 400; i++) {
    qtrrc.calibrate();
    delay(20);
  }
  Serial.println("Calibration complete.");
}



void loop() {
  // Read sensor values 
  int position = qtrrc.readLine(sensorValues);
  
  // Calculate error (desired position = 3500)
  error = position - 3500;
  
  // PID calculations
  integral += error;
  float derivative = error - lastError;
  float correction = Kp * error + Ki * integral + Kd * derivative;

  // Adjust motor speeds
  int leftSpeed = baseSpeed + correction;
  int rightSpeed = baseSpeed - correction;

  // Constrain motor speeds
  leftSpeed = constrain(leftSpeed, 0, 255);
  rightSpeed = constrain(rightSpeed, 0, 255);

  // Drive the motors
  driveMotors(leftSpeed, rightSpeed);

  // Update the last error
  lastError = error;

  delay(10);
}

void driveMotors(int leftSpeed, int rightSpeed) {
  // Left motor
  if (leftSpeed > 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, leftSpeed);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, -leftSpeed);
  }


  // Right motor
  if (rightSpeed > 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, rightSpeed);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, -rightSpeed);
  }
}