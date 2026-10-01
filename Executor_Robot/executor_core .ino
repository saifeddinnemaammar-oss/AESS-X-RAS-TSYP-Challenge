#include <SPI.h>
#include <LoRa.h>
#include <ESP32Servo.h>
#include <RPLidar.h>

// --- PIN DEFINITIONS ---
const int csPin = 5;
const int resetPin = 14;
const int irqPin = 26;

const int SERVO_PIN = 18;
const int PUMP_RELAY_PIN = 19;

const int ENA = 14; const int IN1 = 27; const int IN2 = 26;
const int ENB = 32; const int IN3 = 25; const int IN4 = 33;

const int LIDAR_RX = 16;
const int LIDAR_TX = 17;
const int LIDAR_PWM = 21; 

RPLidar lidar;
Servo payloadServo;

// --- 20-BYTE PACKET STRUCTURE ---
struct __attribute__((packed)) BeaconPacket {
  uint16_t beacon_id;
  uint8_t writer_id;
  uint8_t event_type; 
  int16_t x;
  int16_t y;
  int8_t z;
  uint32_t timestamp;
  uint16_t ttl;
  uint8_t confidence;
  uint16_t previous_beacon;
  uint16_t crc16;
};

// CRC16 implementation for data integrity
uint16_t calculateCRC(uint8_t *data, size_t len) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i] << 8;
    for (uint8_t j = 0; j < 8; j++) {
      crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : crc << 1;
    }
  }
  return crc;
}

// --- STATE MACHINE ---
enum SystemState { STATE_BOOT, STATE_BRIEFING, STATE_NAVIGATING, STATE_ACTING, STATE_DONE };
SystemState currentState = STATE_BOOT;

struct HazardTarget {
  uint8_t beacon_id;
  uint8_t hazard_type; 
  bool completed;
};

HazardTarget missionTargets[5];
int targetCount = 0;
int currentTargetIndex = -1;

void setup() {
  Serial.begin(115200);
  
  // Setup RPLiDAR
  Serial2.begin(115200, SERIAL_8N1, LIDAR_RX, LIDAR_TX);
  lidar.begin(Serial2);
  pinMode(LIDAR_PWM, OUTPUT);
  analogWrite(LIDAR_PWM, 255);
  
  // Actuators & Motors
  payloadServo.attach(SERVO_PIN);
  payloadServo.write(90); 
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  digitalWrite(PUMP_RELAY_PIN, LOW); 
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  
  // LoRa
  LoRa.setPins(csPin, resetPin, irqPin);
  if (!LoRa.begin(868E6)) {
    Serial.println("[ERR] LoRa Radio failed");
    while (true);
  }
  
  Serial.println("[SYS] Executor Ready. Awaiting LoRa Briefing...");
  currentState = STATE_BRIEFING;
}

void loop() {
  switch (currentState) {
    case STATE_BRIEFING:
      receiveMissionBriefing();
      break;
    case STATE_NAVIGATING:
      if (selectNextPriorityTarget()) {
        homeToBeacon(missionTargets[currentTargetIndex].beacon_id);
      } else {
        Serial.println("[MISSION] All targets complete.");
        analogWrite(LIDAR_PWM, 0); 
        currentState = STATE_DONE;
      }
      break;
    case STATE_ACTING:
      executeHardwareAction(missionTargets[currentTargetIndex].hazard_type);
      missionTargets[currentTargetIndex].completed = true;
      currentState = STATE_NAVIGATING;
      break;
    case STATE_DONE:
      stopMotors();
      delay(1000);
      break;
  }
}

void receiveMissionBriefing() {
  int packetSize = LoRa.parsePacket();
  if (packetSize == sizeof(BeaconPacket)) {
    BeaconPacket receivedPacket;
    LoRa.readBytes((uint8_t*)&receivedPacket, sizeof(BeaconPacket));
    
    // Verify CRC before accepting the mission
    if (calculateCRC((uint8_t*)&receivedPacket, 18) == receivedPacket.crc16) {
      Serial.println("[NET] Valid Mission Briefing Received.");
      
      // Dynamically load the target from the parsed packet
      missionTargets[targetCount] = {
        (uint8_t)receivedPacket.beacon_id, 
        receivedPacket.event_type, 
        false
      };
      targetCount++;
      
      // Sort array by priority (1 = Victim, 2 = Fire, 3 = Gas)
      for (int i = 0; i < targetCount - 1; i++) {
        for (int j = i + 1; j < targetCount; j++) {
          if (missionTargets[j].hazard_type < missionTargets[i].hazard_type) {
            HazardTarget temp = missionTargets[i];
            missionTargets[i] = missionTargets[j];
            missionTargets[j] = temp;
          }
        }
      }
      currentState = STATE_NAVIGATING;
    }
  }
}

bool selectNextPriorityTarget() {
  for (int i = 0; i < targetCount; i++) {
    if (!missionTargets[i].completed) {
      currentTargetIndex = i;
      return true;
    }
  }
  return false;
}

void homeToBeacon(uint8_t target_id) {
  Serial.print("[NAV] Homing to Beacon: ");
  Serial.println(target_id);
  
  unsigned long navStart = millis();
  while (millis() - navStart < 6000) {
    if (IS_OK(lidar.waitPoint())) {
      float distance = lidar.getCurrentPoint().distance;
      float angle = lidar.getCurrentPoint().angle;
      
      if (distance > 0 && distance < 400 && (angle < 45 || angle > 315)) {
        turnRight();
      } else {
        driveForward();
      }
    }
  }
  
  stopMotors();
  Serial.println("[NAV] Arrived at Target.");
  currentState = STATE_ACTING;
}

void executeHardwareAction(uint8_t hazard_type) {
  if (hazard_type == 1) { 
    Serial.println("[ACT] Victim Reached. Dropping MedKit.");
    payloadServo.write(0); delay(1500); payloadServo.write(90);
  } else if (hazard_type == 2) { 
    Serial.println("[ACT] Fire Reached. Activating Pump.");
    digitalWrite(PUMP_RELAY_PIN, HIGH); delay(4000); digitalWrite(PUMP_RELAY_PIN, LOW);
  }
}

void driveForward() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  analogWrite(ENA, 160); analogWrite(ENB, 160);
}

void turnRight() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  analogWrite(ENA, 180); analogWrite(ENB, 180);
}

void stopMotors() {
  analogWrite(ENA, 0); analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN3, LOW);
}