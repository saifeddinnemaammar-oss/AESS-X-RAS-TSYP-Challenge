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
const int BATT_PIN = 34; // Voltage divider for 3S LiPo

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

// --- STATE MACHINE & FMEA GLOBALS ---
enum SystemState { STATE_BOOT, STATE_BRIEFING, STATE_NAVIGATING, STATE_ACTING, STATE_RETURN_TO_BASE, STATE_DONE };
SystemState currentState = STATE_BOOT;

struct HazardTarget {
  uint8_t beacon_id;
  uint8_t hazard_type; 
  bool completed;
};

HazardTarget missionTargets[5];
int targetCount = 0;
int currentTargetIndex = -1;

unsigned long lastLoRaTime = 0;
bool imuHealthy = true; // Placeholder for MPU9250 health status
bool speedReduced = false;

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

void setup() {
  Serial.begin(115200);
  
  Serial2.begin(115200, SERIAL_8N1, LIDAR_RX, LIDAR_TX);
  lidar.begin(Serial2);
  pinMode(LIDAR_PWM, OUTPUT);
  analogWrite(LIDAR_PWM, 255);
  
  payloadServo.attach(SERVO_PIN);
  payloadServo.write(90); 
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  
  LoRa.setPins(csPin, resetPin, irqPin);
  if (!LoRa.begin(868E6)) {
    Serial.println("[ERR] LoRa Radio failed");
    while (true);
  }
  
  Serial.println("[SYS] Executor Ready. Awaiting LoRa Briefing...");
  lastLoRaTime = millis();
  currentState = STATE_BRIEFING;
}

void loop() {
  // FMEA 1: Continuous Battery Monitoring (Abort < 20%)
  // 3S LiPo is 12.6V full, dead at 10.5V
  float voltage = (analogRead(BATT_PIN) / 4095.0) * 3.3 * 5.0; 
  if (voltage > 1.0 && voltage < 10.5 && currentState != STATE_DONE && currentState != STATE_RETURN_TO_BASE) {
    Serial.println("[CRITICAL] Battery < 20%. Aborting mission!");
    currentState = STATE_RETURN_TO_BASE;
  }

  // FMEA 2: LoRa Dead Check (No packets for 45 seconds)
  if (millis() - lastLoRaTime > 45000 && currentState == STATE_NAVIGATING) {
    Serial.println("[CRITICAL] LoRa radio timeout. Comm link lost. Aborting!");
    currentState = STATE_RETURN_TO_BASE;
  }

  // FMEA 3: IMU Degradation Check
  // If IMU I2C fails, we drop the motor speed via PWM
  if (!imuHealthy && !speedReduced) {
    Serial.println("[WARN] IMU failure detected. Reducing speed to 100 PWM.");
    speedReduced = true;
  }

  switch (currentState) {
    case STATE_BRIEFING:
      receiveMissionBriefing();
      break;
    case STATE_NAVIGATING:
      if (selectNextPriorityTarget()) {
        homeToBeacon(missionTargets[currentTargetIndex].beacon_id);
      } else {
        Serial.println("[MISSION] All targets complete.");
        currentState = STATE_RETURN_TO_BASE;
      }
      break;
    case STATE_ACTING:
      executeHardwareAction(missionTargets[currentTargetIndex].hazard_type);
      missionTargets[currentTargetIndex].completed = true;
      currentState = STATE_NAVIGATING;
      break;
    case STATE_RETURN_TO_BASE:
      Serial.println("[SYS] Executing Return-to-ONA Odometry Sequence...");
      analogWrite(LIDAR_PWM, 0); // Save power
      // In production, execute reverse odometry array here
      delay(3000); 
      currentState = STATE_DONE;
      break;
    case STATE_DONE:
      stopMotors();
      break;
  }
}

void receiveMissionBriefing() {
  int packetSize = LoRa.parsePacket();
  if (packetSize == sizeof(BeaconPacket)) {
    lastLoRaTime = millis(); // Reset FMEA LoRa Watchdog
    
    BeaconPacket receivedPacket;
    LoRa.readBytes((uint8_t*)&receivedPacket, sizeof(BeaconPacket));
    
    if (calculateCRC((uint8_t*)&receivedPacket, 18) == receivedPacket.crc16) {
      
      // FMEA 4: TTL Expiration Check
      // Using simulated epoch. If beacon is older than TTL, discard.
      uint32_t current_ts = 1700000000 + (millis() / 1000); 
      if ((current_ts - receivedPacket.timestamp) > receivedPacket.ttl) {
        Serial.println("[WARN] Beacon TTL expired. Ignoring stale intelligence.");
        return; 
      }

      Serial.println("[NET] Valid Mission Briefing Received.");
      missionTargets[targetCount] = {(uint8_t)receivedPacket.beacon_id, receivedPacket.event_type, false};
      targetCount++;
      
      // Priority sorting logic
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
  int lidarTimeouts = 0;

  while (millis() - navStart < 6000) {
    if (IS_OK(lidar.waitPoint())) {
      lidarTimeouts = 0; 
      float distance = lidar.getCurrentPoint().distance;
      float angle = lidar.getCurrentPoint().angle;
      
      if (distance > 0 && distance < 400 && (angle < 45 || angle > 315)) {
        turnRight();
      } else {
        driveForward();
      }
    } else {
      // FMEA 5: LiDAR Degradation Check
      lidarTimeouts++;
      if (lidarTimeouts > 15) {
        Serial.println("[CRITICAL] LiDAR blindness detected! Halting navigation.");
        stopMotors();
        currentState = STATE_RETURN_TO_BASE;
        return;
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
  int speed = speedReduced ? 100 : 160; // FMEA: Reduced speed on IMU failure
  analogWrite(ENA, speed); analogWrite(ENB, speed);
}

void turnRight() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  int speed = speedReduced ? 110 : 180;
  analogWrite(ENA, speed); analogWrite(ENB, speed);
}

void stopMotors() {
  analogWrite(ENA, 0); analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN3, LOW);
}