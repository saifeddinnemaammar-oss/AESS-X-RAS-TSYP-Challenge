#include <SPI.h>
#include <LoRa.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <Adafruit_MLX90640.h>

// --- PIN DEFINITIONS ---
const int LORA_CS = 5;
const int LORA_RST = 14;
const int LORA_DIO0 = 26;
const int SERVO_PIN = 18; // Controls the beacon magazine release
const int MQ_GAS_PIN = 34; // Analog pin for MQ2/MQ7 gas sensor

Servo dropServo;
Adafruit_MLX90640 mlx;
float frame[32*24]; // 768 pixels for thermal array

// --- SENSOR THRESHOLDS ---
const float THERMAL_FIRE = 80.0;
const float THERMAL_VICTIM = 32.0;
const int GAS_HAZARD_THRESHOLD = 2000; // Calibrate to specific analog voltage

unsigned long lastSensorPoll = 0;
const unsigned long POLL_INTERVAL = 1000; // Poll sensors every 1 second

// --- 20-BYTE PACKET STRUCTURE ---
struct __attribute__((packed)) BeaconPacket {
  uint16_t beacon_id;
  uint8_t  writer_id;
  uint8_t  event_type; 
  int16_t  x_cm;
  int16_t  y_cm;
  int8_t   z_dm;
  uint32_t timestamp;
  uint16_t ttl_sec;
  uint8_t  confidence;
  uint16_t previous_beacon;
  uint16_t crc16;
};

uint16_t currentBeaconID = 100;
uint16_t previousBeaconID = 0;
const uint8_t WRITER_ID = 1;

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
  
  // Initialize Servo
  dropServo.attach(SERVO_PIN);
  dropServo.write(0); // Locked position
  
  // Initialize LoRa
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(868E6)) {
    Serial.println("[ERR] Writer LoRa init failed.");
    while (true);
  }
  
  // Initialize Thermal Camera (I2C Pins 21/22)
  Wire.begin(21, 22); 
  if (!mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire)) {
    Serial.println("[ERR] Thermal camera not found. Check wiring.");
    while (1) delay(10);
  }
  mlx.setMode(MLX90640_CHESS);
  mlx.setResolution(MLX90640_ADC_18BIT);
  mlx.setRefreshRate(MLX90640_4_HZ);
  
  pinMode(MQ_GAS_PIN, INPUT);
  
  Serial.println("[SYS] Writer ESP32 Ready. Sensor Polling Active.");
}

void loop() {
  // 1. NON-BLOCKING SENSOR FUSION POLLING
  if (millis() - lastSensorPoll > POLL_INTERVAL) {
    lastSensorPoll = millis();
    
    // Check Gas
    int gasLevel = analogRead(MQ_GAS_PIN);
    if (gasLevel > GAS_HAZARD_THRESHOLD) {
      Serial.println("GAS_DETECTED"); // Send trigger to Pi
    }
    
    // Check Thermal
    if (mlx.getFrame(frame) == 0) {
      float max_temp = -100.0;
      for (uint16_t h = 0; h < 768; h++) {
        if (frame[h] > max_temp) max_temp = frame[h];
      }
      
      if (max_temp > THERMAL_FIRE) {
        Serial.println("THERMAL_SPIKE_FIRE");
      } else if (max_temp > THERMAL_VICTIM && max_temp < 45.0) {
        Serial.println("THERMAL_SPIKE"); // Send trigger to Pi to wake YOLOv8
      }
    }
  }

  // 2. LISTEN FOR DEPLOYMENT COMMANDS FROM RASPBERRY PI
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("DROP_BEACON")) {
      // Expected format: DROP_BEACON,<event_type>,<confidence>
      int firstComma = command.indexOf(',');
      int secondComma = command.indexOf(',', firstComma + 1);
      
      if (firstComma > 0 && secondComma > 0) {
        uint8_t event_type = command.substring(firstComma + 1, secondComma).toInt();
        float conf_float = command.substring(secondComma + 1).toFloat();
        uint8_t conf_byte = (uint8_t)((conf_float / 100.0) * 255.0); 
        
        deployBeacon(event_type, conf_byte);
      }
    }
  }
}

void deployBeacon(uint8_t eventType, uint8_t confidenceMap) {
  Serial.println("[ACT] Deploying Beacon physically...");
  
  dropServo.write(90); 
  delay(500); 
  dropServo.write(0); 
  delay(1000); 

  BeaconPacket packet;
  packet.beacon_id = currentBeaconID;
  packet.writer_id = WRITER_ID;
  packet.event_type = eventType;
  
  // Simulated Odometry
  packet.x_cm = 1500; 
  packet.y_cm = 3200; 
  packet.z_dm = 0;
  
  packet.timestamp = 1700000000 + (millis() / 1000); 
  packet.ttl_sec = 3600; 
  packet.confidence = confidenceMap;
  packet.previous_beacon = previousBeaconID;
  
  packet.crc16 = calculateCRC((uint8_t*)&packet, 18);

  Serial.println("[TX] Broadcasting configuration to dropped beacon...");
  LoRa.beginPacket();
  LoRa.write((uint8_t*)&packet, sizeof(BeaconPacket));
  LoRa.endPacket();
  
  previousBeaconID = currentBeaconID;
  currentBeaconID++;
}