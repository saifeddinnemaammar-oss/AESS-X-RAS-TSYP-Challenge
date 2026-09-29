/*
Writer Robot: Hardware Actuation Node
Listens to Serial commands from Raspberry Pi and triggers motors/servos.
*/

#include <ESP32Servo.h>

// --- PIN DEFINITIONS ---
// Motor A (Left Tracks)
const int ENA = 14; 
const int IN1 = 27; 
const int IN2 = 26;

// Motor B (Right Tracks)
const int ENB = 32;
const int IN3 = 25;
const int IN4 = 33;

// Beacon Payload Mechanism
const int SERVO_PIN = 18;
Servo dropServo;

void setup() {
  Serial.begin(115200);
  
  // Initialize Motor Pins
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  
  // Initialize Servo
  dropServo.attach(SERVO_PIN);
  dropServo.write(90); // Locked position
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); 
    
    if (command.startsWith("DRIVE")) {
      // In production, parse X,Y and use encoders/PID to move exactly.
      // For now, we trigger a standard movement sequence.
      executeDriveSequence();
      Serial.println("ACK");
    } 
    else if (command == "DROP_BEACON") {
      actuatePayloadBay();
      Serial.println("ACK");
    } 
    else {
      Serial.println("ERR_UNKNOWN");
    }
  }
}

void executeDriveSequence() {
  // Move Forward
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  analogWrite(ENA, 200); analogWrite(ENB, 200);
  delay(1500); 
  
  // Stop
  analogWrite(ENA, 0); analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN3, LOW);
}

void actuatePayloadBay() {
  dropServo.write(0);   // Open latch
  delay(800);           // Allow physical beacon to fall
  dropServo.write(90);  // Close latch
}