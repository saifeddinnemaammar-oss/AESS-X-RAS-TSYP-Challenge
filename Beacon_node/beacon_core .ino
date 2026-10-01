#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_NeoPixel.h>

// --- PIN DEFINITIONS ---
const int LORA_CS    = 5;
const int LORA_RST   = 14;
const int LORA_DIO0  = 26;

const int LED_PIN    = 4;
const int NUM_PIXELS = 8; 

Adafruit_NeoPixel strip(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

// --- BEACON STATE ---
enum BeaconState {
  STATE_UNCONFIGURED,
  STATE_ACTIVE_BROADCAST,
  STATE_RESOLVED
};

BeaconState currentState = STATE_UNCONFIGURED;

// Strict 20-byte Little-Endian Struct (Matches System Architecture)
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

BeaconPacket activePayload;
unsigned long lastPingTime = 0;
const unsigned long PING_INTERVAL = 1500; 

// --- HELPER FUNCTIONS ---
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

void setIndicatorColor(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < NUM_PIXELS; i++) {
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.show();
}

void applyEventColor(uint8_t event_type) {
  switch (event_type) {
    case 0: setIndicatorColor(245, 158, 11); break; // Anchor: Amber
    case 1: setIndicatorColor(6, 182, 212); break;  // Victim: Cyan
    case 2: setIndicatorColor(239, 68, 68); break;  // Fire: Red
    case 3: setIndicatorColor(168, 85, 247); break; // Gas: Purple
    default: setIndicatorColor(255, 255, 255); break;
  }
}

void handleIncomingPacket(int packetSize) {
  // Case 1: Initial configuration from Writer
  if (currentState == STATE_UNCONFIGURED && packetSize == sizeof(BeaconPacket)) {
    BeaconPacket tempPacket;
    LoRa.readBytes((uint8_t*)&tempPacket, sizeof(BeaconPacket));
    
    // Verify CRC-16
    if (calculateCRC((uint8_t*)&tempPacket, 18) == tempPacket.crc16) {
      activePayload = tempPacket;
      
      Serial.print("[BEACON] Configured! Assigned ID: ");
      Serial.println(activePayload.beacon_id);

      // Transmit ACK back to Writer
      LoRa.beginPacket();
      LoRa.print("ACK");
      LoRa.write(activePayload.beacon_id & 0xFF);
      LoRa.endPacket();

      applyEventColor(activePayload.event_type);
      currentState = STATE_ACTIVE_BROADCAST;
      lastPingTime = millis();
    } else {
      Serial.println("[ERR] CRC-16 mismatch. Packet dropped.");
    }
  }
  // Case 2: Status Resolution from Executor
  else if (currentState == STATE_ACTIVE_BROADCAST && packetSize >= 4) {
    uint8_t header = LoRa.read();
    if (header == 0xFF) {
      uint16_t targetID = (LoRa.read() << 8) | LoRa.read();
      uint8_t newStatus = LoRa.read();

      if (targetID == activePayload.beacon_id && newStatus == 0) {
        Serial.println("[BEACON] Hazard resolved by Executor.");
        currentState = STATE_RESOLVED;
        setIndicatorColor(16, 185, 129); // Turn Green
      }
    }
  }
}

void setup() {
  Serial.begin(115200);

  strip.begin();
  strip.setBrightness(80);
  setIndicatorColor(20, 20, 20); // Dim white: Booting / Unconfigured

  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(868E6)) {
    Serial.println("[ERR] LoRa init failed.");
    setIndicatorColor(255, 0, 0); 
    while (true);
  }

  Serial.println("[BEACON] Booted. Waiting for Writer configuration packet...");
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize > 0) {
    handleIncomingPacket(packetSize);
  }

  // Periodic Broadcasting
  if (currentState == STATE_ACTIVE_BROADCAST) {
    if (millis() - lastPingTime >= PING_INTERVAL) {
      LoRa.beginPacket();
      LoRa.write((uint8_t*)&activePayload, sizeof(BeaconPacket));
      LoRa.endPacket();
      
      Serial.println("[TX] Beacon pulsing...");
      lastPingTime = millis();
    }
  }
}