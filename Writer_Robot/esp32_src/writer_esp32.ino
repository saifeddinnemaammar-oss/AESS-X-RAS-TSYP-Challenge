#include <SPI.h>
#include <LoRa.h>
#include <ESP32Servo.h>

// --- HARDWARE PINS ---
#define LORA_SS 18
#define LORA_RST 14
#define LORA_DIO0 26
#define SERVO_PIN 12

Servo dropServo;
uint16_t beaconCounter = 1;

// --- 20-BYTE PACKET STRUCTURE ---
// __attribute__((packed)) prevents the compiler from adding padding bytes
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

// Basic CRC16 implementation for data integrity
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
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(868E6)) { // Set to 433E6 if using 433MHz Ra-02 modules
    Serial.println("[ERR] LoRa init failed. Check wiring.");
    while (true);
  }
  Serial.println("[SYS] ESP32 Ready. Awaiting AI triggers.");
}

void loop() {
  if (Serial.available() > 0) {
    String incoming = Serial.readStringUntil('\n');
    
    // Expected format from Pi: "DROP_BEACON,1,85.5"
    if (incoming.startsWith("DROP_BEACON")) {
      Serial.println("[ACTUATOR] Releasing physical beacon...");
      dropServo.write(90);
      delay(1000);
      dropServo.write(0);
      
      // Parse the confidence from the incoming serial string
      int firstComma = incoming.indexOf(',');
      int secondComma = incoming.indexOf(',', firstComma + 1);
      float confidenceFloat = incoming.substring(secondComma + 1).toFloat();
      
      // Map confidence (0-100) to a single uint8_t byte (0-255)
      uint8_t confidenceByte = (uint8_t)((confidenceFloat / 100.0) * 255.0);

      // Construct the 20-byte packet
      BeaconPacket packet;
      packet.beacon_id = beaconCounter;
      packet.writer_id = 1; // ID for this specific Writer Robot
      packet.event_type = 1; // 1 = Victim
      packet.x = 0; // TODO: Replace with real SLAM X coordinate 
      packet.y = 0; // TODO: Replace with real SLAM Y coordinate
      packet.z = 0; 
      packet.timestamp = 0; // TODO: Sync with Pi's RTC timestamp
      packet.ttl = 3600; // 1 hour TTL
      packet.confidence = confidenceByte;
      packet.previous_beacon = beaconCounter - 1;
      
      // Calculate CRC for the first 18 bytes and append it
      packet.crc16 = calculateCRC((uint8_t*)&packet, 18);

      // Broadcast via LoRa
      LoRa.beginPacket();
      LoRa.write((uint8_t*)&packet, sizeof(packet));
      LoRa.endPacket();

      Serial.println("[LoRa] 20-byte beacon packet broadcasted successfully.");
      beaconCounter++;
    }
  }
}