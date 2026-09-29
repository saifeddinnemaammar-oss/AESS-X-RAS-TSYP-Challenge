/*
ONA GATEWAY: ESP32 BIDIRECTIONAL RF FIREWALL
--------------------------------------------
Listens to LoRa mesh traffic, performs CRC validation, forwards to Pi.
Receives "TX:<HEX>" strings from Pi and broadcasts them via LoRa.
*/

#include <SPI.h>
#include <LoRa.h>

const int csPin = 5;      
const int resetPin = 14;  
const int irqPin = 26;    

uint16_t calculateCRC16(uint8_t *data, uint8_t len) {
    uint16_t crc = 0xFFFF;
    for (uint8_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) crc = (crc << 1) ^ 0x1021;
            else crc <<= 1;
        }
    }
    return crc;
}

void setup() {
  Serial.begin(115200);
  while (!Serial);

  LoRa.setPins(csPin, resetPin, irqPin);
  if (!LoRa.begin(868E6)) {
    Serial.println("ERR_LORA_INIT_FAILED");
    while (true);
  }
  Serial.println("SYS_ONA_ESP32_ACTIVE");
}

void loop() {
  // 1. Handle Incoming LoRa Packets (Ingress)
  int packetSize = LoRa.parsePacket();
  if (packetSize > 0) {
    uint8_t packet[256];
    int i = 0;
    while (LoRa.available() && i < 256) {
      packet[i++] = LoRa.read();
    }

    // CRC Validation (Assuming last 2 bytes are CRC)
    if (packetSize >= 4) {
      uint16_t receivedCRC = (packet[packetSize - 2] << 8) | packet[packetSize - 1];
      uint16_t calculatedCRC = calculateCRC16(packet, packetSize - 2);

      if (receivedCRC == calculatedCRC) {
        Serial.print("VALID_PKT:");
        for (int j = 0; j < packetSize; j++) {
          if (packet[j] < 16) Serial.print("0");
          Serial.print(packet[j], HEX);
        }
        Serial.println();
      } else {
        Serial.println("WARN_CRC_MISMATCH_DROPPED");
      }
    }
  }

  // 2. Handle Outgoing LoRa Transmissions from Pi (Egress)
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.startsWith("TX:")) {
      String hexStr = cmd.substring(3);
      int len = hexStr.length() / 2;
      
      LoRa.beginPacket();
      for (int i = 0; i < len; i++) {
        String byteStr = hexStr.substring(i * 2, i * 2 + 2);
        LoRa.write((uint8_t) strtol(byteStr.c_str(), NULL, 16));
      }
      LoRa.endPacket();
      Serial.println("ACK_TX_COMPLETE");
    }
  }
}