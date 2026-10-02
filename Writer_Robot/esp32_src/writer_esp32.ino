#include <SPI.h>
#include <LoRa.h>
#include <ESP32Servo.h>

// --- PIN DEFINITIONS ---
const int LORA_CS = 5;
const int LORA_RST = 14;
const int LORA_DIO0 = 26;
const int SERVO_PIN = 18; // Controls the beacon magazine release

Servo dropServo;

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

uint16_t currentBeaconID = 100; // Starting ID for this mission
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
  
  dropServo.attach(SERVO_PIN);
  dropServo.write(0); // Locked position
  
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(868E6)) {
    Serial.println("[ERR] Writer LoRa init failed.");
    while (true);
  }
  
  Serial.println("[SYS] Writer ESP32 Ready. Awaiting commands from Pi Vision AI...");
}

void loop() {
  // Listen for the serial bridge command from the Pi's Python script
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("DROP_BEACON")) {
      // Expected format: DROP_BEACON,<event_type>,<confidence>
      // Example: DROP_BEACON,1,85.5
      int firstComma = command.indexOf(',');
      int secondComma = command.indexOf(',', firstComma + 1);
      
      if (firstComma > 0 && secondComma > 0) {
        uint8_t event_type = command.substring(firstComma + 1, secondComma).toInt();
        float conf_float = command.substring(secondComma + 1).toFloat();
        uint8_t conf_byte = (uint8_t)((conf_float / 100.0) * 255.0); // Map 0-100% to 0-255
        
        deployBeacon(event_type, conf_byte);
      }
    }
  }
}

void deployBeacon(uint8_t eventType, uint8_t confidenceMap) {
  Serial.println("[ACT] Deploying Beacon physically...");
  
  // 1. Actuate the drop mechanism
  dropServo.write(90); 
  delay(500); // Allow gravity to pull the beacon out of the magnetic field
  dropServo.write(0); 
  delay(1000); // Wait for the beacon's ESP32 to boot via the MOSFET wake-up circuit

  // 2. Construct the 20-byte payload
  BeaconPacket packet;
  packet.beacon_id = currentBeaconID;
  packet.writer_id = WRITER_ID;
  packet.event_type = eventType;
  
  // Simulated Odometry (In production, pull from ROS2 serial bridge)
  packet.x_cm = 1500; 
  packet.y_cm = 3200; 
  packet.z_dm = 0;
  
  packet.timestamp = 1700000000 + (millis() / 1000); 
  packet.ttl_sec = 3600; // 1 hour validity
  packet.confidence = confidenceMap;
  packet.previous_beacon = previousBeaconID;
  
  // 3. Calculate CRC over the first 18 bytes
  packet.crc16 = calculateCRC((uint8_t*)&packet, 18);

  // 4. Transmit configuration to the newly dropped beacon
  Serial.println("[TX] Broadcasting configuration to dropped beacon...");
  LoRa.beginPacket();
  LoRa.write((uint8_t*)&packet, sizeof(BeaconPacket));
  LoRa.endPacket();
  
  // 5. Update chain pointers
  previousBeaconID = currentBeaconID;
  currentBeaconID++;
}