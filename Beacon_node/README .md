# Deployable Beacon Node

Self-contained RF breadcrumb node dropped by the Writer Robot to establish an ad-hoc local positioning mesh within GPS-denied environments.

## Hardware Stack
* **Microcontroller:** ESP32-WROOM-32 (or ESP32-C3 Mini)
* **RF Transceiver:** Semtech SX1276 (868 MHz)
* **Visual Status:** WS2812B NeoPixel RGB Ring (8 pixels)
* **Audio Failsafe:** Piezoelectric Buzzer
* **Power Source:** 3.7V 18650 Li-ion cell with a 3.3V LDO regulator

## Pinout
| Module Pin | ESP32 GPIO | Function |
| :--- | :--- | :--- |
| **LoRa SCK** | GPIO 18 | SPI Clock |
| **LoRa MISO** | GPIO 19 | SPI Master In Slave Out |
| **LoRa MOSI** | GPIO 23 | SPI Master Out Slave In |
| **LoRa NSS** | GPIO 5 | SPI Chip Select |
| **LoRa RST** | GPIO 14 | Module Reset |
| **LoRa DIO0** | GPIO 26 | Packet RX Interrupt |
| **NeoPixel DIN**| GPIO 4 | RGB LED Single-Wire Control |
| **Buzzer** | GPIO 12 | PWM Audio Failsafe (SOS) |

## Protocol State Machine
1. **Unconfigured (`STATE_UNCONFIGURED`):** LED is dim white. The node listens for a 20-byte configuration packet from the Writer.
2. **Handshake:** Node transmits `ACK` back to the Writer upon receipt.
3. **Active Broadcast (`STATE_ACTIVE_BROADCAST`):** LED switches to the designated hazard color. The node broadcasts the full 20-byte struct using ALOHA randomization (3000ms ± 500ms).
4. **Resolved (`STATE_RESOLVED`):** When the Executor verifies and neutralizes the hazard, it transmits an override packet (`0xFF`). The LED transitions to solid green.
5. **Alarm (`STATE_ALARM`):** If the TTL expires (15 min) and the target is a victim, the node flashes red and sounds a loud SOS Morse code pattern.