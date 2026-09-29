/*
THE LIVING MAP: DEPLOYABLE BEACON NODE (ESP32)
-----------------------------------------------
Description: Standalone mesh breadcrumb node dropped by the Writer Robot.
Listens for Writer configuration, drives NeoPixel status indicators,
and broadcasts periodic LoRa pings for Executor RSSI homing.
Dependencies: LoRa by Sandeep Mistry, Adafruit NeoPixel
*/

#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_NeoPixel.h>

// --- PIN DEFINITIONS ---
// LoRa SPI (Standard ESP32 wiring)
const int LORA_CS    = 5;
const int LORA_RST   = 14;
const int LORA_DIO0  = 26;

// NeoPixel LED
const int LED_PIN    = 4;
const int NUM_PIXELS = 8; // Adjust to match your hardware (e.g., 8-LED ring or 1 discrete pixel)

Adafruit_NeoPixel strip(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

// --- BEACON STATE ---
enum BeaconState {
  STATE_UNCONFIGURED,
  STATE_ACTIVE_BROADCAST,
  STATE_RESOLVED
};

BeaconState currentState = STATE_UNCONFIGURED;

// Configuration Storage (matches Writer packet payload)
struct BeaconConfig {
  uint16_t beacon_id;
  uint8_t  writer_id;
  uint8_t  event_type; // 0=Anchor, 1=Victim, 2=Fire, 3=Gas
  int16_t  x_cm;
  int16_t  y_cm;
  int16_t  z_cm;
  uint16_t ttl_sec;
  uint8_t  confidence;
  uint16_t next_id;
} config;

unsigned long lastPingTime = 0;
const unsigned long PING_INTERVAL = 1500; // Broadcast every 1.5 seconds

// Helper to set all pixels to a single color
void setIndicatorColor(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < NUM_PIXELS; i++) {
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.show();
}

void applyEventColor(uint8_t event_type) {
  switch (event_type) {
    case 0: // Anchor / Checkpoint -> Amber
      setIndicatorColor(245, 158, 11);
      break;
    case 1: // Victim -> Cyan
      setIndicatorColor(6, 182, 212);
      break;
    case 2: // Fire -> Red
      setIndicatorColor(239, 68, 68);
      break;
    case 3: // Gas -> Purple
      setIndicatorColor(168, 85, 247);
      break;
    default:
      setIndicatorColor(255, 255, 255);
      break;
  }
}

void setup() {
  Serial.begin(115200);

  // Initialize NeoPixel
  strip.begin();
  strip.setBrightness(80);
  setIndicatorColor(20, 20, 20); // Dim white: Booting / Unconfigured

  // Initialize LoRa
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(868E6)) {
    Serial.println("[ERR] LoRa init failed.");
    setIndicatorColor(255, 0, 0); // Solid Red warning
    while (true);
  }

  Serial.println("[BEACON] Booted. Waiting for Writer configuration packet...");
}

void loop() {
  void handleIncomingPacket(int packetSize) {
  uint8_t buffer[64];
  int len = 0;
  while (LoRa.available() && len < 64) {
    buffer[len++] = LoRa.read();
  }

  // Case 1: Configuration from Writer (Strict 20-byte check)
  // [ID:2][WriterID:1][Type:1][X:2][Y:2][Z:2][TS:4][TTL:2][Conf:1][NextID:1][CRC:2]
  if (currentState == STATE_UNCONFIGURED && len == 20) {
    uint16_t receivedCRC = (buffer[18] << 8) | buffer[19];
    uint16_t calculatedCRC = calculateCRC16(buffer, 18);
    
    if (receivedCRC != calculatedCRC) {
        Serial.println("[ERR] CRC-16 mismatch. Packet dropped.");
        return;
    }

    config.beacon_id  = (buffer[0] << 8) | buffer[1];
    config.writer_id  = buffer[2];
    config.event_type = buffer[3];
    config.x_cm       = (int16_t)((buffer[4] << 8) | buffer[5]);
    config.y_cm       = (int16_t)((buffer[6] << 8) | buffer[7]);
    config.z_cm       = (int16_t)((buffer[8] << 8) | buffer[9]);
    config.timestamp  = (buffer[10] << 24) | (buffer[11] << 16) | (buffer[12] << 8) | buffer[13];
    config.ttl_sec    = (buffer[14] << 8) | buffer[15];
    config.confidence = buffer[16];
    config.next_id    = buffer[17];

    Serial.print("[BEACON] Configured! Assigned ID: ");
    Serial.println(config.beacon_id);

    LoRa.beginPacket();
    LoRa.print("ACK");
    LoRa.write(config.beacon_id & 0xFF);
    LoRa.endPacket();

    applyEventColor(config.event_type);
    currentState = STATE_ACTIVE_BROADCAST;
    lastPingTime = millis();
  }

  // Case 2: Status Resolution from Executor
  // Structure: [0xFF][TargetBeaconID:2][NewStatus:1]
  else if (len >= 4 && buffer[0] == 0xFF) {
    uint16_t targetID = (buffer[1] << 8) | buffer[2];
    uint8_t newStatus = buffer[3]; // 0 = Neutralized / Rescued

    if (targetID == config.beacon_id && newStatus == 0) {
      Serial.println("[BEACON] Hazard resolved by Executor.");
      currentState = STATE_RESOLVED;
      setIndicatorColor(16, 185, 129); // Turn Green
    }
  }
}